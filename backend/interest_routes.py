"""HTTP transport for free requests, owner triage and private availability updates."""

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel, ConfigDict, Field

from .curated_costs import CuratedCostReport, curated_cost_report
from .domain import Domain, User
from .interests import Interests, InterestStatus
from .settings import Settings
from .store import Database, Store


class InterestUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: InterestStatus
    lesson_id: str | None = Field(default=None, max_length=100)
    note: str = Field(default="", max_length=600)


class InterestBuild(BaseModel):
    """An owner click names an attempt; a lost HTTP response cannot authorize another."""

    model_config = ConfigDict(extra="forbid")
    operation: str = Field(pattern=r"^[a-zA-Z0-9-]{8,80}$")


def register_interest_routes(app: FastAPI, store: Store, settings: Settings,
                             member: Callable[..., User], dispatch: Callable[[str, str], Awaitable[None]]) -> None:
    """One domain service; only the explicit owner build endpoint can spend money."""
    interests = Interests(store, settings)

    @app.get("/api/v1/owner/costs")
    def costs(user: Annotated[User, Depends(member)]) -> CuratedCostReport:
        interests.owner(user)
        return curated_cost_report(store.snapshot(), settings, user)

    @app.get("/api/v1/requests")
    def mine(user: Annotated[User, Depends(member)]) -> list[dict[str, object]]:
        return interests.mine(user)

    @app.get("/api/v1/notifications")
    def notifications(user: Annotated[User, Depends(member)]) -> list[dict[str, object]]:
        return interests.updates(user)

    @app.post("/api/v1/notifications/{key}/read")
    def read(key: str, user: Annotated[User, Depends(member)]) -> dict[str, bool]:
        return interests.read(key, user)

    @app.get("/api/v1/owner/requests")
    def queue(user: Annotated[User, Depends(member)]) -> list[dict[str, object]]:
        return interests.queue(user)

    @app.patch("/api/v1/owner/requests/{key}")
    def update(key: str, body: InterestUpdate, user: Annotated[User, Depends(member)]) -> dict[str, bool]:
        return interests.update(key, body.status, body.lesson_id, body.note, user)

    @app.post("/api/v1/owner/requests/{key}/build")
    async def build(key: str, body: InterestBuild, user: Annotated[User, Depends(member)]) -> dict[str, object]:
        interests.owner(user)
        from fastapi import HTTPException
        record = store.snapshot().topic_interests.get(key)
        if not record:
            raise HTTPException(404, "Topic request not found")
        result = Domain(store, settings).request(str(record["question"]), user,
                                                owner_build=True, operation=body.operation)
        if result["kind"] == "job":
            job = Domain(store, settings).job(str(result["job_id"]))
            def remember(db: Database) -> None:
                db.topic_interests[key].update(status="working", job_id=job["id"])
            store.transaction(remember)
            await dispatch(str(job["id"]), str(job["phase"]))
        return result
