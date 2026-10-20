"""Typed, reviewable edits preserve a rejected draft's correct existing work."""

from typing import cast

from pydantic import Field

from .contracts import AuthorLessonSpec, Part, Stage, StrictModel
from .starters import digest_spec
from .teaching_contracts import TeachingSpec


class StageEdit(StrictModel):
    """Address a stage by its stable teaching beat identity."""

    beat_id: str
    stage: Stage


class LessonPatch(StrictModel):
    """Data edits only: no arbitrary paths, code, sources or identity changes."""

    base_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    parts: list[Part] = Field(max_length=40)
    graphics: list[Part] = Field(max_length=60)
    stages: list[StageEdit] = Field(max_length=7)
    teaching: TeachingSpec | None
    notes: list[str] = Field(max_length=10)


def patch_schema(base: AuthorLessonSpec) -> dict[str, object]:
    """Bind the proposal to one exact source draft before model dispatch."""
    schema = LessonPatch.model_json_schema()
    properties = cast(dict[str, dict[str, object]], schema["properties"])
    properties["base_sha256"]["enum"] = [digest_spec(base)]
    return schema


def apply_revision(raw: str | bytes, base: AuthorLessonSpec, canonical: str) -> AuthorLessonSpec:
    """Compile a new artifact without altering its source or relaxing any contract."""
    patch = LessonPatch.model_validate_json(raw)
    if patch.base_sha256 != digest_spec(base):
        raise ValueError("Revision patch refers to another source draft")
    updated = base.model_copy(deep=True)
    for name, edits in (("parts", patch.parts), ("graphics", patch.graphics)):
        if len({p.id for p in edits}) != len(edits):
            raise ValueError("A revision can update each shape only once")
        current = updated.parts if name == "parts" else updated.graphics
        by_id = {p.id: p for p in edits}
        result = [by_id.pop(p.id, p) for p in current] + list(by_id.values())
        if name == "parts":
            updated.parts = result
        else:
            updated.graphics = result
    if updated.teaching is None:
        raise ValueError("A revision needs teaching data")
    indexes = {b.id: b.stage for b in updated.teaching.beats}
    if len({e.beat_id for e in patch.stages}) != len(patch.stages):
        raise ValueError("A revision can update each stage only once")
    for edit in patch.stages:
        if edit.beat_id not in indexes:
            raise ValueError("Revision references an unknown teaching beat")
        updated.stages[indexes[edit.beat_id]] = edit.stage
    if patch.teaching is not None:
        updated.teaching = patch.teaching
    if updated.model_dump(exclude={"canonical"}) == base.model_dump(exclude={"canonical"}):
        raise ValueError("The revision made no actual change")
    updated.canonical = canonical
    return AuthorLessonSpec.model_validate(updated.model_dump(mode="json"))
