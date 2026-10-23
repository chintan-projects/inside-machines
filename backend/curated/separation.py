"""Fluid separation, field heating and dependency diagrams with explicit boundaries."""

from ..teaching_authoring import transition
from ..teaching_contracts import Change, Pose
from .panels import BLUE, INK, METAL, WARM, Panel, base, freeze
from .plans import Step, SystemPlan


def filter_panel(plan: SystemPlan, step: Step, index: int) -> Panel:
    d = base(plan, step, index)
    d.box("chamber", 160, 185, 590, 190, METAL)
    d.box("passage", 160, 205, 590, 150, "#f8fbfd")
    # The drawn pores are real gaps, so moving air never passes a solid wall.
    for j in range(4):
        d.box(f"porous-wall-{j}", 450, 205+j*42, 20, 22, "#ba986e")
    d.text("in-label", "In", 140, 150, 36)
    d.text("out-label", "Out", 685, 150, 36)
    d.text("wall-label", "Porous separator", 275, 455, 36)
    changes: list[Change] = []
    for j in range(3):
        marker = d.dot(f"air-{j}", 190+j*23, 236+j*42, 5, BLUE)
        changes.append(transition(marker, Pose(x=460)))
    dirt = d.dot("retained-particle", 210, 280, 12, WARM)
    changes.append(transition(dirt, Pose(x=222)))
    barrier = d.box("airtight-comparison", 450, 205, 20, 150, INK)
    changes.append(transition(barrier, Pose(opacity=0), Pose(opacity=0)))
    alt = [*freeze(changes[:-1]), transition(barrier, Pose(), Pose())]
    if plan.id == "espresso-machine":
        # More resistance is less throughput, not a solid airtight coffee bed.
        alt = [changes[0], *freeze(changes[1:3]),
               changes[3], transition(barrier, Pose(opacity=0), Pose(opacity=0))]
    return Panel(d, changes, alt)


def field(plan: SystemPlan, step: Step, index: int) -> Panel:
    d = base(plan, step, index)
    microwave = plan.id == "microwave"
    if microwave:
        d.box("metal-enclosure", 250, 155, 470, 260, METAL)
        d.box("cavity", 270, 175, 430, 220, "#f8fbfd")
        d.box("food", 430, 285, 160, 90, "#d4b284")
        d.box("source", 115, 235, 130, 90, "#859eaf")
        d.text("source-label", "Source", 95, 200, 36)
        d.text("food-label", "Food", 500, 455, 36)
        wave = d.line("field", [[290, 260], [325, 240], [360, 280], [395, 240], [430, 280], [465, 260]], BLUE, 6)
        # An energy marker stays in the cavity; it is not literal matter crossing a shield.
        heat = d.dot("absorbed-energy", 510, 330, 12, WARM)
        changes = [transition(wave, Pose(x=35)), transition(heat, Pose(sx=1.8, sy=1.8), Pose(opacity=.2))]
        d.text("model-label", "Field pattern is illustrative", 210, 120, 30)
    else:
        d.box("glass-top", 210, 310, 480, 20, "#91a8b7")
        d.box("pan-base", 290, 286, 320, 22, METAL)
        d.box("pan-wall-left", 290, 210, 18, 76, METAL)
        d.box("pan-wall-right", 592, 210, 18, 76, METAL)
        d.box("contents", 310, 245, 280, 38, "#d4b284")
        coil = d.line("coil", [[300, 365], [350, 350], [400, 365], [450, 350], [500, 365], [550, 350], [600, 365]], BLUE, 8)
        energy = d.arrow("energy", 420, 275, 55, WARM)
        d.text("coil-label", "Powered coil", 265, 440, 36)
        d.text("pan-label", "Suitable metal pan", 225, 165, 36)
        changes = [transition(coil, Pose(opacity=1), Pose(opacity=.35)),
                   transition(energy, Pose(angle=-90, y=-25), Pose(angle=-90, y=12))]
    if not microwave:
        alternate = [changes[0], transition(energy, Pose(opacity=0), Pose(opacity=0))]
        return Panel(d, changes, alternate)
    return Panel(d, changes, freeze(changes))


def spray(plan: SystemPlan, step: Step, index: int) -> Panel:
    d = base(plan, step, index)
    d.box("tub", 170, 135, 560, 290, METAL)
    d.box("inside", 190, 155, 520, 250, "#f9fbfd")
    d.line("dish", [[405, 190], [420, 255], [530, 255], [545, 190]], INK, 9)
    d.box("spray-arm", 300, 355, 300, 20, BLUE)
    d.box("pump-inlet", 436, 375, 28, 45, BLUE)
    d.text("dish-label", "Dish surface", 310, 110, 36)
    d.text("arm-label", "Spray arm", 270, 475, 36)
    changes = []
    for j in range(3):
        jet = d.dot(f"jet-{j}", 435+j*35, 343, 6, BLUE)
        changes.append(transition(jet, Pose(y=-76)))
    barrier = d.box("blocked-view", 408, 300, 150, 16, "#b88d60")
    changes.append(transition(barrier, Pose(opacity=0), Pose(opacity=0)))
    alt = [*[transition(c.target, Pose(y=-20)) for c in changes[:-1]], transition(barrier, Pose(), Pose())]
    return Panel(d, changes, alt)


def trap(plan: SystemPlan, step: Step, index: int) -> Panel:
    d = base(plan, step, index)
    # Open U passage: the water seal fills the bottom of both connected legs.
    d.line("pipe-wall", [[285, 130], [285, 350], [315, 385], [490, 385], [525, 350], [525, 240], [690, 240]], METAL, 76)
    d.line("open-bore", [[285, 130], [285, 350], [315, 385], [490, 385], [525, 350], [525, 240], [690, 240]], "#f8fbfd", 48)
    water = d.line("water-seal", [[285, 290], [285, 350], [315, 385], [490, 385], [525, 350], [525, 290]], BLUE, 46)
    d.text("sink-label", "From sink", 100, 110, 36)
    d.text("drain-label", "To drain", 625, 180, 36)
    d.text("seal-label", "Retained water seal", 240, 475, 36)
    marker = d.dot("water-flow", 285, 160, 7, "#17648c")
    changes = [transition(marker, Pose(x=365, y=80), via=[Pose(y=185), Pose(x=45, y=225), Pose(x=195, y=225), Pose(x=240, y=175), Pose(x=240, y=80)])]
    alt = [transition(water, Pose(opacity=0), Pose(opacity=0)),
           transition(marker, Pose(opacity=0), Pose(opacity=0))]
    return Panel(d, changes, alt)


def compute(plan: SystemPlan, step: Step, index: int) -> Panel:
    d = base(plan, step, index)
    inputs = (1, 3, 5)
    d.text("kind", "Logical view · not chip geometry", 110, 120, 32)
    if index == 2:
        d.box("first-job", 150, 200, 150, 65, "#c8d9ed")
        d.text("first-operation", "1 + 1", 170, 212, 36)
        d.box("second-job", 150, 330, 150, 65, "#c8d9ed")
        d.text("second-operation", "3 + 1", 170, 342, 36)
        d.box("dependent", 510, 250, 220, 100, "#d6e5d8")
        first, second = inputs[0] + 1, inputs[1] + 1
        answer = d.text("dependent-answer", f"{first} + {second} = {first + second}", 525, 280, 36)
        d.line("dependency-a", [[300, 230], [400, 230], [510, 275]], BLUE, 5)
        d.line("dependency-b", [[300, 362], [400, 362], [510, 325]], BLUE, 5)
        d.text("dependency-label", "Both results needed", 425, 425, 32)
        a = d.dot("first-result", 320, 230, 8, BLUE)
        b = d.dot("second-result", 320, 362, 8, BLUE)
        changes = [transition(a, Pose(x=180, y=45), via=[Pose(x=80)]),
                   transition(b, Pose(x=180, y=-37), via=[Pose(x=80)]),
                   transition(answer, Pose(), Pose(opacity=0), via=[Pose(opacity=0), Pose(opacity=0)])]
        return Panel(d, changes, freeze(changes))
    changes = []
    for j, operand in enumerate(inputs):
        result = operand + 1
        y = 185 + j*85
        d.box(f"input-{j}", 140, y, 90, 55, "#d9e6ef")
        d.text(f"input-value-{j}", str(operand), 174, y+10, 34)
        d.box(f"lane-{j}", 365, y, 160, 55, "#c8d9ed")
        d.text(f"operation-{j}", "+ 1", 410, y+10, 34)
        if index == 0:
            d.text(f"job-id-{j}", str(j), 75, y+10, 34)
        output = d.box(f"output-{j}", 660, y, 90, 55, "#d6e5d8")
        value = d.text(f"result-{j}", str(result), 692, y+10, 34)
        token = d.dot(f"operand-{j}", 255, y+27, 6, BLUE)
        changes.extend([transition(token, Pose(x=365)), transition(value, Pose(), Pose(opacity=0))])
        del output
    d.text("input-label", "Read inputs" if index == 1 else "Inputs", 100, 440, 36)
    d.text("work-label", "Compute" if index == 1 else "Independent jobs", 300, 490, 32)
    d.text("output-label", "Store" if index == 1 else "Results", 640, 440, 36)
    # Withhold the middle input: other independent work remains intact.
    alt = [c if not c.target.endswith(("operand-1", "result-1")) else transition(c.target, Pose(opacity=0), Pose(opacity=0)) for c in changes]
    alt.append(transition(d.prefix+"input-value-1", Pose(opacity=0), Pose(opacity=0)))
    return Panel(d, changes, alt)
