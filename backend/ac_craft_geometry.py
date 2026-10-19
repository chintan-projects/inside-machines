"""Shared declarative AC cutaway: hardware, tubing and permanent component names."""

import math

from .contracts import Part
from .seed_geometry import motion, part


def ac_parts() -> list[Part]:
    """Build the geometry once as safe data for both SVG and video rendering."""
    pieces: list[Part] = []

    def box(id: str, x: float, y: float, w: float, h: float, color: str, layer: int = 3) -> None:
        pieces.append(
            part(
                id,
                id.replace("-", " ").capitalize(),
                "A structural detail of the cutaway housing.",
                "box",
                x,
                y,
                w,
                h,
                color=color,
                stroke="#8b9da5",
                layer=layer,
            )
        )

    def line(
        id: str,
        name: str,
        text: str,
        points: list[list[float]],
        color: str,
        width: int = 6,
        flow: bool = False,
        layer: int = 10,
    ) -> None:
        pieces.append(
            part(
                id,
                name,
                text,
                "path",
                points[0][0],
                points[0][1],
                width,
                0,
                points=points,
                stroke=color,
                layer=layer,
                motions=[motion(i, "flow") for i in range(6)] if flow else [],
            )
        )

    def label(id: str, text: str, x: float, y: float, size: int = 38, color: str = "#223942") -> None:
        pieces.append(
            part(
                id,
                text,
                "A visible label identifies this part in the drawing.",
                "text",
                x,
                y,
                0,
                size,
                color=color,
                label=text,
                layer=30,
            )
        )

    label("room-heading", "Inside your room", 64, 8, 32)
    label("outdoor-heading", "Outside", 510, 8, 32)
    # Four-tone faces, mounting feet, cutaway rims, coil fins and connected fittings.
    for prefix, x, y, w, h in [("indoor", 75, 158, 309, 178), ("outdoor", 510, 165, 295, 231)]:
        box(prefix + "-back", x, y, w, h, "#dce6e9", 0)
        pieces.append(
            part(
                prefix + "-side",
                "Housing side",
                "The side face shows the depth of the opened cabinet.",
                "polygon",
                x + w,
                y,
                20,
                h,
                points=[[x + w, y], [x + w + 20, y - 15], [x + w + 20, y + h - 15], [x + w, y + h]],
                color="#9eafb8",
                layer=0,
            )
        )
        pieces.append(
            part(
                prefix + "-top",
                "Housing top",
                "The top face joins the cabinet rim.",
                "polygon",
                x,
                y - 15,
                w + 20,
                15,
                points=[[x, y], [x + 20, y - 15], [x + w + 20, y - 15], [x + w, y]],
                color="#f8fafb",
                layer=1,
            )
        )
        box(prefix + "-recess", x + 9, y + 9, w - 18, h - 18, "#f5f8f9", 2)
        box(prefix + "-rail", x + 8, y + h - 13, w - 16, 5, "#a6b6bf", 4)
        for j, dx in enumerate((23, w - 43)):
            box(f"{prefix}-foot-{j}", x + dx, y + h, 24, 8, "#566974", 1)
        for j, (dx, dy) in enumerate(((6, 6), (w - 10, 6), (6, h - 10), (w - 10, h - 10))):
            pieces.append(
                part(
                    f"{prefix}-screw-{j}",
                    "Panel screw",
                    "A fixing at the edge of the cabinet rim.",
                    "ellipse",
                    x + dx,
                    y + dy,
                    4,
                    4,
                    color="#647b86",
                    layer=8,
                )
            )
    # Fins belong to the coil support plates; refrigerant stays in the heavy tube.
    for prefix, x, y, h in [("indoor", 121, 185, 115), ("outdoor", 699, 196, 159)]:
        box(prefix + "-coil-plate", x - 12, y - 4, 104, h + 8, "#d9e5e8", 4)
        for j in range(9):
            box(f"{prefix}-fin-{j}", x - 6 + j * 11, y, 2, h, "#a7c2cb", 5)
    line(
        "evaporator",
        "Indoor coil · evaporator",
        "Inside this coil, low-pressure refrigerant absorbs room heat and boils. Room air passes around the tube, never inside it.",
        [
            [147, 310],
            [147, 291],
            [201, 291],
            [201, 268],
            [134, 268],
            [134, 245],
            [201, 245],
            [201, 222],
            [134, 222],
            [134, 198],
            [212, 198],
        ],
        "#237f9e",
        9,
        True,
    )
    line(
        "suction",
        "Low-pressure vapor",
        "Vapor leaving the indoor coil travels to the compressor through a sealed tube.",
        [[212, 198], [424, 198], [424, 348], [559, 348]],
        "#448c9a",
        8,
        True,
    )
    # Compressor is a sealed motor-driven pump; this exterior view does not invent its internals.
    box("compressor-mount", 544, 366, 70, 8, "#9aabb3", 6)
    pieces.append(
        part(
            "compressor",
            "Compressor",
            "An electric motor drives a pump inside this sealed shell. It takes in low-pressure vapor and delivers hotter, high-pressure vapor.",
            "box",
            552,
            288,
            55,
            78,
            color="#5f7885",
            stroke="#425966",
            layer=9,
            motions=[motion(2, "pulse")],
        )
    )
    pieces.append(
        part(
            "compressor-dome",
            "Compressor shell",
            "A rounded cover closes the compressor's sealed housing.",
            "ellipse",
            552,
            277,
            55,
            22,
            color="#92aab7",
            layer=10,
        )
    )
    box("compressor-seam", 552, 340, 55, 3, "#46606c", 10)
    line(
        "power",
        "Electrical work",
        "Electricity drives the compressor. This added energy also leaves as heat outdoors.",
        [[528, 363], [528, 322], [552, 322]],
        "#6b7780",
        3,
    )
    line(
        "discharge",
        "Hot high-pressure vapor",
        "The compressor outlet carries hotter vapor to the outdoor coil.",
        [[579, 278], [579, 204], [711, 204]],
        "#c86c4c",
        8,
        True,
    )
    line(
        "condenser",
        "Outdoor coil · condenser",
        "Hot refrigerant releases heat to outdoor air and condenses into a liquid, while staying at high pressure.",
        [
            [711, 204],
            [772, 204],
            [772, 228],
            [711, 228],
            [711, 253],
            [772, 253],
            [772, 279],
            [711, 279],
            [711, 306],
            [772, 306],
            [772, 344],
            [727, 344],
        ],
        "#c57948",
        9,
        True,
    )
    line(
        "liquid-line",
        "High-pressure liquid",
        "Liquid returns toward the expansion valve through a sealed tube.",
        [[727, 344], [727, 423], [389, 423]],
        "#b68b51",
        8,
        True,
    )
    pieces.append(
        part(
            "expansion",
            "Expansion valve",
            "This restriction meters refrigerant into the low-pressure side. Pressure drops and some liquid flashes into vapor, creating a cold mixture.",
            "polygon",
            350,
            407,
            39,
            32,
            points=[[350, 407], [370, 423], [389, 407], [389, 439], [370, 423], [350, 439]],
            color="#adbdc5",
            stroke="#425e6d",
            layer=12,
            motions=[motion(4, "pulse")],
        )
    )
    line(
        "return-line",
        "Cold low-pressure mixture",
        "The cold liquid-and-vapor mixture returns to the indoor coil, where it can absorb more room heat.",
        [[350, 423], [147, 423], [147, 310]],
        "#237f9e",
        8,
        True,
    )
    # Fan blades rotate about a real hub, and sit inside their guards.
    for prefix, x, y, r in [("blower", 293, 247, 42), ("fan", 651, 266, 38)]:
        pieces.append(
            part(
                prefix + "-ring",
                "Fan guard",
                "A ring surrounds the fan, with a central motor hub.",
                "ring",
                x - r,
                y - r,
                r * 2,
                r * 2,
                stroke="#8da4af",
                layer=7,
            )
        )
        blade_points: list[list[float]] = []
        for j in range(12):
            a = j * math.pi / 6
            radius = r - 5 if j % 2 == 0 else r * 0.27
            blade_points.append([x + radius * math.cos(a), y + radius * math.sin(a)])
        pieces.append(
            part(
                prefix,
                "Indoor blower" if prefix == "blower" else "Outdoor fan",
                "The fan moves air over a coil. It does not send air between the indoor and outdoor units.",
                "polygon",
                x - r,
                y - r,
                r * 2,
                r * 2,
                points=blade_points,
                color="#91aab6",
                layer=8,
                motions=[motion(i, "rotate", 360) for i in range(6)],
            )
        )
        pieces.append(
            part(
                prefix + "-hub",
                "Fan motor hub",
                "The blades attach to this central hub.",
                "ellipse",
                x - 8,
                y - 8,
                16,
                16,
                color="#526f7d",
                layer=11,
            )
        )
    line(
        "warm-air",
        "Room air entering",
        "Room air passes over the outside of the indoor coil and gives up heat.",
        [[31, 216], [97, 216], [115, 232]],
        "#82959b",
        5,
        True,
        15,
    )
    line(
        "cool-air",
        "Cooler air returning",
        "The blower returns the same room air after heat has been removed.",
        [[296, 301], [278, 357], [70, 357], [39, 341]],
        "#5798ab",
        5,
        True,
        15,
    )
    line(
        "outdoor-air",
        "Outdoor air",
        "The outdoor fan carries the released heat away into outdoor air.",
        [[796, 282], [856, 282]],
        "#87999e",
        5,
        True,
        15,
    )
    # Heat has its own glyph and color: it is energy crossing a wall, not another pipe.
    line(
        "absorbed-heat",
        "Heat entering the refrigerant",
        "Heat passes from room air through the tube wall into colder refrigerant.",
        [[79, 273], [106, 273], [127, 253]],
        "#b68435",
        4,
        True,
        16,
    )
    line(
        "released-heat",
        "Heat leaving outdoors",
        "The outdoor coil releases the heat removed indoors plus compressor work.",
        [[769, 257], [826, 232], [856, 232]],
        "#b68435",
        4,
        True,
        16,
    )
    label("label-evaporator", "1 · Indoor coil", 63, 57)
    label("name-evaporator", "Evaporator · absorbs heat", 63, 114, 21, "#526d78")
    label("label-condenser", "3 · Outdoor coil", 510, 57)
    label("name-condenser", "Condenser · releases heat", 541, 114, 21, "#526d78")
    label("label-compressor", "2 · Compressor", 530, 456)
    label("label-expansion", "4 · Expansion valve", 65, 456)
    for id, points in [
        ("evaporator", [[183, 142], [183, 176]]),
        ("condenser", [[737, 142], [737, 186]]),
        ("compressor", [[579, 450], [579, 377]]),
        ("expansion", [[307, 450], [370, 443]]),
    ]:
        line(
            "leader-" + id,
            "Component label anchor",
            "This line connects a component name to its physical location.",
            [[float(v) for v in pair] for pair in points],
            "#8d9fa6",
            2,
            False,
            25,
        )
    label("heat-in-label", "Heat in", 29, 288, 20, "#946b26")
    label("heat-out-label", "Heat out", 809, 191, 20, "#946b26")
    label("power-label", "Electricity in", 438, 374, 18, "#526d78")
    label("loop-note", "Refrigerant stays inside the sealed tubing.", 163, 514, 22, "#526d78")
    return pieces
