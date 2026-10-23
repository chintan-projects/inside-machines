"""Explicit artifact-bound public demos, separate from human review and activation."""

import time

from _shared.services.logger import get_logger
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .domain import Domain, User
from .native_contracts import NativeLessonSpec
from .native_publication import native_record_issues
from .path_publication import bundle_binding
from .quality import learning_issues
from .starters import digest_spec
from .store import Database, Store
from .stored_lessons import parse_stored_spec

logger = get_logger(__name__)
SHA = r"^[a-f0-9]{64}$"


class PreviewIdentity(BaseModel):
    """Owner consent names the exact public root and current composition."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    spec_sha256: str = Field(pattern=SHA)
    video_sha256: str = Field(pattern=SHA)
    bundle_sha256: str = Field(pattern=r"^(?:|[a-f0-9]{64})$")


class PreviewSubmission(PreviewIdentity):
    enabled: bool = Field(strict=True)


class PreviewArtifact(BaseModel):
    """All child teaching data, actual media and native proof remain pinned."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    lesson_id: str
    spec_sha256: str = Field(pattern=SHA)
    video_sha256: str = Field(pattern=SHA)
    proof_sha256: str = Field(pattern=SHA)
    artifact_sha256: str = Field(pattern=SHA)


class PreviewBinding(PreviewIdentity):
    bindings: list[PreviewArtifact] = Field(min_length=1, max_length=12)


def _candidate(db: Database, lesson_id: str) -> PreviewBinding:
    root = db.lessons.get(lesson_id)
    if not root:
        raise HTTPException(404, "Lesson not found")
    if root.get("archived") or root.get("superseded_by") or root.get("depth_parent"):
        raise HTTPException(409, "Public preview requires an active root revision")
    graph = bundle_binding(db, lesson_id)
    if graph.issues:
        raise HTTPException(409, "Repair the exact learning bundle before enabling a public preview")
    ids = [node.lesson_id for node in graph.path.nodes] if graph.path else [lesson_id]
    artifacts = []
    for node_id in ids:
        record = db.lessons[node_id]
        spec = parse_stored_spec(record["spec"])
        if (not isinstance(spec, NativeLessonSpec) or not record.get("video")
                or learning_issues(spec) or native_record_issues(record, spec)):
            raise HTTPException(409, "Public preview needs complete, source-bound native artifacts; it cannot bypass structural checks")
        digest = digest_spec(spec)
        latest: dict[str, object] = {}
        for review in db.learning_reviews:
            if (review.get("lesson_id") == node_id and review.get("spec_sha256") == digest
                    and review.get("video_sha256") == record.get("video_sha256")):
                # Recomposition cannot erase a truth/craft/learning rejection of
                # unchanged artwork. Only a later same-artifact gate verdict can.
                latest[str(review.get("gate"))] = review.get("decision")
        if "needs-work" in latest.values():
            raise HTTPException(409, "The current artifact has an unresolved review rejection; public preview cannot override it")
        artifacts.append(PreviewArtifact(
            lesson_id=node_id, spec_sha256=digest, video_sha256=str(record["video_sha256"]),
            proof_sha256=str(record["native_proof_sha256"]), artifact_sha256=str(record["native_artifact_sha256"])))
    return PreviewBinding(spec_sha256=artifacts[0].spec_sha256, video_sha256=artifacts[0].video_sha256,
                          bundle_sha256=graph.sha256, bindings=artifacts)


def public_preview_identity(db: Database, lesson_id: str, root_id: str | None = None) -> bool:
    """A changed/revoked demo cannot grant root, descendant, media or private chat access."""
    if lesson_id not in db.lessons:
        return False
    # The bound graph is authoritative: earlier standalone leaf imports need
    # not have a mutable parent hint, and one immutable leaf may be reused.
    roots = [root_id] if root_id else list(db.lessons)
    for parent_id in roots:
        raw = db.lessons.get(parent_id, {}).get("public_preview")
        if not isinstance(raw, dict) or raw.get("enabled") is not True:
            continue
        try:
            saved = PreviewBinding.model_validate(raw.get("binding"))
            if lesson_id in {bound.lesson_id for bound in saved.bindings} and saved == _candidate(db, parent_id):
                return True
        except (HTTPException, ValueError, OSError, ValidationError):
            continue
    return False


class PublicPreviews:
    """One explicit, reversible owner operation; never approve, notify or spend."""

    def __init__(self, store: Store) -> None:
        self.store = store

    @staticmethod
    def owner(user: User) -> None:
        if not user.owner:
            raise HTTPException(403, "Owner access is required")

    def status(self, lesson_id: str, user: User) -> dict[str, object]:
        self.owner(user)

        def read(db: Database) -> dict[str, object]:
            record = db.lessons.get(lesson_id)
            if not record:
                raise HTTPException(404, "Lesson not found")
            saved = record.get("public_preview")
            try:
                candidate = _candidate(db, lesson_id).model_dump(mode="json")
                issue = ""
            except (HTTPException, ValueError, OSError) as exc:
                candidate = None
                issue = str(exc.detail) if isinstance(exc, HTTPException) else "The current preview candidate needs owner attention"
            return {"lesson_id": lesson_id, "candidate": candidate, "preview": saved,
                    "enabled": public_preview_identity(db, lesson_id), "issue": issue,
                    "notice": "Public review draft. Not human-approved, certified or activated."}

        return self.store.transaction(read, write=False)

    def set(self, lesson_id: str, body: PreviewSubmission, user: User) -> dict[str, object]:
        self.owner(user)
        identity = PreviewIdentity.model_validate(body.model_dump(exclude={"enabled"}))

        def write(db: Database) -> dict[str, object]:
            root = db.lessons.get(lesson_id)
            if not root:
                raise HTTPException(404, "Lesson not found")
            saved = root.get("public_preview")
            previous = saved if isinstance(saved, dict) else {}
            if body.enabled:
                binding = _candidate(db, lesson_id)
                if identity != PreviewIdentity.model_validate(binding.model_dump(exclude={"bindings"})):
                    raise HTTPException(409, "The public preview artifact or bundle changed")
                raw = binding.model_dump(mode="json")
                if previous.get("enabled") is True and previous.get("binding") == raw:
                    return {"lesson_id": lesson_id, "enabled": True, "reused": True}
            else:
                # Revoke the saved identity even when source/current composition has broken.
                try:
                    binding = PreviewBinding.model_validate(previous.get("binding"))
                except ValidationError as exc:
                    raise HTTPException(409, "There is no recorded preview identity to revoke") from exc
                if identity != PreviewIdentity.model_validate(binding.model_dump(exclude={"bindings"})):
                    raise HTTPException(409, "Revocation must name the recorded preview identity")
                raw = binding.model_dump(mode="json")
                if previous.get("enabled") is False:
                    return {"lesson_id": lesson_id, "enabled": False, "reused": True}
            root["public_preview"] = {"binding": raw, "enabled": body.enabled, "by": user.id, "at": time.time()}
            Domain.event(db, "public_preview_enabled" if body.enabled else "public_preview_revoked", user,
                         lesson_id=lesson_id, **identity.model_dump())
            return {"lesson_id": lesson_id, "enabled": body.enabled, "reused": False}

        result = self.store.transaction(write)
        logger.info("Public preview permission saved", task="public-preview", route="owner-public-preview",
                    lesson_id=lesson_id, enabled=result["enabled"], reused=result["reused"])
        return result
