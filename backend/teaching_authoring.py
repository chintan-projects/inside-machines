"""Small shared authoring helpers for safe causal illustrations."""

from .contracts import Part
from .seed_geometry import part
from .teaching_contracts import Change, Pose


class Drawing:
    """Collect original primitives with stable identities and deterministic layers."""

    def __init__(self, prefix: str) -> None:
        """Give each beat its own geometry namespace."""
        self.prefix = prefix
        self.parts: list[Part] = []

    def box(self, name: str, x: float, y: float, w: float, h: float, fill: str = "#d7e1dc") -> str:
        """Add a physical surface or a clearly declared schematic region."""
        return self._add(
            part(
                self.prefix + name,
                name.replace("-", " "),
                "A schematic teaching surface, not an operating measurement.",
                "box",
                x,
                y,
                w,
                h,
                color=fill,
                stroke="#526b63",
            )
        )

    def dot(self, name: str, x: float, y: float, r: float, fill: str = "#72a9ad") -> str:
        """Add a qualitative fluid/heat marker, never an actual molecule count."""
        return self._add(
            part(
                self.prefix + name,
                name.replace("-", " "),
                "Qualitative state marker; size and count are illustrative.",
                "ellipse",
                x - r,
                y - r,
                2 * r,
                2 * r,
                color=fill,
                stroke=fill,
            )
        )

    def text(self, name: str, value: str, x: float, y: float, size: float = 32) -> str:
        """Add short legible labels to the drawing itself."""
        return self._add(
            part(
                self.prefix + name,
                name.replace("-", " "),
                "A label identifying the concept represented in this teaching view.",
                "text",
                x,
                y,
                0,
                size,
                color="#29383d",
                label=value,
            )
        )

    def line(self, name: str, points: list[list[float]], color: str = "#cf7846", width: float = 5) -> str:
        """Add a connected path with real termini."""
        return self._add(
            part(
                self.prefix + name,
                name.replace("-", " "),
                "A qualitative path with direction described by its label.",
                "path",
                points[0][0],
                points[0][1],
                width,
                0,
                points=points,
                stroke=color,
            )
        )

    def arrow(self, name: str, x: float, y: float, length: float, color: str = "#cf7846") -> str:
        """A closed arrow has an unambiguous direction without depending on color."""
        points = [
            [x, y - 7],
            [x + length - 22, y - 7],
            [x + length - 22, y - 21],
            [x + length, y],
            [x + length - 22, y + 21],
            [x + length - 22, y + 7],
            [x, y + 7],
        ]
        return self._add(
            part(
                self.prefix + name,
                name.replace("-", " "),
                "An illustrative transfer arrow, not a measured flow rate.",
                "polygon",
                x,
                y - 21,
                length,
                42,
                points=points,
                color=color,
                stroke=color,
            )
        )

    def _add(self, item: Part) -> str:
        item.layer = len(self.parts)
        self.parts.append(item)
        return item.id


def transition(
    target: str, after: Pose, before: Pose | None = None, *, via: list[Pose] | None = None
) -> Change:
    """Keep all causal outcomes in the authored data rather than renderer code."""
    return Change(target=target, before=before or Pose(), after=after, via=via or [])
