"""Physical section primitives. Geometry is authored; causal changes are shared data."""

from dataclasses import dataclass

from ..teaching_authoring import Drawing, transition
from ..teaching_contracts import Change, Pose
from .plans import Step, SystemPlan

INK = "#273b4a"
BLUE = "#337ca0"
WARM = "#ac5b2d"
METAL = "#c6d2dc"


@dataclass
class Panel:
    drawing: Drawing
    changes: list[Change]
    alternate: list[Change]


def base(plan: SystemPlan, step: Step, index: int) -> Drawing:
    """A working part always has its own labeled surroundings, not whole-object coordinates."""
    d = Drawing(f"c{index}-")
    d.box("surroundings", 45, 90, 810, 350, "#eaf0f5")
    d.text("component", plan.core[step.focus], 65, 34, 36)
    return d


def freeze(changes: list[Change], *, end: bool = False) -> list[Change]:
    """A declared static comparison, rather than a second implementation of physics."""
    return [Change(target=c.target, before=c.after if end else c.before, after=c.after if end else c.before) for c in changes]


def heat(plan: SystemPlan, step: Step, index: int) -> Panel:
    d = base(plan, step, index)
    d.box("vessel-wall", 260, 165, 400, 240, METAL)
    d.box("vessel-interior", 278, 180, 364, 207, "#f9fbfd")
    contents = "#d1b483" if plan.id == "electric-oven" else "#a5d2e7"
    d.box("contents", 294, 275, 332, 98, contents)
    immersed = plan.id == "water-heater"
    y = 354 if immersed else 395
    d.line("element", [[300, y], [330, y-8], [370, y], [410, y-8], [450, y], [490, y-8], [530, y], [590, y-8]], WARM, 9)
    d.text("wall-label", "Metal wall", 655, 205, 32)
    d.line("wall-leader", [[650, 211], [641, 211]], INK, 2)
    d.text("energy-label", "Energy in", 65, 315, 36)
    arrow = d.arrow("heat-input", 100, 350, 115, WARM)
    d.text("water-label", "Contents gain energy", 278, 460, 32)
    motions = [transition(arrow, Pose(x=70), Pose(x=0))]
    for j in range(3):
        marker = d.dot(f"thermal-{j}", 350 + j*85, 307, 9, WARM)
        motions.append(transition(marker, Pose(y=-82), Pose(opacity=.15)))
    alternate = freeze(motions)
    alternate[0] = transition(arrow, Pose(opacity=0), Pose(opacity=0))
    return Panel(d, motions, alternate)


def coil(plan: SystemPlan, step: Step, index: int) -> Panel:
    d = base(plan, step, index)
    warm = step.focus == 2 and plan.id in {"refrigerator", "air-conditioner"}
    d.text("air-label", "Surrounding air", 280, 130, 36)
    d.box("tube-metal", 170, 235, 560, 112, METAL)
    d.box("open-passage", 169, 254, 562, 74, "#dcecf7")
    d.box("liquid-region", 190 if not warm else 535, 290, 175, 28, "#8fbed8")
    for j in range(4):
        d.dot(f"phase-{j}", 450+j*57 if not warm else 225+j*57, 276, 12, "#ffffff")
    d.text("inlet", "Vapor in" if warm else "Liquid in", 130, 388, 32)
    d.text("outlet", "Liquid out" if warm else "Vapor out", 575, 388, 32)
    d.text("wall", "Metal tube wall", 305, 470, 32)
    d.line("wall-pointer", [[425, 452], [425, 345]], INK, 2)
    d.text("heat-label", "Heat out" if warm else "Heat in", 585, 180, 32)
    energy = d.arrow("heat-arrow", 405, 200, 100, WARM)
    # A broad transfer arrow is oriented through the wall; it is not refrigerant.
    heat_before = Pose(angle=-90 if warm else 90, y=35 if warm else -15)
    heat_after = Pose(angle=-90 if warm else 90, y=-15 if warm else 35)
    motions = [transition(energy, heat_after, heat_before)]
    flow = d.dot("flow-marker", 205, 303, 7, BLUE)
    motions.append(transition(flow, Pose(x=470)))
    altered = freeze(motions)
    if plan.id == "air-conditioner":
        altered = list(motions)
        altered[0] = transition(energy, Pose(opacity=0), Pose(opacity=0))
    return Panel(d, motions, altered)


def tank(plan: SystemPlan, step: Step, index: int) -> Panel:
    d = base(plan, step, index)
    d.box("tank-shell", 245, 130, 390, 285, METAL)
    d.box("tank-cavity", 263, 151, 354, 246, "#fafcfe")
    water = d.box("water", 280, 285, 320, 95, "#9ccbe2")
    lid = d.box("lid", 232, 116, 417, 25, "#74899d")
    d.text("liquid-label", "Liquid", 90, 335, 36)
    d.line("liquid-pointer", [[200, 331], [280, 331]], INK, 2)
    d.text("vapor-label", "Vapor", 660, 180, 36)
    d.line("vapor-pointer", [[657, 190], [617, 190]], INK, 2)
    motions: list[Change] = []
    for j in range(4):
        bubble = d.dot(f"vapor-{j}", 315+j*75, 287, 11, "#ffffff")
        motions.append(transition(bubble, Pose(y=-100), Pose(opacity=.1)))
    alternate = freeze(motions)
    if plan.id == "pressure-cooker":
        alternate = [transition(lid, Pose(y=-45), Pose(y=-45)), *[
            transition(c.target, Pose(y=-145), Pose(opacity=.1)) for c in motions
        ]]
    elif plan.id == "toilet":
        # Refill is a rising level and float, not evaporation.
        d.parts = [p for p in d.parts if not p.id.startswith(d.prefix+"vapor-")]
        floating = d.dot("float", 545, 275, 20, "#c28a56")
        stem = d.line("float-arm", [[565, 275], [585, 275], [585, 164]], INK, 5)
        inlet = d.dot("inlet-water", 330, 160, 8, BLUE)
        d.text("float-label", "Float", 668, 275, 32)
        d.line("float-pointer", [[663, 281], [566, 281]], INK, 2)
        motions = [transition(water, Pose(sy=2, y=-47.5)), transition(floating, Pose(y=-95)),
                   transition(stem, Pose(y=-70)), transition(inlet, Pose(y=100, opacity=0))]
        alternate = freeze(motions, end=True)
    return Panel(d, motions, alternate)


def valve(plan: SystemPlan, step: Step, index: int) -> Panel:
    d = base(plan, step, index)
    d.box("upper-wall", 100, 220, 700, 20, METAL)
    d.box("lower-wall", 100, 330, 700, 20, METAL)
    d.box("gate-housing", 405, 130, 90, 100, "#a6b8c5")
    gate = d.box("gate", 427, 205, 46, 125, "#bd8d60")
    d.line("handle", [[410, 158], [490, 158]], INK, 8)
    d.text("in-label", "In", 110, 185, 36)
    d.text("out-label", "Out", 720, 185, 36)
    d.text("gate-label", "Controlled opening", 270, 455, 36)
    d.line("gate-leader", [[452, 433], [452, 350]], INK, 2)
    motions = [transition(gate, Pose(y=-90))]
    for j in range(3):
        flow = d.dot(f"flow-{j}", 140+j*15, 310, 8, BLUE)
        motions.append(transition(flow, Pose(x=430)))
    alternate = [transition(gate, Pose(), Pose()), *[
        transition(c.target, Pose(opacity=0), Pose(opacity=0)) for c in motions[1:]
    ]]
    if plan.id in {"electric-oven", "electric-kettle", "water-heater"}:
        d.text("schematic", "Supply switch · conceptual", 75, 500, 30)
    return Panel(d, motions, alternate)


def restrictor(plan: SystemPlan, step: Step, index: int) -> Panel:
    """A capillary restricts an open passage; it is not an opening/closing valve."""
    d = base(plan, step, index)
    d.box("high-side-wall", 125, 180, 200, 190, METAL)
    d.box("high-liquid", 125, 200, 200, 150, "#a5cee2")
    d.box("capillary-metal", 325, 258, 245, 44, METAL)
    d.box("capillary-bore", 325, 270, 245, 20, "#9ccbe2")
    d.box("low-side-wall", 570, 180, 200, 190, METAL)
    d.box("low-mixture", 570, 200, 200, 150, "#b8d8e8")
    d.text("high-label", "Higher pressure", 105, 150, 32)
    d.text("low-label", "Lower pressure", 555, 150, 32)
    d.text("bore-label", "Fixed narrow bore", 285, 445, 36)
    flow_marker = d.dot("fluid", 160, 280, 6, BLUE)
    bubble = d.dot("flash-vapor", 675, 260, 17, "#ffffff")
    changes = [transition(flow_marker, Pose(x=550)), transition(bubble, Pose(opacity=1), Pose(opacity=0))]
    return Panel(d, changes, freeze(changes))


def flow(plan: SystemPlan, step: Step, index: int) -> Panel:
    d = base(plan, step, index)
    d.box("upper-wall", 110, 205, 680, 22, METAL)
    d.box("lower-wall", 110, 332, 680, 22, METAL)
    d.text("inlet", "Inlet", 100, 160, 36)
    d.text("outlet", "Outlet", 650, 160, 36)
    d.text("passage", "Connected open passage", 205, 460, 36)
    motions = []
    for j in range(5):
        marker = d.dot(f"flow-{j}", 145+j*38, 270+(j%2)*25, 10, BLUE)
        motions.append(transition(marker, Pose(x=400)))
    # An idealized no-through-path is visible as a barrier, rather than a ghost flow.
    barrier = d.box("barrier", 440, 227, 25, 105, "#74899d")
    motions.append(transition(barrier, Pose(opacity=0), Pose(opacity=0)))
    alternate = [*freeze(motions[:-1]), transition(barrier, Pose(opacity=1), Pose(opacity=1))]
    if plan.id in {"table-fan", "electric-oven"}:
        # Stopping a fan does not insert a fictitious solid barrier into the room.
        alternate = freeze(motions)
    return Panel(d, motions, alternate)
