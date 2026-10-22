"""Explicit owner adoption of an already released native core, never import-time release."""

import time
from typing import Annotated

from _shared.services.logger import get_logger
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .domain import Domain, User
from .learning_reviews import review_state
from .native_contracts import NativeLessonSpec
from .path_publication import bundle_binding
from .store import Database, Store
from .stored_lessons import current_lesson, parse_stored_spec

logger = get_logger(__name__)
LessonId = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9-]{0,119}$")]


class NativeActivationBody(BaseModel):
    """The owner pins both the released artifact and the exact prior public heads."""

    model_config = ConfigDict(extra="forbid")
    spec_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    video_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    bundle_sha256: str = Field(pattern=r"^(?:|[a-f0-9]{64})$")
    expected_old_ids: list[LessonId] = Field(min_length=1, max_length=12)

    @model_validator(mode="after")
    def distinct_heads(self) -> "NativeActivationBody":
        if len(set(self.expected_old_ids)) != len(self.expected_old_ids):
            raise ValueError("Replacement IDs must be distinct")
        return self


class NativeActivation:
    """Atomically move catalog heads while retaining every old byte and conversation."""

    def __init__(self, store: Store) -> None:
        self.store = store

    def activate(self, lesson_id: str, body: NativeActivationBody, user: User) -> dict[str, object]:
        if not user.owner:
            raise HTTPException(403, "Owner access is required")

        def write(db: Database) -> dict[str, object]:
            target = db.lessons.get(lesson_id)
            if target is None:
                raise HTTPException(404, "Lesson not found")
            if (not isinstance(parse_stored_spec(target["spec"]), NativeLessonSpec)
                    or target.get("depth_parent") or target.get("archived") or target.get("superseded_by")):
                raise HTTPException(409, "Activation requires an active native core, not a branch or prior revision")
            identity = review_state(db, lesson_id)
            if any(getattr(body, key) != identity[key] for key in ("spec_sha256", "video_sha256", "bundle_sha256")):
                raise HTTPException(409, "The released artifact or learning bundle changed; inspect its current identity")
            if not identity["ready"]:
                raise HTTPException(409, "Activation requires all current artifact-bound human release gates")
            expected = sorted(body.expected_old_ids)
            if lesson_id in expected:
                raise HTTPException(409, "A lesson cannot replace itself")
            pending = target.get("pending_replaces")
            if pending is not None and (not isinstance(pending, list) or any(not isinstance(item, str) for item in pending)):
                raise HTTPException(409, "The imported replacement intent needs owner attention")
            if pending and sorted(pending) != expected:
                raise HTTPException(409, "The expected old IDs differ from the imported replacement intent")
            binding: dict[str, object] = {"spec_sha256": body.spec_sha256, "video_sha256": body.video_sha256,
                                          "bundle_sha256": body.bundle_sha256, "replaced_ids": expected}
            previous = target.get("native_activation")
            if previous:
                if not isinstance(previous, dict) or previous.get("binding") != binding:
                    raise HTTPException(409, "This native revision already has a different activation intent")
                if not all(db.lessons.get(old, {}).get("superseded_by") == lesson_id
                           and db.lessons[old].get("archived") for old in expected):
                    raise HTTPException(409, "The previous activation chain needs owner attention")
                return {"lesson_id": lesson_id, "replaced_ids": expected, "reused": True}
            # Active graph leaves cannot be archived underneath another published core.
            for root in db.lessons.values():
                if root.get("archived") or root.get("depth_parent"):
                    continue
                graph = bundle_binding(db, str(root["id"]))
                if graph.path and any(n.lesson_id in [*expected, lesson_id] for n in graph.path.nodes[1:]):
                    raise HTTPException(409, "A replacement is an attached depth branch; compose a new core revision instead")
            for old_id in expected:
                old = db.lessons.get(old_id)
                if old is None:
                    raise HTTPException(409, "An expected old lesson is missing")
                head = current_lesson(db, old_id, True)
                if old.get("depth_parent") or head is not old or old.get("archived"):
                    raise HTTPException(409, "An expected old lesson is a branch or is no longer its active head")
            for old_id in expected:
                db.lessons[old_id].update(archived=True, superseded_by=lesson_id)
            target["native_activation"] = {"binding": binding, "at": time.time(), "by": user.id}
            Domain.event(db, "native_activated", user, lesson_id=lesson_id, replaced_ids=expected,
                         spec_sha256=body.spec_sha256, video_sha256=body.video_sha256,
                         bundle_sha256=body.bundle_sha256)
            return {"lesson_id": lesson_id, "replaced_ids": expected, "reused": False}

        result = self.store.transaction(write)
        logger.info("Native core activation completed", task="native-activation", route="owner-activate",
                    lesson_id=lesson_id, reused=result["reused"])
        return result
