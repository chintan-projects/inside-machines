"""Catalog lookup, transactional job admission, and private-session accounting."""

import hashlib
import secrets
import time
from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel

from .contracts import LessonSpec, canonicalize
from .quality import learning_issues
from .settings import Settings
from .starters import digest_spec
from .store import Database, Store


class User(BaseModel):
    """The browser sees its own identity, never another session's bearer token."""

    id: str
    name: str
    owner: bool


class Domain:
    """Application rules use one transaction for lookup, deduplication, and reservation."""

    def __init__(self, store: Store, settings: Settings) -> None:
        """Bind the durable domain repository."""
        self.store, self.settings = store, settings

    @staticmethod
    def event(db: Database, kind: str, user: User, **fields: object) -> None:
        """Store bounded alpha telemetry without private chat text."""
        db.events.append({"kind": kind, "user_id": user.id, "at": time.time(), **fields})

    def catalog(self) -> list[dict[str, object]]:
        """Project public metadata only; never return owner job data or private chat."""

        def read(db: Database) -> list[dict[str, object]]:
            from .learning_reviews import review_state

            result = []
            for lesson in db.lessons.values():
                if lesson.get("archived"):
                    continue
                spec = LessonSpec.model_validate(lesson["spec"])
                result.append(
                    {
                        "id": lesson["id"],
                        "title": spec.title,
                        "canonical": spec.canonical,
                        "question": spec.question,
                        "summary": spec.summary,
                        "family": spec.family,
                        "category": spec.category,
                        "accent": spec.accent,
                        "duration": sum(s.duration for s in spec.stages),
                        "parts": len(spec.parts),
                        "quality": lesson.get("quality", "generated"),
                        "review_needed": bool(learning_issues(spec))
                        or not review_state(db, str(lesson["id"]))["ready"],
                        "created_at": lesson.get("created_at", 0),
                        "views": lesson.get("views", 0),
                        "video_ready": bool(lesson.get("video")),
                        "preview": spec.model_dump(mode="json"),
                    }
                )
            return sorted(result, key=lambda item: float(str(item["created_at"])), reverse=True)

        return self.store.transaction(read, write=False)

    def request(
        self, question: str, user: User, *, revision_of: str | None = None, operation: str = ""
    ) -> dict[str, object]:
        """Return a cached lesson, attach to a pending job, or atomically admit new work."""
        canonical = canonicalize(question)
        if not canonical:
            raise HTTPException(422, "Tell us which machine you want to understand.")
        if revision_of:
            if not user.owner:
                raise HTTPException(403, "Owner access is required")
            if not operation or len(operation) > 80:
                raise HTTPException(422, "A bounded revision operation ID is required")
            canonical = (
                canonical[:60].rstrip("-")
                + "-ce-"
                + hashlib.sha256((revision_of + ":" + operation).encode()).hexdigest()[:10]
            )

        def admit(db: Database) -> dict[str, object]:
            parent = db.lessons.get(revision_of) if revision_of else None
            if revision_of:
                if parent is None:
                    raise HTTPException(404, "Lesson not found")
                if parent.get("superseded_by"):
                    existing = db.lessons.get(canonical)
                    if existing:
                        return {"kind": "lesson", "lesson_id": canonical, "reused": True}
                    raise HTTPException(409, "Open the latest revision before requesting another draft")
                for pending in db.jobs.values():
                    if pending.get("revision_of") == revision_of and pending["status"] not in (
                        "failed",
                        "complete",
                    ):
                        return {"kind": "job", "job_id": pending["id"], "reused": True}
                    if pending["canonical"] == canonical and pending["status"] == "failed":
                        raise HTTPException(
                            409, "That revision attempt failed. Explicitly start a new operation to try again"
                        )
            for lesson in db.lessons.values():
                if lesson.get("archived"):
                    continue
                spec = LessonSpec.model_validate(lesson["spec"])
                names = {spec.canonical, *(canonicalize(a) for a in spec.aliases)}
                if canonical in names and (not revision_of or spec.canonical == canonical):
                    self.event(db, "catalog_hit", user, question=question, lesson_id=lesson["id"])
                    return {"kind": "lesson", "lesson_id": lesson["id"], "reused": True}
            for job in db.jobs.values():
                if job["canonical"] == canonical and job["status"] not in ("failed", "complete"):
                    self.event(db, "joined_job", user, question=question, job_id=job["id"])
                    return {"kind": "job", "job_id": job["id"], "reused": True}
            if not self.settings.generation_enabled:
                self.event(db, "requested_topic", user, question=question, canonical=canonical)
                return {
                    "kind": "unavailable",
                    "message": "Your request is saved. New explanations will be available once the owner connects AI generation and sets the alpha budget. Existing lessons still work.",
                }
            recent = [
                e
                for e in db.events
                if e.get("user_id") == user.id
                and e["kind"] == "generation_requested"
                and float(str(e["at"])) > time.time() - 3600
            ]
            if len(recent) >= self.settings.hourly_requests:
                raise HTTPException(
                    429, "You've reached the hourly alpha limit. Try an existing explanation."
                )
            reserve = self.settings.generation_reserve
            if db.spent + db.reserved + reserve > self.settings.budget_usd:
                self.event(db, "budget_block", user, canonical=canonical)
                return {
                    "kind": "budget",
                    "message": "The alpha's generation budget is reserved or used. You can still explore every existing explanation.",
                }
            job_id = secrets.token_urlsafe(18)
            db.jobs[job_id] = {
                "id": job_id,
                "canonical": canonical,
                "question": question,
                "user_id": user.id,
                "status": "queued",
                "phase": "queued",
                "pipeline_version": "evidence-first-1",
                "message": "Waiting to build your explanation",
                "created_at": time.time(),
                "updated_at": time.time(),
                "lease_until": 0,
                "lease_token": "",
                "attempts": 0,
                "receipt": {},
                "spec": None,
                "audio": [],
                "video": None,
                "cost_usd": 0,
                "error": None,
                "reservation": reserve,
                "revision_of": revision_of,
                "revision_parent_sha256": digest_spec(LessonSpec.model_validate(parent["spec"]))
                if parent
                else None,
            }
            db.reserved += reserve
            self.event(
                db, "generation_requested", user, question=question, job_id=job_id, canonical=canonical
            )
            return {"kind": "job", "job_id": job_id, "reused": False}

        return self.store.transaction(admit)

    def job(self, job_id: str) -> dict[str, object]:
        """Family members may see job progress, not requester identity or private details."""

        def read(db: Database) -> dict[str, object]:
            job = db.jobs.get(job_id)
            if not job:
                raise HTTPException(404, "Explanation request not found")
            return {
                key: job.get(key)
                for key in (
                    "id",
                    "canonical",
                    "status",
                    "phase",
                    "pipeline_version",
                    "message",
                    "created_at",
                    "updated_at",
                    "error",
                    "lesson_id",
                )
            }

        return self.store.transaction(read, write=False)

    def feedback(
        self,
        lesson_id: str,
        value: Literal["up", "down"],
        reason: str,
        user: User,
        *,
        stage: int | None = None,
    ) -> None:
        """Update one family member's response without equating votes with verification."""

        def update(db: Database) -> None:
            if lesson_id not in db.lessons:
                raise HTTPException(404, "Lesson not found")
            spec = LessonSpec.model_validate(db.lessons[lesson_id]["spec"])
            if stage is not None and not 0 <= stage < len(spec.stages):
                raise HTTPException(422, "Feedback refers to an unknown lesson step")
            db.feedback[f"{user.id}:{lesson_id}"] = {
                "lesson_id": lesson_id,
                "user_id": user.id,
                "value": value,
                "reason": reason,
                "stage": stage,
                "version": spec.version,
                "at": time.time(),
            }
            self.event(db, "feedback", user, lesson_id=lesson_id, value=value)

        self.store.transaction(update)

    def settle(self, db: Database, job: dict[str, object], status: str, error: str | None = None) -> None:
        """Release a reservation exactly once, preserving the actual usage ledger."""
        if job["status"] in ("complete", "failed"):
            return
        db.reserved = max(0, db.reserved - float(str(job["reservation"])))
        job.update(status=status, error=error, updated_at=time.time(), lease_until=0)
