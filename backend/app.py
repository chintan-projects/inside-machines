"""Versioned family-alpha API shared by the web, PWA, and future native clients."""

import json
import re
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Annotated, Literal
from urllib.parse import urlparse

from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from vercel.headers import set_headers

from .assets import Assets
from .auth import COOKIE, Auth
from .chat import Chats, Conversation
from .contracts import LessonSpec
from .domain import Domain, User
from .learning_reviews import review_state
from .pipeline import Enqueue
from .provider import configure_gateway
from .quality import learning_issues
from .settings import Settings, load_settings
from .store import Database, Store
from .teaching_routes import register_teaching_routes


class LoginBody(BaseModel):
    """An invite is exchanged for a cookie, never retained in the browser."""

    name: str = Field(min_length=1, max_length=60)
    code: str = Field(min_length=1, max_length=180)


class RequestBody(BaseModel):
    """Explicit scope prevents silently treating a specific appliance as generic."""

    question: str = Field(min_length=3, max_length=180)
    scope: Literal["general", "specific"] = "general"
    model: str = Field(default="", max_length=120)


class FeedbackBody(BaseModel):
    """Feedback is a member's assessment, not factual verification."""

    value: Literal["up", "down"]
    reason: str = Field(default="", max_length=600)
    stage: int | None = Field(default=None, ge=0, le=6)


class ChatBody(BaseModel):
    """Create a private conversation for a published lesson."""

    lesson_id: str = Field(min_length=1, max_length=80)


class MessageBody(BaseModel):
    """Client-generated idempotency key prevents duplicate paid replies."""

    question: str = Field(min_length=3, max_length=700)
    operation: str = Field(pattern=r"^[a-zA-Z0-9-]{8,80}$")


class RevisionBody(BaseModel):
    """An explicit owner action admits a new paid draft without changing the old one."""

    operation: str = Field(pattern=r"^[a-zA-Z0-9-]{8,80}$")


def video_response(data: bytes, range_header: str | None) -> Response:
    """Support mobile video seeking while keeping private storage URLs private."""
    headers = {"Accept-Ranges": "bytes", "Cache-Control": "private, no-store"}
    if not range_header:
        return Response(data, media_type="video/mp4", headers=headers)
    match = re.fullmatch(r"bytes=(\d*)-(\d*)", range_header)
    if not match or not any(match.groups()):
        return Response(status_code=416, headers={**headers, "Content-Range": f"bytes */{len(data)}"})
    left, right = match.groups()
    start = int(left) if left else max(0, len(data) - int(right))
    end = min(len(data) - 1, int(right)) if left and right else len(data) - 1
    if start > end or start >= len(data):
        return Response(status_code=416, headers={**headers, "Content-Range": f"bytes */{len(data)}"})
    return Response(
        data[start : end + 1],
        status_code=206,
        media_type="video/mp4",
        headers={**headers, "Content-Range": f"bytes {start}-{end}/{len(data)}"},
    )


def create_app(settings: Settings | None = None, *, enqueue: Enqueue | None = None) -> FastAPI:
    """Create an isolated application; production requires durable storage and auth."""
    config = settings or load_settings()
    if config.production and not all(
        (config.database_url, config.blob_token, config.session_secret, config.invite_code, config.owner_code)
    ):
        raise RuntimeError(
            "Production requires durable database, private assets, and family/owner session configuration"
        )
    store = Store(config.database_url, config.data_dir)
    auth, domain, chats, assets = (
        Auth(store, config),
        Domain(store, config),
        Chats(store, config),
        Assets(config),
    )
    configure_gateway(config)
    app = FastAPI(title="Inside Machines", version="1.0.0", docs_url=None, redoc_url=None)
    app.state.store, app.state.auth, app.state.domain, app.state.chats = store, auth, domain, chats

    async def dispatch(job_id: str, phase: str) -> None:
        if enqueue is not None:
            await enqueue(job_id, phase)
        else:
            from .tasks import enqueue_job

            await enqueue_job(job_id, phase)

    @app.middleware("http")
    async def boundary(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        set_headers(dict(request.headers))
        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            origin = request.headers.get("origin")
            if origin and urlparse(origin).netloc != request.headers.get("host"):
                return JSONResponse({"detail": "Requests must come from this app."}, status_code=403)
            if request.url.path.startswith("/api/"):
                body = await request.body()
                if len(body) > 32768:
                    return JSONResponse({"detail": "Request is too large."}, status_code=413)
        response = await call_next(request)
        response.headers["Cache-Control"] = (
            "private, no-store" if request.url.path.startswith("/api/") else "no-cache"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    def member(token: Annotated[str | None, Cookie(alias=COOKIE)] = None) -> User:
        return auth.user(token)

    Member = Annotated[User, Depends(member)]

    @app.get("/api/v1/health")
    def health() -> dict[str, object]:
        return {"ok": True, "version": 1, "generation_enabled": config.generation_enabled}

    @app.post("/api/v1/auth/login")
    def login(body: LoginBody, request: Request, response: Response) -> User:
        address = request.headers.get("x-real-ip", "") if config.production else ""
        address = address or (request.client.host if request.client else "unknown")
        user, token = auth.login(body.name, body.code, address)
        response.set_cookie(
            COOKIE,
            token,
            max_age=config.session_days * 86400,
            secure=config.production,
            httponly=True,
            samesite="strict",
            path="/",
        )
        return user

    @app.get("/api/v1/auth/me")
    def me(user: Member) -> User:
        return user

    @app.post("/api/v1/auth/logout")
    def logout(
        response: Response, token: Annotated[str | None, Cookie(alias=COOKIE)] = None
    ) -> dict[str, bool]:
        auth.logout(token)
        response.delete_cookie(COOKIE, path="/")
        return {"ok": True}

    @app.get("/api/v1/lessons")
    def catalog(user: Member) -> list[dict[str, object]]:
        return domain.catalog()

    @app.get("/api/v1/lessons/{lesson_id}")
    def lesson(lesson_id: str, user: Member) -> dict[str, object]:
        def read(db: Database) -> dict[str, object]:
            record = db.lessons.get(lesson_id)
            if not record:
                raise HTTPException(404, "Explanation not found")
            record["views"] = int(str(record.get("views", 0))) + 1
            domain.event(db, "lesson_opened", user, lesson_id=lesson_id)
            return {
                "id": lesson_id,
                "spec": record["spec"],
                "quality": record.get("quality", "generated"),
                "superseded_by": record.get("superseded_by"),
                "review_needed": bool(learning_issues(LessonSpec.model_validate(record["spec"])))
                or not review_state(db, lesson_id)["ready"],
                "video_ready": bool(record.get("video")),
                "feedback": db.feedback.get(f"{user.id}:{lesson_id}"),
            }

        return store.transaction(read)

    @app.post("/api/v1/requests")
    async def request_lesson(body: RequestBody, user: Member) -> dict[str, object]:
        if body.scope == "specific":
            # Model-specific evidence is private and not a generic cache identity.
            return {
                "kind": "specific",
                "message": "This alpha explains general mechanisms. Tell us the machine type to explore a clearly labelled general lesson. Model-specific manuals and photos are planned; we won't invent details for your appliance.",
                "model": body.model,
            }
        result = domain.request(body.question, user)
        if result["kind"] == "job":
            job = domain.job(str(result["job_id"]))
            await dispatch(str(job["id"]), str(job["phase"]))
        return result

    @app.get("/api/v1/jobs/{job_id}")
    def job(job_id: str, user: Member) -> dict[str, object]:
        return domain.job(job_id)

    @app.post("/api/v1/owner/lessons/{lesson_id}/revise")
    async def revise(lesson_id: str, body: RevisionBody, user: Member) -> dict[str, object]:
        if not user.owner:
            raise HTTPException(403, "Owner access is required")
        parent = store.snapshot().lessons.get(lesson_id)
        if not parent:
            raise HTTPException(404, "Lesson not found")
        spec = LessonSpec.model_validate(parent["spec"])
        result = domain.request(spec.question, user, revision_of=lesson_id, operation=body.operation)
        if result["kind"] == "job":
            current = domain.job(str(result["job_id"]))
            await dispatch(str(current["id"]), str(current["phase"]))
        return result

    @app.get("/api/v1/jobs/{job_id}/events")
    async def progress(job_id: str, request: Request, user: Member) -> StreamingResponse:
        domain.job(job_id)

        async def events() -> AsyncIterator[str]:
            import asyncio

            previous = ""
            for _ in range(110):
                if await request.is_disconnected():
                    return
                current = domain.job(job_id)
                payload = json.dumps(current)
                if payload != previous:
                    yield f"event: progress\ndata: {payload}\n\n"
                    previous = payload
                else:
                    yield ": keepalive\n\n"
                if current["status"] in ("failed", "complete"):
                    return
                await asyncio.sleep(2)

        return StreamingResponse(events(), media_type="text/event-stream")

    @app.post("/api/v1/lessons/{lesson_id}/feedback")
    def feedback(lesson_id: str, body: FeedbackBody, user: Member) -> dict[str, bool]:
        domain.feedback(lesson_id, body.value, body.reason, user, stage=body.stage)
        return {"ok": True}

    @app.get("/api/v1/lessons/{lesson_id}/video")
    async def video(lesson_id: str, request: Request, user: Member) -> Response:
        record = store.snapshot().lessons.get(lesson_id)
        if not record or not record.get("video"):
            raise HTTPException(404, "Narrated video isn't available yet")
        data = await assets.read(str(record["video"]))
        return video_response(data, request.headers.get("range"))

    @app.get("/api/v1/lessons/{lesson_id}/captions")
    def captions(lesson_id: str, user: Member) -> Response:
        record = store.snapshot().lessons.get(lesson_id)
        if not record:
            raise HTTPException(404, "Explanation not found")
        spec = LessonSpec.model_validate(record["spec"])

        def timestamp(seconds: float) -> str:
            milliseconds = round(seconds * 1000)
            return f"{milliseconds // 3600000:02}:{milliseconds // 60000 % 60:02}:{milliseconds // 1000 % 60:02}.{milliseconds % 1000:03}"

        lines, elapsed = ["WEBVTT", ""], 0.0
        for stage in spec.stages:
            lines.extend(
                [f"{timestamp(elapsed)} --> {timestamp(elapsed + stage.duration)}", stage.narration, ""]
            )
            elapsed += stage.duration
        return Response("\n".join(lines), media_type="text/vtt")

    @app.post("/api/v1/chats")
    def create_chat(body: ChatBody, user: Member) -> Conversation:
        return chats.create(body.lesson_id, user)

    @app.get("/api/v1/chats/{chat_id}")
    def chat(chat_id: str, user: Member) -> Conversation:
        return chats.get(chat_id, user)

    @app.post("/api/v1/chats/{chat_id}/messages")
    async def message(chat_id: str, body: MessageBody, user: Member) -> StreamingResponse:
        chats.get(chat_id, user)

        async def reply() -> AsyncIterator[str]:
            yield 'event: status\ndata: {"message":"Thinking about your question"}\n\n'
            try:
                result = await chats.ask(chat_id, body.question, body.operation, user)
                yield f"event: answer\ndata: {result.model_dump_json()}\n\n"
            except HTTPException as exc:
                yield f"event: error\ndata: {json.dumps({'message': str(exc.detail), 'status': exc.status_code})}\n\n"

        return StreamingResponse(reply(), media_type="text/event-stream")

    @app.get("/api/v1/owner/report")
    def report(user: Member) -> dict[str, object]:
        if not user.owner:
            raise HTTPException(403, "Owner access is required")
        db = store.snapshot()
        week = [e for e in db.events if float(str(e["at"])) >= time.time() - 7 * 86400]
        return {
            "budget_usd": config.budget_usd,
            "spent_usd": db.spent,
            "reserved_usd": db.reserved,
            "remaining_usd": max(0, config.budget_usd - db.spent - db.reserved),
            "generation_enabled": config.generation_enabled,
            "generation_reserve_usd": config.generation_reserve,
            "lesson_count": len(db.lessons),
            "events": week,
            "feedback": list(db.feedback.values()),
            "ledger": list(db.ledger.values()),
            "jobs": [
                {
                    **domain.job(key),
                    "failure_type": raw.get("failure_type"),
                    "failed_phase": raw.get("failed_phase"),
                    "quality_issues": raw.get("quality_issues", []),
                    "validation_issues": raw.get("validation_issues", []),
                }
                for key, raw in db.jobs.items()
            ],
            "members": [{"id": u["id"], "name": u["name"]} for u in db.users.values()],
        }

    register_teaching_routes(app, store, member)
    return app
