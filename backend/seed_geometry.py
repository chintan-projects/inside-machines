"""Small authoring helpers for original schematic starter lessons."""

from typing import Literal

from .contracts import Motion, Part, Stage


def motion(
    stage: int,
    kind: Literal["rotate", "translate", "pulse", "flow"],
    amount: float = 0,
    axis: Literal["x", "y"] = "x",
) -> Motion:
    """Author one bounded keyframe in the same contract used by generated lessons."""
    return Motion(stage=stage, kind=kind, amount=amount, axis=axis)


def part(
    id: str,
    name: str,
    description: str,
    shape: Literal["box", "ellipse", "ring", "path", "polygon", "text"],
    x: float,
    y: float,
    w: float,
    h: float,
    color: str = "#d7e1e6",
    stroke: str = "#526d7b",
    *,
    points: list[list[float]] | None = None,
    label: str = "",
    layer: int = 10,
    motions: list[Motion] | None = None,
) -> Part:
    """Create explicit safe geometry, never executable renderer instructions."""
    return Part(
        id=id,
        name=name,
        description=description,
        shape=shape,
        x=x,
        y=y,
        w=w,
        h=h,
        color=color,
        stroke=stroke,
        points=points or [],
        label=label,
        layer=layer,
        motion=motions or [],
    )


def stage(title: str, explanation: str, cause: str, ids: list[str], *, narration: str | None = None) -> Stage:
    """Keep authored teaching text and narration synchronized by default."""
    return Stage(
        title=title,
        explanation=explanation,
        narration=narration or explanation,
        duration=12,
        parts=ids,
        cause=cause,
    )
