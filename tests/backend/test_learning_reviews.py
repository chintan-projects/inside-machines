"""Human evidence cannot be fabricated by a model check, a thumb or a stale revision."""

from typing import cast

import httpx
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from backend.app import create_app
from backend.contracts import LessonSpec
from backend.domain import User
from backend.learning_reviews import LearningReviews, ReviewSubmission, review_state
from backend.settings import Settings
from backend.starters import digest_spec
from backend.store import Store


def submission(spec: LessonSpec, **updates: object) -> ReviewSubmission:
    """Explicit synthetic human assertions only enter an isolated test database."""
    return ReviewSubmission.model_validate(
        {
            "spec_sha256": digest_spec(spec),
            "video_sha256": "0" * 64,
            "gate": "engineering",
            "reviewer": "Synthetic test reviewer",
            "method": "agent",
            "decision": "pass",
            "evidence": "Synthetic fixture evidence; not an actual learner or technical review.",
            **updates,
        }
    )


def test_review_rejects_nonhuman_missing_device_and_prior_knowledge(ce_spec: LessonSpec) -> None:
    """All human gates require their own kind of evidence rather than an aggregate score."""
    for fields in (
        {"gate": "technical"},
        {"gate": "technical", "method": "human"},
        {"gate": "craft", "method": "human", "real_device": False},
        {"gate": "learning", "method": "human", "scores": []},
        {
            "gate": "learning",
            "method": "human",
            "scores": [
                {"participant": f"anon-{i}", "baseline": 2, "causal": 2, "transfer": 2} for i in range(5)
            ],
        },
    ):
        with pytest.raises(ValidationError):
            submission(ce_spec, **fields)
    with pytest.raises(ValidationError):
        submission(ce_spec, scores=[{"participant": "anon-a", "baseline": 0, "causal": 2, "transfer": 2}])


def test_review_binding_release_order_and_later_rejection(
    store: Store, ce_spec: LessonSpec, user: User
) -> None:
    """A release binds both hashes, requires every gate and is invalidated by new findings."""
    id = ce_spec.canonical
    store.transaction(
        lambda db: db.lessons.update(
            {id: {"id": id, "spec": ce_spec.model_dump(mode="json"), "video_sha256": "0" * 64}}
        )
    )
    reviews = LearningReviews(store)
    owner = User(id="synthetic-owner", name="Synthetic owner", owner=True)
    with pytest.raises(HTTPException):
        reviews.record(id, submission(ce_spec), user)
    with pytest.raises(HTTPException):
        reviews.record(id, submission(ce_spec, video_sha256="1" * 64), owner)
    with pytest.raises(HTTPException):
        reviews.record(id, submission(ce_spec, gate="release", method="human"), owner)
    assert not reviews.record(id, submission(ce_spec), owner)["ready"]
    reviews.record(id, submission(ce_spec, gate="technical", method="human", independent=True), owner)
    reviews.record(
        id,
        submission(
            ce_spec,
            gate="craft",
            method="human",
            real_device=True,
            device="Synthetic physical phone evidence",
        ),
        owner,
    )
    scores = [{"participant": f"anon-{i}", "baseline": 0, "causal": 2, "transfer": 2} for i in range(5)]
    assert reviews.record(id, submission(ce_spec, gate="learning", method="human", scores=scores), owner)[
        "can_release"
    ]
    assert reviews.record(id, submission(ce_spec, gate="release", method="human"), owner)["ready"]
    reviews.record(id, submission(ce_spec, gate="technical", method="human", decision="needs-work"), owner)
    state = review_state(store.snapshot(), id)
    assert not state["ready"] and not cast(dict[str, bool], state["gates"])["release"]
    assert store.snapshot().lessons[id]["spec"] == ce_spec.model_dump(mode="json")


async def test_checkpoint_review_and_opt_in_event_boundaries(settings: Settings, ce_spec: LessonSpec) -> None:
    """Member/owner isolation, invalid actions, consent and no free-text analytics."""
    app = create_app(settings)
    store = cast(Store, app.state.store)
    id = ce_spec.canonical
    store.transaction(
        lambda db: db.lessons.update(
            {id: {"id": id, "spec": ce_spec.model_dump(mode="json"), "video_sha256": "0" * 64}}
        )
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get(f"/api/v1/lessons/{id}/checkpoint")).status_code == 401
        await client.post(
            "/api/v1/auth/login", json={"name": "Synthetic member", "code": settings.invite_code}
        )
        assert (await client.get(f"/api/v1/owner/lessons/{id}/reviews")).status_code == 403
        svg = await client.get(f"/api/v1/lessons/{id}/checkpoint?seconds=3")
        assert svg.status_code == 200 and "image/svg+xml" in svg.headers["content-type"]
        assert "data-graphic=" in svg.text and "sandbox" in svg.headers["content-security-policy"]
        for suffix in ("?seconds=nan", "?seconds=181", "?scenario=unknown"):
            assert (await client.get(f"/api/v1/lessons/{id}/checkpoint{suffix}")).status_code == 422
        assert ce_spec.teaching is not None
        body = {"kind": "prediction_skipped", "beat": ce_spec.teaching.beats[0].id}
        assert (await client.post(f"/api/v1/lessons/{id}/learning-event", json=body)).status_code == 422
        assert (
            await client.post(
                f"/api/v1/lessons/{id}/learning-event",
                json={**body, "consent": True, "answer": "private answer"},
            )
        ).status_code == 422
        assert (
            await client.post(f"/api/v1/lessons/{id}/learning-event", json={**body, "consent": True})
        ).status_code == 200
        assert "private answer" not in str(store.snapshot().events)
        await client.post("/api/v1/auth/logout")
        await client.post("/api/v1/auth/login", json={"name": "Synthetic owner", "code": settings.owner_code})
        assert (await client.get(f"/api/v1/owner/lessons/{id}/reviews")).status_code == 200
        recorded = await client.post(
            f"/api/v1/owner/lessons/{id}/reviews", json=submission(ce_spec).model_dump(mode="json")
        )
        assert recorded.status_code == 200 and not recorded.json()["ready"]
