"""Private review and bounded checkpoint routes; transport delegates to domain modules."""

from collections.abc import Awaitable, Callable
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field

from .contracts import LessonSpec
from .domain import Domain, User
from .learning_reviews import LearningReviews, ReviewSubmission, review_state
from .path_publication import PathPublication, PathSubmission
from .settings import Settings
from .store import Database, Store
from .teaching_svg import teaching_svg


class LearningEvent(BaseModel):
    """Opt-in coarse interactions only; no choice, answer or free-form text."""

    model_config = ConfigDict(extra="forbid")
    consent: Literal[True]
    kind: Literal[
        "prediction_skipped", "prediction_attempted", "change_replayed", "transfer_revealed", "confusing_beat"
    ]
    beat: str = Field(pattern=r"^[a-z][a-z0-9-]{0,39}$")


class DepthDraftBody(BaseModel):
    """An explicit owner operation admits one independently reviewed follow-up."""

    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=8, max_length=180)
    role: Literal["insight", "model"]
    operation: str = Field(pattern=r"^[a-zA-Z0-9-]{8,80}$")


def register_teaching_routes(app: FastAPI, store: Store, member: Callable[..., User],
                             settings: Settings, dispatch: Callable[[str, str], Awaitable[None]]) -> None:
    """Attach authenticated teaching endpoints without a duplicate auth system."""
    reviews = LearningReviews(store)
    paths = PathPublication(store)

    @app.post("/api/v1/owner/lessons/{root_id}/depth-drafts")
    async def depth_draft(root_id: str, body: DepthDraftBody,
                          user: Annotated[User, Depends(member)]) -> dict[str, object]:
        if not user.owner:
            raise HTTPException(403, "Owner access is required")
        domain = Domain(store, settings)
        result = domain.request(body.question, user, node_parent=root_id, node_role=body.role,
                                operation=body.operation)
        if result["kind"] == "job":
            job = domain.job(str(result["job_id"]))
            await dispatch(str(job["id"]), str(job["phase"]))
        return result

    @app.get("/api/v1/owner/lessons/{lesson_id}/learning-paths")
    def path_history(lesson_id: str, user: Annotated[User, Depends(member)]) -> dict[str, object]:
        return paths.history(lesson_id, user)

    @app.post("/api/v1/owner/lessons/{lesson_id}/learning-paths")
    def compose_path(lesson_id: str, body: PathSubmission, user: Annotated[User, Depends(member)]) -> dict[str, object]:
        return paths.attach(lesson_id, body, user)

    @app.get("/api/v1/learning-paths/{lesson_id}")
    def path_bundle(lesson_id: str, user: Annotated[User, Depends(member)]) -> dict[str, object]:
        from .learning_bundle import learning_bundle
        return store.transaction(lambda db: learning_bundle(db, lesson_id, user), write=False)

    @app.get("/api/v1/lessons/{lesson_id}/checkpoint")
    def checkpoint(
        lesson_id: str,
        user: Annotated[User, Depends(member)],
        seconds: Annotated[float, Query(ge=0, le=180, allow_inf_nan=False)] = 0,
        scenario: Annotated[str | None, Query(max_length=40)] = None,
    ) -> Response:
        record = store.snapshot().lessons.get(lesson_id)
        if not record:
            raise HTTPException(404, "Lesson not found")
        spec = LessonSpec.model_validate(record["spec"])
        if spec.version != 2:
            raise HTTPException(422, "Checkpoints require a CE lesson revision")
        try:
            svg = teaching_svg(spec, seconds, scenario)
        except ValueError as exc:
            raise HTTPException(422, "Unknown checkpoint or unavailable scenario") from exc
        return Response(
            svg,
            media_type="image/svg+xml",
            headers={
                "Cache-Control": "private, no-store",
                "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; sandbox",
            },
        )

    @app.get("/api/v1/owner/lessons/{lesson_id}/reviews")
    def read_reviews(lesson_id: str, user: Annotated[User, Depends(member)]) -> dict[str, object]:
        if not user.owner:
            raise HTTPException(403, "Owner access is required")
        return review_state(store.snapshot(), lesson_id)

    @app.post("/api/v1/owner/lessons/{lesson_id}/reviews")
    def record_review(
        lesson_id: str, body: ReviewSubmission, user: Annotated[User, Depends(member)]
    ) -> dict[str, object]:
        return reviews.record(lesson_id, body, user)

    @app.post("/api/v1/lessons/{lesson_id}/learning-event")
    def event(lesson_id: str, body: LearningEvent, user: Annotated[User, Depends(member)]) -> dict[str, bool]:
        def write(db: Database) -> None:
            record = db.lessons.get(lesson_id)
            if not record:
                raise HTTPException(404, "Lesson not found")
            spec = LessonSpec.model_validate(record["spec"])
            if not spec.teaching or body.beat not in {b.id for b in spec.teaching.beats}:
                raise HTTPException(422, "Unknown teaching beat")
            recent = sum(
                e.get("user_id") == user.id and str(e.get("kind", "")).startswith("learning_")
                for e in db.events
            )
            if recent >= 300:
                raise HTTPException(429, "Learning-event limit reached; the lesson still works")
            Domain.event(
                db, "learning_" + body.kind, user, lesson_id=lesson_id, beat=body.beat, spec_version="ce-1"
            )

        store.transaction(write)
        return {"ok": True}
