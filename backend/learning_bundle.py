"""Resolve validated learning paths and immutable lesson data for every client."""

from fastapi import HTTPException

from .domain import User
from .learning_paths import LearningPath, PathNode
from .learning_reviews import native_release_identity, review_state
from .path_publication import bundle_binding
from .public_preview import public_preview_identity
from .quality import learning_issues
from .starters import digest_spec
from .store import Database
from .stored_lessons import has_teaching, parse_stored_spec


def learning_bundle(db: Database, lesson_id: str, user: User) -> dict[str, object]:
    """A complete core is a valid one-node path; never fabricate optional depth."""
    root = db.lessons.get(lesson_id)
    if root is None:
        raise HTTPException(404, "Explanation not found")
    spec = parse_stored_spec(root["spec"])
    if not has_teaching(spec) or not spec.teaching:
        raise HTTPException(422, "Earlier revisions use their preserved reader")
    binding = bundle_binding(db, lesson_id)
    preview = public_preview_identity(db, lesson_id)
    if spec.version == 3 and not user.owner and not native_release_identity(db, lesson_id, binding.sha256) and not preview:
        raise HTTPException(404, "Explanation not found")
    if binding.issues and (not binding.path or root.get("learning_bundle_sha256")):
        raise HTTPException(409, "The learning path needs owner attention before it can be opened")
    path = binding.path
    if path is None:
        path = LearningPath(
            schema_version="learning-path-1", id=lesson_id, title=spec.title,
            example=spec.summary, entry="core", nodes=[PathNode(
                id="core", role="core", label="The complete picture", question=spec.question,
                outcome=spec.teaching.goal, lesson_id=lesson_id, prerequisites=[], next=[],
                queries=[spec.question, *spec.aliases[:10]],
            )],
        )
    if path.nodes[0].lesson_id != lesson_id:
        raise HTTPException(409, "The learning path refers to a different core revision")
    lessons = []
    for node in path.nodes:
        record = db.lessons[node.lesson_id]
        node_spec = parse_stored_spec(record["spec"])
        if not has_teaching(node_spec):
            raise HTTPException(409, "A path node has incompatible teaching data")
        node_preview = public_preview_identity(db, node.lesson_id, lesson_id)
        if node.lesson_id != lesson_id and node_spec.version == 3 and not user.owner and not native_release_identity(db, node.lesson_id) and not node_preview:
            raise HTTPException(404, "A path explanation is being reviewed again")
        lessons.append({
            "id": node.lesson_id, "spec": node_spec.model_dump(mode="json"),
            "spec_sha256": digest_spec(node_spec), "video_sha256": str(record.get("video_sha256", "")),
            "quality": record.get("quality", "generated"), "superseded_by": record.get("superseded_by"),
            "public_preview": node_preview,
            "review_needed": bool(learning_issues(node_spec)) or not review_state(db, node.lesson_id)["ready"],
            "video_ready": bool(record.get("video")), "feedback": db.feedback.get(f"{user.id}:{node.lesson_id}") if user.id else None,
        })
    return {"path": path.model_dump(mode="json"), "bundle_sha256": binding.sha256, "lessons": lessons}
