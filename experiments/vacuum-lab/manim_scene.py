"""Actual Manim render of the shared, precomputed vacuum comparison state.

Local authored spike: consumes immutable frame data, never calls a provider or
publishes a lesson. Adapter geometry is not a numerical fluid model.
"""

import json
import math
import os
from collections.abc import Sequence
from pathlib import Path
from typing import TypedDict, cast

import numpy as np
from manim import (
    Circle,
    Dot,
    Ellipse,
    Line,
    Mobject,
    Polygon,
    Rectangle,
    RoundedRectangle,
    Scene,
    Text,
    ValueTracker,
    VGroup,
    VMobject,
    config,
    linear,
)
from numpy.typing import NDArray

INK = "#172432"
AIR = "#4267d5"
DIRT = "#78513b"
PAPER = "#fbfcfe"
config.background_color = PAPER
config.pixel_width, config.pixel_height = 960, 720
config.frame_width, config.frame_height = 12.8, 9.6
config.frame_rate = 24


class Frame(TypedDict):
    """State exported by the common TypeScript qualitative model."""

    time: float
    beat: int
    angle: float
    blocked: bool
    air: list[float]
    dirt: list[float]


def xy(x: float, y: float) -> NDArray[np.float64]:
    """Convert adapter canvas coordinates into Manim scene coordinates."""
    return np.array([(x - 480) / 75, (360 - y) / 75, 0], dtype=np.float64)


def label(text: str, x: float, y: float, size: float = 32, color: str = INK) -> Text:
    """Use actual vector text; no LaTeX installation or image lettering."""
    return Text(text, font="Arial", font_size=size, color=color).move_to(xy(x, y))


def path(points: Sequence[tuple[float, float]], color: str, width: float) -> VMobject:
    """Draw an explicitly connected passage or semantic route."""
    return VMobject(stroke_color=color, stroke_width=width).set_points_as_corners(
        [xy(x, y) for x, y in points]
    )


def along(points: Sequence[tuple[float, float]], progress: float) -> NDArray[np.float64]:
    """Geometry-only placement of an already computed progress marker."""
    lengths = [math.dist(a, b) for a, b in zip(points[:-1], points[1:], strict=True)]
    remaining = progress * sum(lengths)
    for i, length in enumerate(lengths):
        if remaining <= length:
            ratio = remaining / length if length else 0
            return xy(
                points[i][0] + (points[i + 1][0] - points[i][0]) * ratio,
                points[i][1] + (points[i + 1][1] - points[i][1]) * ratio,
            )
        remaining -= length
    return xy(*points[-1])


class VacuumProof(Scene):
    """An analytical section makes an invisible connected air path visible."""

    def construct(self) -> None:
        """Render real Manim objects and updaters from the shared frame table."""
        source = Path(os.environ["VACUUM_LAB_FRAMES"])
        frames = cast(list[Frame], json.loads(source.read_text()))
        clock = ValueTracker(0)

        def state() -> Frame:
            return frames[min(len(frames) - 1, round(clock.get_value()))]

        # Geometry is a generic exposed section; all jobs operate continuously.
        body = RoundedRectangle(
            width=6.9,
            height=4.0,
            corner_radius=0.55,
            fill_color="#f0f4f8",
            fill_opacity=1,
            stroke_color="#b3c0cc",
            stroke_width=2,
        ).move_to(xy(610, 380))
        self.add(body)
        self.add(Line(xy(372, 522), xy(849, 522), color="#c7d0d9", stroke_width=3))
        for x in (419, 800):
            self.add(Circle(radius=0.22, fill_color=INK, fill_opacity=1, stroke_width=0).move_to(xy(x, 549)))
        self.add(
            RoundedRectangle(
                width=1.4, height=0.28, corner_radius=0.1, stroke_color="#8a9caa", stroke_width=4
            ).move_to(xy(612, 214))
        )

        hose_points = [(153, 532), (153, 400), (196, 335), (280, 335), (358, 380), (410, 380)]
        self.add(path(hose_points, "#798d9d", 24), path(hose_points, "#edf2f7", 16))
        for x, y in [(175, 368), (190, 344), (215, 335), (239, 335), (265, 335), (303, 348), (326, 362)]:
            self.add(Line(xy(x - 3, y - 10), xy(x + 3, y + 10), color="#9eafbd", stroke_width=2))
        self.add(
            Polygon(
                xy(115, 535),
                xy(175, 535),
                xy(193, 558),
                xy(92, 558),
                fill_color="#d4dfe8",
                fill_opacity=1,
                stroke_color="#647d90",
                stroke_width=2,
            )
        )
        self.add(Line(xy(72, 565), xy(310, 565), color="#c7d0d9", stroke_width=2))

        bag = RoundedRectangle(
            width=1.7,
            height=2.5,
            corner_radius=0.2,
            fill_color="#e5dcca",
            fill_opacity=1,
            stroke_color="#938572",
            stroke_width=2,
        ).move_to(xy(476, 402))
        self.add(bag)
        for x in range(424, 535, 13):
            self.add(Line(xy(x, 322), xy(x, 484), color="#c0b49f", stroke_width=1))
        # Air crosses the right porous face; dirt remains upstream of that face.
        for y in range(322, 486, 14):
            self.add(Line(xy(536, y), xy(545, y + 3), color="#938572", stroke_width=2))
        for i in range(14):
            self.add(Dot(xy(440 + (i % 5) * 14, 470 - (i // 5) * 13), radius=0.035, color=DIRT))

        # Fan rotor is seen in a compressed oblique plane, coaxial with its motor.
        self.add(Ellipse(width=0.7, height=1.7, stroke_color="#8d9faf", stroke_width=3).move_to(xy(650, 400)))
        self.add(Line(xy(650, 400), xy(750, 400), color="#4e6578", stroke_width=8))
        self.add(
            RoundedRectangle(
                width=1.1,
                height=0.85,
                corner_radius=0.15,
                fill_color="#c4d1de",
                fill_opacity=1,
                stroke_color="#637b90",
                stroke_width=2,
            ).move_to(xy(758, 400))
        )
        for x in range(730, 792, 12):
            self.add(Line(xy(x, 373), xy(x, 427), color="#8fa4b7", stroke_width=2))
        rotor = VGroup()
        for _i in range(6):
            rotor.add(
                Polygon(
                    xy(650, 400),
                    xy(650, 400),
                    xy(650, 400),
                    fill_color="#6888a3",
                    fill_opacity=1,
                    stroke_color="#35566d",
                    stroke_width=1,
                )
            )

        def update_rotor(group: Mobject) -> None:
            angle = math.radians(state()["angle"])
            for i, blade in enumerate(cast(VGroup, group)):
                a = angle + i * math.tau / 6
                coords = [
                    (650 + 6 * math.cos(a), 400 + 10 * math.sin(a)),
                    (650 + 22 * math.cos(a + 0.2), 400 + 56 * math.sin(a + 0.2)),
                    (650 + 22 * math.cos(a + 0.65), 400 + 56 * math.sin(a + 0.65)),
                ]
                blade.set_points_as_corners([xy(*p) for p in [*coords, coords[0]]])

        rotor.add_updater(update_rotor)
        self.add(rotor, Dot(xy(650, 400), radius=0.075, color=INK))
        route = [
            (75, 552),
            (151, 548),
            (153, 400),
            (196, 335),
            (280, 335),
            (358, 380),
            (450, 380),
            (505, 391),
            (545, 400),
            (650, 400),
            (650, 285),
            (884, 285),
        ]
        dirty_route = [*route[:7], (470, 451)]
        self.add(path(route, "#cbd6f2", 3))
        self.add(Line(xy(844, 270), xy(844, 303), color="#6f8597", stroke_width=3))
        for i in range(12):
            marker = Dot(radius=0.06, color=AIR)

            def update_air(dot: Mobject, *, index: int = i) -> None:
                values = state()["air"]
                dot.set_opacity(1 if index < len(values) else 0)
                if index < len(values):
                    dot.move_to(along(route, values[index]))

            marker.add_updater(update_air)
            self.add(marker)
        for i in range(5):
            speck = Rectangle(width=0.09, height=0.09, fill_color=DIRT, fill_opacity=1, stroke_width=0)

            def update_dirt(dot: Mobject, *, index: int = i) -> None:
                values = state()["dirt"]
                dot.set_opacity(1 if index < len(values) else 0)
                if index < len(values):
                    dot.move_to(along(dirty_route, values[index]) + np.array([0, -0.11, 0]))

            speck.add_updater(update_dirt)
            self.add(speck)
        anchors = [
            ("Nozzle", 158, 627, 153, 550),
            ("Porous bag", 466, 260, 480, 310),
            ("Fan", 650, 218, 650, 350),
            ("Motor", 785, 507, 770, 435),
            ("Air out", 850, 207, 850, 280),
        ]
        for text, x, y, ax, ay in anchors:
            self.add(Line(xy(x, y + (17 if y < ay else -18)), xy(ax, ay), color="#97a6b2", stroke_width=1.5))
            self.add(label(text, x, y))
        if frames[0]["blocked"]:
            self.add(
                Line(xy(115, 535), xy(185, 580), color="#a43e32", stroke_width=8),
                Line(xy(185, 535), xy(115, 580), color="#a43e32", stroke_width=8),
            )
        titles = [
            "A powered fan changes the air pressure",
            "Follow the air. The dirt comes with it.",
            "Air crosses the bag. Dirt does not.",
            "One continuous path through the cleaner",
        ]
        heading = label(titles[0], 480, 87, 30)
        previous = [-1]

        def update_title(text: Mobject) -> None:
            beat = state()["beat"]
            if beat != previous[0]:
                text.become(
                    label(
                        "A turning fan needs an open path" if state()["blocked"] else titles[beat],
                        480,
                        87,
                        30,
                    )
                )
                previous[0] = beat

        heading.add_updater(update_title)
        self.add(heading, label("Illustrative section · motion slowed", 480, 688, 24, "#667583"))

        # Each inset owns its mechanism and surrounding passage. The full-machine
        # coordinates above are only the final locator, never enlarged as a fake inset.
        cover = Rectangle(width=12.8, height=9.6, fill_color=PAPER, fill_opacity=1, stroke_width=0)
        self.add(cover)
        details: list[VGroup] = []

        def rect(x: float, y: float, w: float, h: float, fill: str, stroke: str) -> RoundedRectangle:
            return RoundedRectangle(
                width=w / 75,
                height=h / 75,
                corner_radius=0.15,
                fill_color=fill,
                fill_opacity=1,
                stroke_color=stroke,
                stroke_width=2,
            ).move_to(xy(x, y))

        def markers(
            group: VGroup,
            air_path: Sequence[tuple[float, float]],
            dirt_path: Sequence[tuple[float, float]] | None = None,
        ) -> None:
            for index in range(12):
                mark = Dot(radius=0.075, color=AIR)

                def move_air(dot: Mobject, *, i: int = index) -> None:
                    values = state()["air"]
                    if i < len(values):
                        dot.move_to(along(air_path, values[i]))

                mark.add_updater(move_air)
                group.add(mark)
            if dirt_path is not None:
                for index in range(5):
                    mark_dirt = Rectangle(
                        width=0.12, height=0.12, fill_color=DIRT, fill_opacity=1, stroke_width=0
                    )

                    def move_dirt(dot: Mobject, *, i: int = index) -> None:
                        values = state()["dirt"]
                        if i < len(values):
                            dot.move_to(along(dirt_path, values[i]))

                    mark_dirt.add_updater(move_dirt)
                    group.add(mark_dirt)

        fan_detail = VGroup(
            label("Give air a way out.", 480, 85, 38), rect(481, 367, 720, 280, "#eef3f9", "#c6d2de")
        )
        fan_detail.add(
            path([(118, 420), (118, 507), (841, 507), (841, 420)], "#647e93", 4),
            path([(118, 304), (118, 226), (841, 226), (841, 304)], "#647e93", 4),
        )
        fan_detail.add(
            label("From bag", 180, 558, 32),
            label("Air out", 805, 558, 32),
            label("Lower pressure", 295, 270, 30, AIR),
            label("Motor", 697, 270, 32),
        )
        fan_detail.add(
            Line(xy(480, 367), xy(693, 367), color="#526c81", stroke_width=10),
            rect(690, 367, 146, 87, "#c5d5e4", "#637d93"),
        )
        for x in range(636, 750, 15):
            fan_detail.add(Line(xy(x, 330), xy(x, 404), color="#8da5b9", stroke_width=2))
        fan_detail.add(
            Ellipse(width=1.0, height=3.0, stroke_color="#869fb2", stroke_width=4).move_to(xy(480, 367))
        )
        large_rotor = VGroup()
        for index in range(7):
            blade = Polygon(
                xy(480, 367),
                xy(480, 367),
                xy(480, 367),
                fill_color="#6888a3",
                fill_opacity=1,
                stroke_width=1,
                stroke_color="#35566d",
            )

            def move_blade(item: Mobject, *, i: int = index) -> None:
                a = math.radians(state()["angle"]) + i * math.tau / 7
                coords = [
                    (480 + 8 * math.cos(a), 367 + 17 * math.sin(a)),
                    (480 + 35 * math.cos(a + 0.2), 367 + 101 * math.sin(a + 0.2)),
                    (480 + 35 * math.cos(a + 0.6), 367 + 101 * math.sin(a + 0.6)),
                ]
                cast(VMobject, item).set_points_as_corners([xy(*p) for p in [*coords, coords[0]]])

            blade.add_updater(move_blade)
            large_rotor.add(blade)
        fan_detail.add(large_rotor, Dot(xy(480, 367), radius=0.10, color=INK), label("Fan", 480, 190, 32))
        markers(
            fan_detail, [(84, 430), (250, 430), (422, 367), (480, 367), (532, 460), (795, 460), (879, 430)]
        )
        fan_detail.add(label("Moving air out lowers pressure on the inlet side.", 480, 644, 30))
        details.append(fan_detail)

        inlet_detail = VGroup(
            label("The room pushes air in.", 480, 85, 38),
            label("Room air", 206, 272, 34),
            label("Lower pressure inside", 645, 243, 31, AIR),
        )
        inlet_detail.add(
            Line(xy(85, 552), xy(875, 552), color="#a3b3c2", stroke_width=3),
            path([(395, 510), (445, 410), (535, 310), (725, 310)], "#7b92a5", 72),
            path([(395, 510), (445, 410), (535, 310), (725, 310)], "#edf3f8", 60),
        )
        inlet_detail.add(
            Polygon(
                xy(300, 500),
                xy(452, 500),
                xy(487, 546),
                xy(248, 546),
                fill_color="#dce7f0",
                fill_opacity=1,
                stroke_color="#607d94",
                stroke_width=3,
            )
        )
        inlet_detail.add(label("Nozzle", 365, 607, 34), label("To bag", 788, 359, 32))
        for i in range(10):
            inlet_detail.add(Dot(xy(125 + i * 23, 534), radius=0.045, color=DIRT))
        inlet_air = [(76, 532), (279, 532), (369, 528), (434, 420), (535, 310), (817, 310)]
        markers(inlet_detail, inlet_air, inlet_air[:-1] + [(760, 310)])
        inlet_detail.add(label("Moving air carries loose dirt through the opening.", 480, 669, 29))
        details.append(inlet_detail)

        bag_detail = VGroup(
            label("Separate the dirt from the air.", 480, 85, 38),
            rect(452, 372, 324, 330, "#eee6d8", "#9e8d71"),
        )
        bag_detail.add(
            path([(88, 330), (291, 330)], "#7890a5", 55),
            path([(88, 330), (291, 330)], "#e6eef6", 44),
            label("From hose", 181, 258, 32),
            label("Porous bag", 420, 159, 34),
            label("To fan", 788, 261, 32),
        )
        for y in range(218, 528, 24):
            bag_detail.add(Line(xy(606, y), xy(628, y + 16), color="#9f8b6b", stroke_width=3))
        for i in range(25):
            bag_detail.add(Dot(xy(346 + (i % 7) * 26, 498 - (i // 7) * 21), radius=0.045, color=DIRT))
        bag_detail.add(label("Dirt stays", 431, 593, 34, DIRT), label("Air passes", 768, 412, 32, AIR))
        markers(
            bag_detail,
            [(83, 330), (310, 330), (460, 350), (620, 350), (870, 350)],
            [(83, 342), (307, 342), (411, 381), (465, 468)],
        )
        bag_detail.add(label("The bag material has tiny paths for air.", 480, 667, 31))
        details.append(bag_detail)
        for detail in details:
            self.add(detail)
        styles = [
            [
                (item, item.get_fill_opacity(), item.get_stroke_opacity())
                for item in detail.get_family()
                if isinstance(item, VMobject)
            ]
            for detail in details
        ]

        def visibility(_dt: float) -> None:
            beat = state()["beat"]
            cover.set_opacity(0 if beat == 3 else 1)
            for index, members in enumerate(styles):
                visible = 1 if beat == index else 0
                for item, fill_alpha, stroke_alpha in members:
                    item.set_fill(opacity=fill_alpha * visible)
                    item.set_stroke(opacity=stroke_alpha * visible)

        self.add_updater(visibility)
        self.play(clock.animate.set_value(len(frames)), run_time=len(frames) / 24, rate_func=linear)
