"""Original section drawings: bounded geometry, not executable model output."""

import math

from .contracts import Part
from .seed_geometry import part
from .teaching_authoring import Drawing, transition
from .teaching_contracts import Change, Pose

INK = "#354b65"
SHELL = "#506984"
LIGHT = "#c8d7e8"
PAPER = "#f6f9fc"
AIR = "#2676df"
DUST = "#c5823c"


class Section(Drawing):
    """A tiny authoring vocabulary shared by scene data and the video renderer."""

    def solid(self, name: str, points: list[list[float]], fill: str) -> str:
        """Author a filled section surface with a physical boundary."""
        xs, ys = [p[0] for p in points], [p[1] for p in points]
        return self._add(
            part(
                self.prefix + name,
                name.replace("-", " "),
                "A sectioned component in a generic bagged vacuum, not exact manufacturing geometry.",
                "polygon",
                min(xs),
                min(ys),
                max(xs) - min(xs),
                max(ys) - min(ys),
                color=fill,
                stroke=INK,
                points=points,
            )
        )

    def oval(self, name: str, x: float, y: float, w: float, h: float, fill: str) -> str:
        """A shaded disk or shaft end; all occlusion follows authoring order."""
        return self._add(
            part(
                self.prefix + name,
                name.replace("-", " "),
                "A physical surface shown in a qualitative cutaway.",
                "ellipse",
                x,
                y,
                w,
                h,
                color=fill,
                stroke=INK,
            )
        )

    def surface(self, name: str, x: float, y: float, w: float, h: float, fill: str) -> str:
        """A small filled casing face, bearing or collar."""
        id = self.box(name, x, y, w, h, fill)
        self.parts[-1].stroke = INK
        return id

    def stream(self, name: str, x: float, y: float, length: float) -> str:
        """A thin directional marker fits inside the illustrated open passage."""
        return self.solid(
            name,
            [
                [x, y - 3],
                [x + length - 13, y - 3],
                [x + length - 13, y - 10],
                [x + length, y],
                [x + length - 13, y + 10],
                [x + length - 13, y + 3],
                [x, y + 3],
            ],
            AIR,
        )


def fan_section() -> tuple[Section, list[Change]]:
    """Show the drive shaft and impeller inside a bounded fan housing."""
    d = Section("vf-")
    d.oval("shadow", 212, 449, 570, 28, "#e1e9f2")
    d.surface("outlet-back", 360, 133, 236, 68, SHELL)
    d.surface("outlet-passage", 375, 143, 240, 40, "#e7f1fc")
    d.oval("housing-depth", 242, 164, 310, 284, "#415870")
    d.oval("housing-rim", 222, 151, 310, 284, LIGHT)
    d.oval("air-chamber", 238, 167, 278, 252, "#e6f0fb")
    d.surface("shaft", 402, 278, 223, 18, "#9faec0")
    d.surface("bearing", 529, 262, 22, 50, "#667e98")
    d.surface("motor-back", 618, 231, 119, 117, "#394f69")
    d.surface("motor-core", 596, 220, 119, 117, "#829bb5")
    for i in range(5):
        d.surface(f"winding-{i}", 609 + i * 18, 228, 9, 101, "#c89968")
    d.surface("motor-end", 710, 235, 20, 100, "#536d88")
    d.surface("motor-foot", 603, 337, 124, 24, "#506984")
    d.oval("impeller-back", 279, 206, 194, 174, "#8198ae")
    changes: list[Change] = []
    for i in range(7):
        a = i * 2 * math.pi / 7
        points = [
            [376 + r * math.cos(a + k), 293 + r * math.sin(a + k)]
            for r, k in [(28, 0), (81, 0.20), (87, 0.48), (49, 0.27), (28, 0.25)]
        ]
        id = d.solid(f"vane-{i}", points, "#e9eff6")
        # Each vane rotates about the common shaft, rather than its own bounding box.
        p = d.parts[-1]
        p.x, p.y, p.w, p.h = 276, 193, 200, 200
        changes.append(transition(id, Pose(angle=145)))
    d.oval("hub", 347, 264, 58, 58, "#536d88")
    d.oval("inlet-eye", 358, 275, 36, 36, "#263e59")
    incoming = d.stream("air-in", 110, 293, 130)
    outgoing = d.stream("air-out", 474, 163, 132)
    changes.extend(
        [
            transition(incoming, Pose(x=100), Pose(opacity=0.25)),
            transition(outgoing, Pose(x=105), Pose(opacity=0.25)),
        ]
    )
    d.text("fan-label", "Fan", 280, 460, 42)
    d.text("motor-label", "Motor", 608, 378, 42)
    d.text("in-label", "Air in", 68, 217, 40)
    d.text("out-label", "Air out", 580, 70, 40)
    d.line("out-anchor", [[621, 119], [621, 146]], INK, 2)
    return d, changes


def inlet_section() -> tuple[Section, list[Change]]:
    """A floor nozzle has a visible opening; arrows travel through its air space."""
    d = Section("vi-")
    d.surface("floor-edge", 50, 425, 800, 25, "#c6b8a4")
    d.surface("floor-top", 50, 419, 800, 7, "#e0d6c7")
    for i in range(4):
        x = 125 + i * 190
        d.line(f"floor-seam-{i}", [[x, 425], [x + 12, 448]], "#a99986", 2)
    d.solid(
        "nozzle-depth", [[273, 386], [352, 280], [505, 280], [615, 386], [615, 407], [273, 407]], "#3d536e"
    )
    d.solid("nozzle-shell", [[246, 371], [333, 264], [493, 264], [592, 371], [592, 394], [246, 394]], LIGHT)
    d.solid("nozzle-passage", [[276, 394], [365, 298], [464, 298], [560, 394]], "#edf5ff")
    d.surface("hose-back", 385, 139, 77, 143, "#5c738d")
    d.surface("hose-air-space", 400, 139, 47, 159, "#e5effb")
    d.surface("hose-cuff", 382, 254, 83, 20, "#9fb2c7")
    for i in range(4):
        d.surface(f"hose-rib-{i}", 380, 151 + i * 24, 87, 8, "#97acc3")
    d.surface("left-foot", 246, 388, 32, 14, "#344a61")
    d.surface("right-foot", 559, 388, 33, 14, "#344a61")
    changes: list[Change] = []
    for i in range(3):
        air = d.stream(f"air-{i}", 118 + i * 60, 416, 24)
        changes.append(
            transition(
                air,
                Pose(x=293 - i * 60, y=-176 - i * 40, angle=-90),
                via=[Pose(x=245 - i * 44, y=-32 - i * 25), Pose(x=293 - i * 60, y=-110 - i * 40, angle=-90)],
            )
        )
        dust = d.dot(f"dust-{i}", 170 + i * 69, 422, 6 + i * 2, DUST)
        changes.append(
            transition(
                dust,
                Pose(x=252 - i * 69, y=-184 - i * 30),
                via=[Pose(x=190 - i * 53, y=-37 - i * 25), Pose(x=250 - i * 69, y=-110 - i * 40)],
            )
        )
    d.text("room-label", "Room air", 70, 91, 42)
    d.text("hose-label", "To the bag", 515, 163, 42)
    d.line("hose-anchor", [[500, 203], [448, 203]], INK, 2)
    d.text("nozzle-label", "Floor nozzle", 300, 466, 42)
    d.text("gap-label", "Open gap", 650, 315, 40)
    d.line("gap-anchor", [[668, 361], [617, 406]], INK, 2)
    return d, changes


def bag_section() -> tuple[Section, list[Change]]:
    """Air traverses the porous wall; dust remains inside, not in a closed box."""
    d = Section("vb-")
    d.surface("case-back", 160, 129, 600, 320, "#bfcedf")
    d.surface("case-inside", 174, 143, 570, 292, "#e8eff7")
    d.surface("intake-tube", 55, 212, 169, 53, "#718ba6")
    d.surface("intake-passage", 55, 225, 174, 26, "#e9f3ff")
    d.solid("bag", [[225, 181], [395, 173], [434, 207], [452, 405], [228, 400]], "#ead9bc")
    d.solid("bag-inside", [[242, 199], [383, 191], [414, 218], [430, 383], [246, 379]], "#fff5e3")
    d.surface("bag-neck", 207, 205, 32, 68, "#c9b18a")
    d.line("bag-fold", [[267, 201], [263, 357], [309, 379]], "#cdb589", 3)
    d.line("bag-seam", [[384, 197], [408, 227], [423, 373]], "#bca177", 3)
    pores: list[str] = []
    for i in range(5):
        pores.append(d.dot(f"pore-{i}", 417 + i * 6, 235 + i * 29, 5, "#f6f9fc"))
    d.surface("fan-partition", 592, 170, 16, 243, "#8da5be")
    d.oval("fan-housing", 541, 235, 132, 132, "#4a6480")
    d.oval("fan", 554, 248, 106, 106, "#a4bbd2")
    vanes = d.solid(
        "impeller",
        [
            [607, 258],
            [622, 284],
            [649, 288],
            [625, 306],
            [629, 335],
            [605, 319],
            [579, 335],
            [585, 307],
            [564, 288],
            [593, 283],
        ],
        "#eaf1f8",
    )
    d.oval("fan-hub", 595, 289, 24, 24, "#526e8b")
    d.surface("outlet-space", 675, 277, 135, 48, "#e8eff7")
    for i in range(3):
        d.surface(f"outlet-louver-{i}", 746 + i * 13, 278, 5, 46, "#7891ac")
    changes = [transition(vanes, Pose(angle=140))]
    for i in range(3):
        air = d.stream(f"air-{i}", 75 + i * 40, 236, 49)
        changes.append(
            transition(
                air, Pose(x=640 + i * 20, y=66), via=[Pose(x=250 + i * 20), Pose(x=410 + i * 20, y=66)]
            )
        )
        dust = d.dot(f"dust-{i}", 103 + i * 34, 237, 7, DUST)
        changes.append(
            transition(dust, Pose(x=218 - i * 22, y=120 + i * 7), via=[Pose(x=196 - i * 22, y=18)])
        )
    d.text("bag-label", "Porous bag", 218, 68, 42)
    d.text("fan-label", "Fan", 572, 371, 42)
    d.text("out-label", "Air out", 661, 182, 40)
    d.text("dust-label", "Dirt stays", 230, 465, 42)
    return d, changes


def overview() -> list[Part]:
    """A connected canister locator, separate from the causal close-ups."""
    d = Section("")
    d.surface("chassis", 351, 218, 403, 210, SHELL)
    d.solid("lid", [[351, 218], [396, 179], [790, 179], [754, 218]], "#99afc6")
    d.solid("side", [[754, 218], [790, 179], [790, 395], [754, 428]], "#3d536d")
    d.surface("cutaway", 370, 237, 364, 169, "#e7eff8")
    d.surface("handle", 478, 158, 158, 24, "#4b627d")
    d.surface("handle-gap", 505, 168, 103, 18, PAPER)
    for x in (414, 695):
        d.oval(f"wheel-{x}", x - 34, 397, 68, 68, "#263d54")
        d.oval(f"hub-{x}", x - 19, 412, 38, 38, "#899fb6")
    d.line(
        "hose",
        [[353, 285], [303, 285], [282, 163], [244, 125], [192, 124], [152, 165], [152, 379]],
        SHELL,
        25,
    )
    d.line(
        "hose-light",
        [[353, 282], [303, 282], [282, 160], [244, 122], [192, 121], [152, 162], [152, 379]],
        "#8fa6bf",
        10,
    )
    d.solid("nozzle", [[102, 376], [184, 376], [221, 413], [75, 413]], "#829bb4")
    d.surface("nozzle-lip", 75, 413, 146, 10, "#3c536d")
    d.solid("bag", [[394, 256], [523, 247], [548, 386], [397, 386]], "#e7d4b2")
    d.line("bag-fold", [[413, 269], [417, 371], [475, 382]], "#c4aa7f", 3)
    d.oval("fan", 601, 271, 95, 95, "#9fb7d0")
    d.solid(
        "vanes",
        [[648, 281], [663, 310], [686, 318], [658, 330], [646, 356], [633, 331], [610, 317], [637, 307]],
        "#e9eff6",
    )
    d.surface("motor", 681, 304, 41, 56, "#c38e59")
    d.text("label-fan", "Fan", 588, 81, 40)
    d.line("fan-anchor", [[619, 126], [649, 270]], INK, 2)
    d.text("label-bag", "Porous bag", 345, 468, 40)
    d.line("bag-anchor", [[459, 452], [459, 386]], INK, 2)
    d.text("label-nozzle", "Nozzle", 72, 466, 40)
    d.line("nozzle-anchor", [[134, 452], [145, 424]], INK, 2)
    return d.parts
