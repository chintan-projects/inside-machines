"""Typed edits keep source identity immutable and preserve shared validation."""

import pytest

from backend.contracts import AuthorLessonSpec, LessonSpec
from backend.lesson_patch import LessonPatch, StageEdit, apply_revision, patch_schema
from backend.quality import require_learning_quality
from backend.starters import digest_spec


def test_patch_keeps_source_and_untouched_data_immutable(ce_spec: LessonSpec) -> None:
    """A geometric correction becomes a fresh full artifact, not a source overwrite."""
    base = AuthorLessonSpec.model_validate(ce_spec.model_dump())
    before = base.model_dump_json()
    part = base.graphics[0].model_copy(update={"x": base.graphics[0].x + 1})
    assert base.teaching is not None
    stage = base.stages[0].model_copy(
        update={"narration": base.stages[0].narration + " This is a synthetic test."}
    )
    patch = LessonPatch(
        base_sha256=digest_spec(base),
        parts=[],
        graphics=[part],
        stages=[StageEdit(beat_id=base.teaching.beats[0].id, stage=stage)],
        teaching=None,
        notes=["Synthetic edit, not factual review."],
    )
    updated = apply_revision(patch.model_dump_json(), base, "new-test-revision")
    require_learning_quality(updated)
    assert base.model_dump_json() == before
    assert updated.canonical == "new-test-revision" and updated.sources == base.sources
    assert updated.graphics[0] == part and updated.graphics[1:] == base.graphics[1:]
    assert updated.stages[0] == stage and updated.stages[1:] == base.stages[1:]
    schema = patch_schema(base)
    properties = schema["properties"]
    assert isinstance(properties, dict)
    assert "sources" not in properties and "canonical" not in properties


@pytest.mark.parametrize(
    "defect", ["wrong-hash", "unknown-beat", "no-change", "duplicate-shape", "arbitrary-field"]
)
def test_patch_rejects_unsafe_or_nonexistent_edits(ce_spec: LessonSpec, defect: str) -> None:
    """A proposal cannot target another draft or bypass the typed lesson boundary."""
    base = AuthorLessonSpec.model_validate(ce_spec.model_dump())
    patch = LessonPatch(
        base_sha256=digest_spec(base), parts=[], graphics=[], stages=[], teaching=None, notes=[]
    )
    if defect == "wrong-hash":
        patch.base_sha256 = "0" * 64
    elif defect == "unknown-beat":
        patch.stages = [StageEdit(beat_id="unknown", stage=base.stages[0])]
    elif defect == "duplicate-shape":
        patch.graphics = [base.graphics[0], base.graphics[0]]
    if defect == "arbitrary-field":
        import json

        payload = patch.model_dump(mode="json")
        payload["sources"] = []
        raw = json.dumps(payload)
    else:
        raw = patch.model_dump_json()
    with pytest.raises(ValueError):
        apply_revision(raw, base, "new-test-revision")
