"""Compact authoring DTO expands into the unchanged public lesson contract."""

import json
from copy import deepcopy
from typing import cast

from pydantic import Field, TypeAdapter

from .contracts import AuthorLessonSpec, LessonSpec, Part, PartShape, StrictModel
from .teaching_contracts import Pose


class CompactPose(StrictModel):
    """Six ordered numbers retain the exact transform; fill remains explicit."""

    values: list[float] = Field(min_length=6, max_length=6)
    fill: str

    def expand(self) -> Pose:
        """Delegate all pose bounds to the shared mechanism contract."""
        x, y, sx, sy, angle, opacity = self.values
        return Pose(x=x, y=y, sx=sx, sy=sy, angle=angle, opacity=opacity, fill=self.fill)


def _poses(document: dict[str, object], *, expand: bool) -> None:
    """Translate only declared beat/scenario changes, preserving all other data."""
    teaching = document.get("teaching")
    if not isinstance(teaching, dict):
        raise ValueError("Compact authoring requires teaching data")
    for key in ("beats", "scenarios"):
        entries = teaching.get(key)
        if not isinstance(entries, list):
            raise ValueError("Compact authoring requires beats and scenarios")
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("changes"), list):
                raise ValueError("Compact authoring requires declared changes")
            for change in entry["changes"]:
                if not isinstance(change, dict):
                    raise ValueError("Each change must be an object")

                def convert(value: object) -> dict[str, object]:
                    if expand:
                        return CompactPose.model_validate(value).expand().model_dump(mode="json")
                    pose = Pose.model_validate(value)
                    return CompactPose(
                        values=[pose.x, pose.y, pose.sx, pose.sy, pose.angle, pose.opacity], fill=pose.fill
                    ).model_dump(mode="json")

                for field in ("before", "after"):
                    change[field] = convert(change.get(field))
                via = change.get("via", [])
                if not isinstance(via, list):
                    raise ValueError("Intermediate poses must be an array")
                change["via"] = [convert(p) for p in via]


class CompactPart(StrictModel):
    """Remove repeated coordinate keys and static-motion boilerplate, not detail."""

    id: str
    name: str
    description: str
    shape: PartShape
    box: list[float] = Field(min_length=4, max_length=4)
    paint: list[str] = Field(min_length=2, max_length=2)
    points: list[list[float]]
    label: str
    layer: int

    def expand(self) -> Part:
        """Apply every original geometry/identity constraint at the domain boundary."""
        x, y, w, h = self.box
        color, stroke = self.paint
        return Part.model_validate(
            {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "shape": self.shape,
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "color": color,
                "stroke": stroke,
                "points": self.points,
                "label": self.label,
                "layer": self.layer,
                "motion": [],
            }
        )


def author_schema() -> dict[str, object]:
    """Compose transport geometry with the single shared lesson/storyboard schema."""
    schema = deepcopy(AuthorLessonSpec.model_json_schema())
    definitions = cast(dict[str, object], schema["$defs"])
    definitions.pop("Part")
    definitions.pop("Motion", None)
    definitions["CompactPart"] = CompactPart.model_json_schema()
    definitions["Pose"] = CompactPose.model_json_schema()
    properties = cast(dict[str, dict[str, object]], schema["properties"])
    for field in ("parts", "graphics"):
        properties[field]["items"] = {"$ref": "#/$defs/CompactPart"}
    return schema


def expand_author(raw: str | bytes) -> AuthorLessonSpec:
    """Parse bounded DTOs then validate the complete, ordinary version-2 lesson."""
    data: object = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Author output must be an object")
    document = cast(dict[str, object], data)
    for field in ("parts", "graphics"):
        compact = TypeAdapter(list[CompactPart]).validate_python(document.get(field))
        document[field] = [p.expand().model_dump(mode="json") for p in compact]
    _poses(document, expand=True)
    return AuthorLessonSpec.model_validate(document)


def compact_author(spec: LessonSpec) -> dict[str, object]:
    """Losslessly encode a static CE draft for fixtures/equivalent provider evals."""
    document = spec.model_dump(mode="json")
    for field, parts in (("parts", spec.parts), ("graphics", spec.graphics)):
        if any(p.motion for p in parts):
            raise ValueError("Compact authoring cannot discard existing motion")
        document[field] = [
            CompactPart(
                id=p.id,
                name=p.name,
                description=p.description,
                shape=p.shape,
                box=[p.x, p.y, p.w, p.h],
                paint=[p.color, p.stroke],
                points=p.points,
                label=p.label,
                layer=p.layer,
            ).model_dump(mode="json")
            for p in parts
        ]
    _poses(document, expand=False)
    return document
