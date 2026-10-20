"""Curated-topic demand and private in-app updates; never dispatch paid work."""

import hashlib
import time
from typing import Literal, cast

from _shared.services.logger import get_logger
from fastapi import HTTPException

from .contracts import LessonSpec, canonicalize
from .domain import User
from .learning_reviews import review_state
from .settings import Settings
from .store import Database, Store

InterestStatus = Literal["requested", "planned", "working", "available", "declined"]
logger = get_logger(__name__)


def currently_available(db: Database, lesson_id: str) -> bool:
    """Archived, missing or newly held revisions cannot advertise availability."""
    lesson = db.lessons.get(lesson_id)
    return bool(lesson and not lesson.get("archived") and review_state(db, lesson_id)["ready"])


def _current_interest(db: Database, item: dict[str, object]) -> dict[str, object]:
    """Project fresh release status without rewriting subscription history on reads."""
    result = {k: item.get(k) for k in ("id", "question", "status", "lesson_id", "updated_at")}
    if item.get("status") == "available" and not currently_available(db, str(item.get("lesson_id", ""))):
        result.update(status="working", lesson_id=None)
    return result


def notify_available(db: Database, lesson_id: str) -> None:
    """Create private, revision-bound notices only after all release gates pass."""
    if not currently_available(db, lesson_id):
        return
    identity = review_state(db, lesson_id)
    for interest in db.topic_interests.values():
        if interest.get("lesson_id") != lesson_id:
            continue
        interest.update(status="available", updated_at=time.time())
        members = cast(dict[str, object], interest["members"])
        for member_id in members:
            bundle = str(identity["bundle_sha256"])
            suffix = f":{bundle}" if bundle else ""
            key = hashlib.sha256(f"{interest['id']}:{member_id}:{lesson_id}{suffix}".encode()).hexdigest()
            if key not in db.notifications:
                db.notifications[key] = {
                    "id": key, "user_id": member_id, "topic_id": interest["id"],
                    "lesson_id": lesson_id, "title": "Your requested explanation is ready",
                    "question": interest["question"], "at": time.time(), "read": False,
                    "spec_sha256": identity["spec_sha256"], "video_sha256": identity["video_sha256"],
                    "bundle_sha256": bundle,
                }


class Interests:
    """Reuse the transactional Store; customers cannot create jobs through this module."""

    def __init__(self, store: Store, settings: Settings) -> None:
        self.store, self.settings = store, settings

    def request(self, question: str, user: User) -> dict[str, object]:
        """Reuse an existing lesson or record one subscription without reserving money."""
        canonical = canonicalize(question)
        if not canonical or len(question) > 300:
            raise HTTPException(422, "Tell us which system you would like to understand.")
        key = hashlib.sha256(canonical.encode()).hexdigest()[:24]

        def write(db: Database) -> dict[str, object]:
            for lesson in db.lessons.values():
                if lesson.get("archived") or lesson.get("depth_parent"):
                    continue
                spec = LessonSpec.model_validate(lesson["spec"])
                if canonical in {spec.canonical, *(canonicalize(a) for a in spec.aliases)}:
                    return {"kind": "lesson", "lesson_id": lesson["id"], "reused": True}
            interest = db.topic_interests.get(key)
            if not interest:
                recent = sum(
                    user.id in cast(dict[str, object], item["members"])
                    and float(str(cast(dict[str, object], item["members"])[user.id])) > time.time() - 3600
                    for item in db.topic_interests.values()
                )
                if recent >= max(1, self.settings.hourly_requests):
                    raise HTTPException(429, "Your requests are saved. Please come back later to add more.")
                interest = {"id": key, "canonical": canonical, "question": question.strip(),
                            "status": "requested", "members": {}, "lesson_id": None,
                            "created_at": time.time(), "updated_at": time.time(), "note": ""}
                db.topic_interests[key] = interest
            cast(dict[str, object], interest["members"]).setdefault(user.id, time.time())
            if interest.get("lesson_id"):
                notify_available(db, str(interest["lesson_id"]))
            return {"kind": "interest", "interest_id": key, "status": _current_interest(db, interest)["status"],
                    "message": "Request saved. We’ll let you know here when the explanation is ready. This request does not spend AI credits."}

        result = self.store.transaction(write)
        logger.info("Topic request recorded", task="topic-interest", route="requests", kind=result["kind"], topic_id=result.get("interest_id"), status=result.get("status"))
        return result

    def mine(self, user: User) -> list[dict[str, object]]:
        """Do not disclose other requesters or private notes."""
        return self.store.transaction(lambda db: [
            _current_interest(db, item)
            for item in db.topic_interests.values() if user.id in cast(dict[str, object], item["members"])
        ], write=False)

    def queue(self, user: User) -> list[dict[str, object]]:
        """Owner sees aggregate demand, not subscriber names or conversation text."""
        self.owner(user)
        return self.store.transaction(lambda db: sorted([
            {**{k: value for k, value in item.items() if k != "members"}, **_current_interest(db, item),
             "lesson_id": item.get("lesson_id"),
             "requesters": len(cast(dict[str, object], item["members"]))}
            for item in db.topic_interests.values()
        ], key=lambda item: (-int(str(item["requesters"])), str(item["created_at"]))), write=False)

    def update(self, key: str, status: InterestStatus, lesson_id: str | None, note: str, user: User) -> dict[str, bool]:
        """Bind fulfillment deliberately; a model job completing is not publication."""
        self.owner(user)

        def write(db: Database) -> None:
            item = db.topic_interests.get(key)
            if not item:
                raise HTTPException(404, "Topic request not found")
            if lesson_id and lesson_id not in db.lessons:
                raise HTTPException(404, "Lesson not found")
            if status == "available" and (not lesson_id or not currently_available(db, lesson_id)):
                raise HTTPException(409, "Availability requires a released, reviewed lesson revision")
            item.update(status=status, lesson_id=lesson_id, note=note, updated_at=time.time())
            if lesson_id:
                notify_available(db, lesson_id)

        self.store.transaction(write)
        logger.info("Topic triage saved", task="topic-interest", route="owner-requests", topic_id=key, status=status, lesson_id=lesson_id)
        return {"ok": True}

    def updates(self, user: User) -> list[dict[str, object]]:
        """Member-scoped notification inbox; no external delivery is implied."""
        def read(db: Database) -> list[dict[str, object]]:
            result: list[dict[str, object]] = []
            for item in db.notifications.values():
                if item["user_id"] != user.id:
                    continue
                lesson_id = str(item["lesson_id"])
                available = currently_available(db, lesson_id)
                if available:
                    identity = review_state(db, lesson_id)
                    available = all(item.get(key) == identity[key] for key in ("spec_sha256", "video_sha256"))
                    available = available and item.get("bundle_sha256", "") == identity["bundle_sha256"]
                result.append({
                    **{k: item[k] for k in ("id", "question", "read", "at")},
                    "lesson_id": lesson_id if available else None, "available": available,
                    "title": "Your requested explanation is ready" if available else "This explanation is being reviewed again",
                })
            return sorted(result, key=lambda item: float(str(item["at"])), reverse=True)
        return self.store.transaction(read, write=False)

    def read(self, key: str, user: User) -> dict[str, bool]:
        def write(db: Database) -> None:
            item = db.notifications.get(key)
            if not item or item["user_id"] != user.id:
                raise HTTPException(404, "Update not found")
            item["read"] = True
        self.store.transaction(write)
        return {"ok": True}

    @staticmethod
    def owner(user: User) -> None:
        if not user.owner:
            raise HTTPException(403, "Owner access is required")
