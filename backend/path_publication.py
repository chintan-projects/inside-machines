"""Owner composition of existing lessons, with immutable graph and artifact bindings."""

import hashlib
import json
import time
from dataclasses import dataclass

from _shared.services.logger import get_logger
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .domain import User
from .learning_paths import LearningPath, validate_path
from .quality import learning_issues
from .starters import digest_spec
from .store import Database, Store
from .stored_lessons import has_teaching, parse_stored_spec

logger = get_logger(__name__)
SHA = r"^[a-f0-9]{64}$"


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class BoundLesson(BaseModel):
    """Each node pins immutable visual content and narration, not just its public ID."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    lesson_id: str
    spec_sha256: str = Field(pattern=SHA)
    video_sha256: str = Field(pattern=SHA)


class PublishedPath(BaseModel):
    """The content identity excludes operational metadata such as who attached it."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    root_lesson_id: str
    path: LearningPath
    bindings: list[BoundLesson]
    path_sha256: str = Field(pattern=SHA)
    bundle_sha256: str = Field(pattern=SHA)
    created_at: float
    created_by: str

    def content_identity(self) -> str:
        """Bind the graph to the root and the exact referenced artifacts."""
        return _digest({
            "root_lesson_id": self.root_lesson_id, "path_sha256": self.path_sha256,
            "bindings": [binding.model_dump(mode="json") for binding in self.bindings],
        })


@dataclass(frozen=True)
class BundleBinding:
    """A broken attachment is held for review, never treated as a standalone lesson."""

    sha256: str
    path: LearningPath | None
    issues: list[str]


def bundle_binding(db: Database, root_id: str) -> BundleBinding:
    """Validate the current pointer and all pinned leaf artifacts without recursion."""
    root = db.lessons.get(root_id)
    if root is None:
        raise HTTPException(404, "Lesson not found")
    pointer = str(root.get("learning_bundle_sha256", ""))
    if not pointer:
        if root.get("learning_path"):
            try:
                legacy = validate_path(json.dumps(root["learning_path"]), set(db.lessons))
                if legacy.nodes[0].lesson_id != root_id:
                    raise ValueError("Wrong core")
                for node in legacy.nodes:
                    spec = parse_stored_spec(db.lessons[node.lesson_id]["spec"])
                    if not has_teaching(spec):
                        raise ValueError("Incompatible node")
            except (ValueError, ValidationError):
                return BundleBinding(_digest(root["learning_path"]), None, ["The earlier path needs owner attention before it can be opened."])
            return BundleBinding(_digest(root["learning_path"]), legacy, ["This earlier path needs an owner-authored, artifact-bound composition."])
        return BundleBinding("", None, [])
    raw = db.learning_paths.get(pointer)
    if not raw:
        return BundleBinding(pointer, None, ["The attached learning-path record is missing."])
    try:
        record = PublishedPath.model_validate(raw)
    except ValidationError:
        return BundleBinding(pointer, None, ["The attached learning-path record is incompatible."])
    issues = []
    if record.root_lesson_id != root_id or record.path.nodes[0].lesson_id != root_id:
        issues.append("The attached path refers to another core revision.")
    if record.bundle_sha256 != pointer or record.content_identity() != pointer or _digest(record.path.model_dump(mode="json")) != record.path_sha256:
        issues.append("The learning-path content identity changed.")
    ids = [node.lesson_id for node in record.path.nodes]
    if len(set(ids)) != len(ids) or ids != [bound.lesson_id for bound in record.bindings]:
        issues.append("Path nodes and immutable artifact bindings do not match.")
    for bound in record.bindings:
        lesson = db.lessons.get(bound.lesson_id)
        if lesson is None:
            issues.append("A referenced lesson revision is missing.")
            continue
        spec = parse_stored_spec(lesson["spec"])
        if not has_teaching(spec) or digest_spec(spec) != bound.spec_sha256 or lesson.get("video_sha256") != bound.video_sha256:
            issues.append("A referenced lesson or video no longer matches its bound artifact.")
        if bound.lesson_id != root_id and (lesson.get("learning_bundle_sha256") or lesson.get("learning_path") or lesson.get("archived")):
            issues.append("Branches must remain active leaf lesson revisions; nested compositions are unsupported.")
    return BundleBinding(pointer, record.path, issues)


class PathSubmission(BaseModel):
    """Strict, data-only input; owner intent and concurrent edits are explicit."""

    model_config = ConfigDict(extra="forbid")
    path: LearningPath
    expected_bundle_sha256: str = Field(default="", pattern=r"^(?:|[a-f0-9]{64})$")
    allow_review_drafts: bool = Field(default=False, strict=True)


class PathPublication:
    """Reuse Store transactions; this service never authors content or spends money."""

    def __init__(self, store: Store) -> None:
        self.store = store

    @staticmethod
    def _owner(user: User) -> None:
        if not user.owner:
            raise HTTPException(403, "Owner access is required")

    def history(self, root_id: str, user: User) -> dict[str, object]:
        """Expose only graph/artifact metadata; keep owner IDs and private state server-side."""
        self._owner(user)

        def read(db: Database) -> dict[str, object]:
            root = db.lessons.get(root_id)
            if root is None:
                raise HTTPException(404, "Lesson not found")
            records = []
            for raw in db.learning_paths.values():
                if raw.get("root_lesson_id") == root_id:
                    record = PublishedPath.model_validate(raw)
                    records.append(record.model_dump(mode="json", exclude={"created_by"}))
            return {"root_lesson_id": root_id, "current_bundle_sha256": root.get("learning_bundle_sha256", ""),
                    "records": sorted(records, key=lambda row: float(str(row["created_at"])), reverse=True)}

        return self.store.transaction(read, write=False)

    def attach(self, root_id: str, submission: PathSubmission, user: User) -> dict[str, object]:
        """Store a new immutable composition and hold its fresh bundle review gates."""
        self._owner(user)

        def write(db: Database) -> dict[str, object]:
            from .learning_reviews import review_state, standalone_review_state

            root = db.lessons.get(root_id)
            if root is None:
                raise HTTPException(404, "Lesson not found")
            path = submission.path
            if path.nodes[0].lesson_id != root_id:
                raise HTTPException(422, "The core node must use the root lesson revision")
            if len({node.lesson_id for node in path.nodes}) != len(path.nodes):
                raise HTTPException(422, "Each depth node needs a distinct existing lesson revision")
            bindings = []
            for node in path.nodes:
                lesson = db.lessons.get(node.lesson_id)
                if lesson is None:
                    raise HTTPException(422, "A referenced lesson revision does not exist")
                spec = parse_stored_spec(lesson["spec"])
                if not has_teaching(spec) or lesson.get("archived") or not lesson.get("video"):
                    raise HTTPException(409, "Every node must be an active CE lesson with completed media")
                if learning_issues(spec):
                    raise HTTPException(409, "Every node must pass current learning-quality checks before composition")
                if spec.version == 3:
                    from .native_publication import native_record_issues
                    if native_record_issues(lesson, spec):
                        raise HTTPException(409, "Native nodes need their intact rendered source/media proof before composition")
                if node.lesson_id != root_id and (lesson.get("learning_bundle_sha256") or lesson.get("learning_path")):
                    raise HTTPException(422, "Use leaf lesson revisions; nested learning paths are unsupported")
                state = review_state(db, node.lesson_id)
                ready = bool(state["ready"])
                if node.lesson_id == root_id:
                    ready = ready or bool(standalone_review_state(db, root_id)["ready"])
                if not ready and not submission.allow_review_drafts:
                    raise HTTPException(409, "Every node needs release approval, or explicitly allow review drafts to preview a held bundle")
                try:
                    bindings.append(BoundLesson(lesson_id=node.lesson_id, spec_sha256=digest_spec(spec), video_sha256=str(lesson.get("video_sha256", ""))))
                except ValidationError as error:
                    raise HTTPException(409, "Completed node media needs its recorded SHA-256 identity") from error
            record = PublishedPath(
                root_lesson_id=root_id, path=path, bindings=bindings,
                path_sha256=_digest(path.model_dump(mode="json")), bundle_sha256="0" * 64,
                created_at=time.time(), created_by=user.id,
            )
            record = record.model_copy(update={"bundle_sha256": record.content_identity()})
            current = str(root.get("learning_bundle_sha256", ""))
            previous = db.learning_paths.get(record.bundle_sha256)
            if previous:
                try:
                    original = PublishedPath.model_validate(previous)
                except ValidationError as error:
                    raise HTTPException(409, "The saved path identity needs owner attention") from error
                if (original.content_identity() != record.bundle_sha256 or original.path != record.path
                        or original.bindings != record.bindings or original.bundle_sha256 != record.bundle_sha256):
                    raise HTTPException(409, "The saved path identity needs owner attention")
            if current == record.bundle_sha256:
                if not previous:
                    raise HTTPException(409, "The saved path record is missing; owner recovery is required")
                ready = bool(review_state(db, root_id)["ready"])
                if ready:
                    from .interests import notify_available
                    notify_available(db, root_id)
                return {"bundle_sha256": current, "path_sha256": record.path_sha256, "reused": True, "review_required": not ready}
            if current != submission.expected_bundle_sha256:
                raise HTTPException(409, "The path changed in another session. Reload its current version before attaching.")
            history = [r for r in db.learning_paths.values() if r.get("root_lesson_id") == root_id]
            if len(history) >= 32 and record.bundle_sha256 not in db.learning_paths:
                raise HTTPException(422, "This core has reached its path history limit; start a new core revision")
            if not previous:
                db.learning_paths[record.bundle_sha256] = record.model_dump(mode="json")
            root["learning_bundle_sha256"] = record.bundle_sha256
            # Legacy embedded paths remain preserved for historical evidence, but the pointer wins.
            ready = bool(review_state(db, root_id)["ready"])
            if ready:
                from .interests import notify_available
                notify_available(db, root_id)
            return {"bundle_sha256": record.bundle_sha256, "path_sha256": record.path_sha256,
                    "reused": bool(previous), "review_required": not ready}

        result = self.store.transaction(write)
        logger.info("Learning-path attachment saved", task="path-composition", root_lesson_id=root_id, bundle_sha256=result["bundle_sha256"], reused=result["reused"])
        return result
