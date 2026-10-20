"""Domain-specific boundaries where a generic flow panel would teach the wrong thing."""

from ..teaching_authoring import transition
from ..teaching_contracts import Pose
from .panels import BLUE, INK, METAL, WARM, Panel, base, freeze
from .plans import Step, SystemPlan


def circuit(plan: SystemPlan, step: Step, index: int) -> Panel:
    """A conceptual electrical control, never a fictitious water valve."""
    d = base(plan, step, index)
    d.box("supply", 150, 230, 100, 100, "#c1ceda")
    d.line("wire", [[250, 280], [350, 280]], BLUE, 7)
    contact = d.line("contact", [[350, 280], [470, 280]], INK, 8)
    d.line("load-wire", [[470, 280], [610, 280]], BLUE, 7)
    d.line("element", [[610, 240], [650, 255], [610, 270], [650, 285], [610, 300], [650, 315]], WARM, 9)
    d.text("supply-label", "Supply", 115, 370, 36)
    d.text("switch-label", "Controlled switch", 265, 160, 36)
    d.text("load-label", "Heater", 600, 370, 36)
    d.text("model", "Conceptual circuit · wiring omitted", 110, 470, 30)
    marker = d.dot("energy-input", 275, 280, 8, WARM)
    changes = [transition(contact, Pose(angle=-35)), transition(marker, Pose(opacity=0))]
    return Panel(d, changes, [transition(contact, Pose(), Pose()), transition(marker, Pose(x=310))])


def dryer_heat(plan: SystemPlan, step: Step, index: int) -> Panel:
    d = base(plan, step, index)
    d.box("duct-wall-top", 130, 200, 630, 22, METAL)
    d.box("duct-wall-bottom", 130, 340, 630, 22, METAL)
    d.line("element", [[420, 225], [450, 245], [420, 265], [450, 285], [420, 305], [450, 335]], WARM, 9)
    d.text("air-in", "Room air", 100, 150, 36)
    d.text("air-out", "Warmer air", 565, 150, 36)
    d.text("element-label", "Electric element", 275, 445, 36)
    marker = d.dot("air", 180, 280, 9, BLUE)
    changes = [transition(marker, Pose(x=515, fill=WARM))]
    return Panel(d, changes, [transition(marker, Pose(x=515))])


def storage_flow(plan: SystemPlan, step: Step, index: int) -> Panel:
    d = base(plan, step, index)
    d.box("insulation", 285, 140, 330, 285, METAL)
    d.box("stored-water", 305, 160, 290, 245, "#a9cfe2")
    d.box("hot-layer", 305, 160, 290, 85, "#e0b799")
    d.line("dip-tube", [[355, 100], [355, 360]], BLUE, 22)
    d.line("hot-outlet", [[535, 205], [535, 100]], WARM, 22)
    cold = d.dot("cold-flow", 355, 140, 6, "#1d6289")
    hot = d.dot("hot-flow", 535, 195, 6, "#80421e")
    d.text("cold-label", "Cold in", 155, 80, 36)
    d.text("hot-label", "Hot out", 540, 80, 36)
    d.text("dip-label", "Dip tube", 80, 310, 36)
    d.line("dip-pointer", [[255, 325], [355, 325]], INK, 2)
    d.text("store-label", "Tank remains full", 270, 475, 36)
    changes = [transition(cold, Pose(y=200)), transition(hot, Pose(y=-85))]
    return Panel(d, changes, freeze(changes))


def air_motion(plan: SystemPlan, step: Step, index: int) -> Panel:
    d = base(plan, step, index)
    d.box("motor", 175, 225, 100, 100, METAL)
    d.line("shaft", [[275, 275], [330, 275]], INK, 12)
    blade = d.line("side-view-blade", [[330, 190], [350, 225], [330, 325], [350, 360]], BLUE, 18)
    d.text("blade-label", "Angled moving blade", 110, 120, 32)
    d.text("air-label", "Air gains momentum", 380, 450, 32)
    changes = [transition(blade, Pose(sy=.7), Pose(sy=1))]
    for j in range(3):
        a = d.arrow(f"air-{j}", 400, 210+j*65, 105, BLUE)
        changes.append(transition(a, Pose(x=135)))
    if index == 2:
        d.box("skin-surface", 740, 190, 22, 190, "#d4ad90")
        d.text("skin-label", "Skin", 720, 145, 36)
    return Panel(d, changes, freeze(changes))


def mixing(plan: SystemPlan, step: Step, index: int) -> Panel:
    d = base(plan, step, index)
    d.line("cold-inlet", [[160, 185], [355, 185], [440, 275]], BLUE, 30)
    d.line("hot-inlet", [[160, 365], [355, 365], [440, 275]], WARM, 30)
    d.line("spout", [[440, 275], [720, 275]], METAL, 44)
    d.line("spout-bore", [[440, 275], [720, 275]], "#c0dce9", 26)
    d.text("cold-label", "Cold supply", 110, 130, 36)
    d.text("hot-label", "Hot supply", 110, 410, 36)
    d.text("mix-label", "Mixed outlet", 550, 220, 36)
    cold = d.dot("cold-water", 190, 185, 6, "#1d6289")
    hot = d.dot("hot-water", 190, 365, 6, "#80421e")
    changes = [transition(cold, Pose(x=500, y=90), via=[Pose(x=160), Pose(x=250, y=90)]),
               transition(hot, Pose(x=500, y=-90), via=[Pose(x=160), Pose(x=250, y=-90)])]
    return Panel(d, changes, freeze(changes))


def reversing(plan: SystemPlan, step: Step, index: int) -> Panel:
    d = base(plan, step, index)
    d.box("valve-body", 290, 190, 300, 190, METAL)
    for name, points in (("supply", [[440, 110], [440, 210]]), ("left", [[150, 285], [310, 285]]),
                         ("right", [[570, 285], [750, 285]]), ("return", [[440, 360], [440, 430]])):
        d.line(name, [[float(v) for v in point] for point in points], BLUE, 20)
    route = d.line("routing", [[440, 210], [440, 285], [310, 285]], WARM, 14)
    other = d.line("other-routing", [[440, 210], [440, 285], [570, 285]], WARM, 14)
    returning = d.line("return-route", [[570, 305], [490, 330], [440, 360]], BLUE, 14)
    other_return = d.line("other-return", [[310, 305], [390, 330], [440, 360]], BLUE, 14)
    d.text("work-in", "Hot supply", 310, 75, 36)
    d.text("left-label", "Indoor", 100, 225, 36)
    d.text("right-label", "Outdoor", 610, 225, 36)
    d.text("return-label", "Return", 370, 465, 36)
    # Mode comparison swaps routing; no claim to simulate the slide's transient motion.
    changes = [transition(route, Pose(), Pose()), transition(other, Pose(opacity=0), Pose(opacity=0)),
               transition(returning, Pose(), Pose()), transition(other_return, Pose(opacity=0), Pose(opacity=0))]
    alternate = [transition(route, Pose(opacity=0), Pose(opacity=0)), transition(other, Pose(), Pose()),
                 transition(returning, Pose(opacity=0), Pose(opacity=0)), transition(other_return, Pose(), Pose())]
    # Add a visible marker for the normal stream so the beat has a geometric change.
    marker = d.dot("supply-marker", 440, 150, 6, WARM)
    changes.append(transition(marker, Pose(x=-230, y=135), via=[Pose(y=135)]))
    alternate.append(transition(marker, Pose(x=230, y=135), via=[Pose(y=135)]))
    return Panel(d, changes, alternate)


def disc(plan: SystemPlan, step: Step, index: int) -> Panel:
    """Section through two disc openings: a slide changes their overlap."""
    d = base(plan, step, index)
    top_a = d.box("upper-disc-left", 200, 230, 225, 25, "#a8becf")
    top_b = d.box("upper-disc-right", 475, 230, 225, 25, "#a8becf")
    d.box("lower-disc-left", 200, 290, 225, 25, "#d1dce4")
    d.box("lower-disc-right", 475, 290, 225, 25, "#d1dce4")
    d.text("upper-label", "Sliding disc", 120, 155, 36)
    d.text("lower-label", "Fixed disc", 540, 365, 36)
    d.text("hole-label", "Overlapping holes", 230, 455, 36)
    d.text("supply-label", "Supply", 540, 190, 36)
    stream = d.dot("water", 450, 195, 7, BLUE)
    changes = [transition(top_a, Pose(), Pose(x=80), via=[Pose()]), transition(top_b, Pose(), Pose(x=80), via=[Pose()]),
               transition(stream, Pose(y=160), Pose(opacity=0), via=[Pose(opacity=0), Pose(opacity=0)])]
    alternate = [transition(top_a, Pose(x=80), Pose(x=80)), transition(top_b, Pose(x=80), Pose(x=80)),
                 transition(stream, Pose(opacity=0), Pose(opacity=0))]
    return Panel(d, changes, alternate)


def toilet_trap(plan: SystemPlan, step: Step, index: int) -> Panel:
    """A filled rising trapway then a descending drain, not a sink's simple U-bend."""
    d = base(plan, step, index)
    d.box("bowl-shell", 150, 180, 240, 170, METAL)
    d.box("bowl-water", 172, 200, 196, 130, "#a5cee2")
    points: list[list[float]] = [[350, 300], [410, 340], [460, 300], [480, 205], [530, 190], [580, 235], [580, 390], [720, 390]]
    d.line("trapway-wall", points, METAL, 66)
    d.line("trapway-bore", points, "#f7fbfd", 42)
    d.line("filled-trapway", points, BLUE, 32)
    d.text("bowl-label", "Bowl", 160, 115, 40)
    d.text("crest-label", "Filled trapway", 420, 105, 36)
    d.text("drain-label", "Lower drain", 570, 455, 36)
    marker = d.dot("water", 350, 300, 7, "#215b7b")
    changes = [transition(marker, Pose(x=350, y=90), via=[Pose(x=60, y=40), Pose(x=110),
                  Pose(x=130, y=-95), Pose(x=180, y=-110), Pose(x=230, y=-65), Pose(x=230, y=90)])]
    return Panel(d, changes, freeze(changes))
