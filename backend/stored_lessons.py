"""One reader for immutable legacy geometry and explicitly versioned native lessons."""

from fastapi import HTTPException

from .contracts import LessonSpec, Part
from .native_contracts import NativeComponent, NativeLessonSpec
from .store import Database

type StoredSpec = LessonSpec | NativeLessonSpec


def parse_stored_spec(value: object) -> StoredSpec:
    """Dispatch only the declared artifact version; never reinterpret a legacy payload."""
    if isinstance(value, dict) and value.get("version") == 3:
        return NativeLessonSpec.model_validate(value)
    return LessonSpec.model_validate(value)


def components_for(spec: StoredSpec) -> list[Part] | list[NativeComponent]:
    """Expose actual semantic identities without manufacturing primitive geometry."""
    return spec.components if isinstance(spec, NativeLessonSpec) else spec.parts


def component_ids(spec: StoredSpec) -> list[str]:
    """Share progress/chat selection identity across both artifact representations."""
    return [part.id for part in components_for(spec)]


def has_teaching(spec: StoredSpec) -> bool:
    """Legacy v1 retains its reader; both teaching contracts have their own gates."""
    return spec.version in (2, 3) and spec.teaching is not None


def native_visible(db: Database, lesson_id: str, owner: bool) -> bool:
    """Native imports remain owner previews until the existing human release gates pass."""
    record = db.lessons.get(lesson_id)
    if record is None:
        return False
    if owner or parse_stored_spec(record["spec"]).version != 3:
        return True
    from .learning_reviews import native_release_identity
    from .public_preview import public_preview_identity
    return native_release_identity(db, lesson_id) or public_preview_identity(db, lesson_id)


def current_lesson(db: Database, lesson_id: str, owner: bool) -> dict[str, object] | None:
    """Resolve preserved aliases to one active, visible head without rewriting history."""
    current = db.lessons.get(lesson_id)
    visited = {lesson_id}
    while current and current.get("superseded_by"):
        target = str(current["superseded_by"])
        if target in visited or target not in db.lessons:
            raise HTTPException(409, "This lesson's revision chain needs owner attention")
        visited.add(target)
        current = db.lessons[target]
    if not current or current.get("archived") or not native_visible(db, str(current["id"]), owner):
        return None
    return current
