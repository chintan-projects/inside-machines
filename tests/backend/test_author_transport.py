"""Compact transport preserves geometry/meaning and every public boundary check."""

import json

import pytest
from pydantic import ValidationError

from backend.author_transport import CompactPart, author_schema, compact_author, expand_author
from backend.contracts import AuthorLessonSpec, LessonSpec, Motion, Part
from backend.provider_schema import openai_schema
from backend.quality import require_learning_quality
from backend.starters import digest_spec


def test_lossless_compact_geometry_and_schema(ce_spec: LessonSpec) -> None:
    """Save transport bytes without dropping painter order, paths, labels or claims."""
    payload = compact_author(ce_spec)
    expanded = expand_author(json.dumps(payload))
    assert digest_spec(expanded) == digest_spec(ce_spec)
    require_learning_quality(expanded)
    assert len(json.dumps(payload, separators=(",", ":"))) < len(ce_spec.model_dump_json())
    original = AuthorLessonSpec.model_json_schema()
    schema = openai_schema(author_schema())
    assert AuthorLessonSpec.model_json_schema() == original
    definitions = schema["$defs"]
    assert isinstance(definitions, dict)

    def refs(node: object) -> None:
        if isinstance(node, dict):
            if "$ref" in node:
                assert str(node["$ref"]).split("/")[-1] in definitions
            for value in node.values():
                refs(value)
        elif isinstance(node, list):
            for value in node:
                refs(value)

    refs(schema)


@pytest.mark.parametrize("defect", ["box", "color", "bounds", "pose-bounds", "extra"])
def test_compact_data_cannot_bypass_original_checks(ce_spec: LessonSpec, defect: str) -> None:
    """Provider transport convenience never relaxes validated lesson constraints."""
    payload = compact_author(ce_spec)
    parts = payload["parts"]
    assert isinstance(parts, list)
    part = parts[0]
    if defect == "box":
        part["box"] = [0, 1]
    elif defect == "color":
        part["paint"] = ["javascript:bad", "#000000"]
    elif defect == "bounds":
        part["box"][0] = 901
    elif defect == "pose-bounds":
        teaching = payload["teaching"]
        assert isinstance(teaching, dict)
        teaching["beats"][0]["changes"][0]["after"]["values"][2] = -1
    else:
        payload["arbitrary_code"] = "not permitted"
    with pytest.raises(ValidationError):
        expand_author(json.dumps(payload))


def test_compact_encoder_refuses_to_erase_legacy_motion(ce_spec: LessonSpec) -> None:
    """Historical motion needs its historical protocol, not a lossy conversion."""
    ce_spec.parts[0].motion = [Motion(stage=0, kind="rotate", amount=90, axis="x")]
    with pytest.raises(ValueError, match="discard"):
        compact_author(ce_spec)


def test_unused_paint_and_polygon_bounds_have_explicit_compiler_meaning(ce_spec: LessonSpec) -> None:
    """No visible paint is invented; zero boxes derive an actual geometric center."""
    from backend.teaching_svg import graphic_svg

    for shape in ("path", "ring", "text"):
        reference = Part.model_validate(
            dict(
                id="sample",
                name="Sample",
                description="Synthetic test shape",
                shape=shape,
                x=100,
                y=100,
                w=4,
                h=32,
                color="#123456",
                stroke="#234567",
                points=[[100, 100], [150, 150]],
                label="Sample",
                layer=0,
                motion=[],
            )
        )
        paints = [reference.color, reference.stroke]
        paints[1 if shape == "text" else 0] = ""
        expanded = CompactPart(
            id=reference.id,
            name=reference.name,
            description=reference.description,
            shape=reference.shape,
            box=[100, 100, 4, 32],
            paint=paints,
            points=reference.points,
            label=reference.label,
            layer=0,
        ).expand()
        assert graphic_svg(expanded, None, 0) == graphic_svg(reference, None, 0)
    polygon = CompactPart(
        id="rotor",
        name="Rotor",
        description="Synthetic test rotor",
        shape="polygon",
        box=[0, 0, 0, 0],
        paint=["#123456", "#123456"],
        points=[[100, 100], [300, 100], [300, 300], [100, 300]],
        label="",
        layer=0,
    )
    part = polygon.expand()
    assert (part.x, part.y, part.w, part.h) == (100, 100, 200, 200)
    polygon.box = [150, 150, 0, 0]
    assert polygon.expand().x == 150  # An explicit nonzero pivot is never rewritten.
