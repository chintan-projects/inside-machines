"""Bounded mechanical sections: a working stroke, actual contact and moving fabric."""

import math

from ..seed_geometry import part
from ..teaching_authoring import Drawing, transition
from ..teaching_contracts import Change, Pose
from .panels import BLUE, INK, METAL, WARM, Panel, base, freeze
from .plans import Step, SystemPlan


def polygon(d: Drawing, name: str, points: list[list[float]], color: str) -> str:
    """Use the real shape bounds so its rotation is about the actual centre."""
    x, y = min(p[0] for p in points), min(p[1] for p in points)
    w, h = max(p[0] for p in points)-x, max(p[1] for p in points)-y
    identity = d.prefix + name
    d.parts.append(part(identity, name.replace("-", " "),
                        "Authored working geometry; dimensions are illustrative.",
                        "polygon", x, y, w, h, points=points, color=color,
                        stroke=INK, layer=len(d.parts)))
    return identity


def orbit(target: str, x: float, y: float, degrees: float, *, before: Pose | None = None) -> Change:
    """Author one bounded orbit as poses, without putting simulation rules in the player."""
    start = before or Pose()
    radius_x, radius_y = x+start.x-450, y+start.y-270
    poses = []
    for i in range(8):
        angle = math.radians(degrees*i/7)
        poses.append(Pose(
            x=450+radius_x*math.cos(angle)-radius_y*math.sin(angle)-x,
            y=270+radius_x*math.sin(angle)+radius_y*math.cos(angle)-y,
            angle=start.angle+degrees*i/7,
        ))
    return transition(target, poses[-1], poses[0], via=poses[1:-1])


def pump(plan: SystemPlan, step: Step, index: int) -> Panel:
    """One delivery stroke displaces liquid through an outlet instead of compressing it."""
    d = base(plan, step, index)
    d.box("cylinder", 300, 150, 280, 295, METAL)
    water = d.box("water-chamber", 320, 170, 240, 160, "#a5cee2")
    ports: tuple[tuple[str, list[list[float]]], ...] = (
        ("inlet", [[150, 250], [320, 250]]), ("outlet", [[560, 205], [745, 205]]),
    )
    for name, points in ports:
        d.line(name+"-wall", points, METAL, 46)
        d.line(name+"-bore", points, "#a5cee2", 26)
    # During delivery the inlet is seated, the outlet provides an open path.
    d.box("inlet-check-seated", 280, 235, 12, 30, INK)
    d.line("outlet-check-open", [[598, 188], [625, 177]], INK, 7)
    plate = d.box("piston", 320, 330, 240, 34, "#7891a5")
    rod = d.box("rod", 426, 364, 28, 125, INK)
    d.box("drive-housing", 365, 400, 150, 95, "#8fa5b7")
    d.text("water-label", "Water chamber", 290, 105, 40)
    label = d.text("piston-label", "Piston", 635, 320, 40)
    pointer = d.line("piston-pointer", [[625, 341], [562, 341]], INK, 2)
    d.text("inlet-label", "Inlet check closed", 70, 395, 32)
    d.text("outlet-label", "Water out", 600, 265, 40)
    d.text("stroke-label", "Delivery: water flows out", 100, 500, 32)
    displacement = -70.0
    changes = [
        transition(plate, Pose(y=displacement)), transition(rod, Pose(y=displacement)),
        transition(label, Pose(y=displacement)), transition(pointer, Pose(y=displacement)),
        # The chamber gets smaller because water is delivered through the open
        # outlet. This is a volume displacement, not a liquid-density change.
        transition(water, Pose(sy=(160+displacement)/160, y=displacement/2)),
    ]
    for j in range(3):
        marker = d.dot(f"delivered-water-{j}", 568+j*18, 205, 6, BLUE)
        changes.append(transition(marker, Pose(x=100)))
    return Panel(d, changes, freeze(changes))


def piston(plan: SystemPlan, step: Step, index: int) -> Panel:
    """Isolate a sealed working stroke; do not invent an animated crank linkage."""
    if plan.id == "espresso-machine":
        return pump(plan, step, index)
    d = base(plan, step, index)
    d.box("cylinder", 300, 150, 280, 270, METAL)
    gas = d.box("sealed-gas", 320, 165, 240, 145, "#dcb693")
    plate = d.box("piston", 320, 310, 240, 28, "#7891a5")
    expansion = plan.id == "car"
    rod = d.box("rod", 426, 338, 28, 120 if expansion else 140, INK)
    # The opaque housing deliberately hides the linkage, rather than changing rod length.
    d.box("drive-housing", 365, 380, 150, 115, "#8fa5b7")
    d.text("gas-label", "Sealed gas", 65, 200, 40)
    d.line("gas-leader", [[260, 207], [320, 207]], INK, 2)
    label = d.text("piston-label", "Piston", 635, 320, 40)
    pointer = d.line("piston-leader", [[625, 327], [560, 327]], INK, 2)
    d.text("stroke-label", "One sealed working stroke", 145, 500, 32)
    # All three poses share one displacement; the plate remains sealed to the cylinder.
    before, after = (Pose(y=-75), Pose(y=30)) if expansion else (Pose(), Pose(y=-90))
    # Top stays at y=165. Both gas boundaries meet the piston face exactly at
    # every interpolated pose; no gas appears beneath the piston on expansion.
    gas_before = Pose(sy=(145+before.y)/145, y=before.y/2)
    gas_after = Pose(sy=(145+after.y)/145, y=after.y/2)
    changes = [transition(plate, after, before), transition(rod, after, before),
               transition(gas, gas_after, gas_before), transition(label, after, before),
               transition(pointer, after, before)]
    return Panel(d, changes, freeze(changes))


def rotor(plan: SystemPlan, step: Step, index: int) -> Panel:
    d = base(plan, step, index)
    if plan.id == "car":
        changes: list[Change] = []
        for k, (x, radius, teeth, angle) in enumerate(((365, 70, 8, 90), (540, 105, 12, -60))):
            # One connected toothed profile rotates about its own true centre.
            points = []
            for j in range(teeth * 4):
                theta = j * math.tau / (teeth * 4)
                r = radius if j % 4 in (1, 2) else radius-10
                points.append([x + r*math.cos(theta), 280 + r*math.sin(theta)])
            name = d.prefix + f"gear-{k}"
            d.parts.append(part(name, "Meshing gear", "Illustrative meshing gear; not a measured car ratio.",
                                "polygon", x-radius, 280-radius, radius*2, radius*2,
                                points=points, color=METAL, stroke=INK))
            d.dot(f"shaft-{k}", x, 280, 13, INK)
            changes.append(transition(name, Pose(angle=angle)))
        d.text("input", "Input shaft", 160, 150, 36)
        d.text("output", "Output shaft", 530, 450, 36)
        return Panel(d, changes, freeze(changes))
    if plan.id == "microwave":
        d.box("oven-cavity", 210, 155, 480, 260, METAL)
        d.box("inside", 230, 175, 440, 220, "#f8fafc")
        d.dot("plate", 450, 285, 98, "#d0dbe3")
        food = d.box("food", 390, 255, 120, 60, "#d5b17b")
        d.text("plate-label", "Turntable", 320, 465, 36)
        d.text("rotation", "Changes food position", 255, 120, 32)
        changes = [transition(food, Pose(angle=180))]
        return Panel(d, changes, freeze(changes))
    d.box("motor-shell", 170, 200, 150, 170, METAL)
    d.box("shaft", 320, 268, 110, 24, INK)
    d.dot("guard", 540, 280, 150, "#dce6ed")
    changes = []
    # A connected two-blade rotor fits inside the guard at every angle.
    blade = polygon(d, "rotor", [[540+x, 280+y] for x, y in (
        (-122, -32), (-75, -50), (-18, -16), (18, -16), (75, 14),
        (122, 32), (75, 50), (18, 16), (-18, 16), (-75, -14),
    )], BLUE)
    d.dot("hub", 540, 280, 25, INK)
    changes.append(transition(blade, Pose(angle=240)))
    d.text("motor-label", "Motor", 175, 160, 40)
    d.text("blade-label", "Blades", 650, 455, 40)
    d.line("blade-pointer", [[680, 430], [640, 355]], INK, 2)
    d.text("shaft-label", "Shaft", 330, 415, 40)
    return Panel(d, changes, freeze(changes))


def drum(plan: SystemPlan, step: Step, index: int) -> Panel:
    d = base(plan, step, index)
    d.dot("outer-tub", 450, 270, 155, METAL)
    d.dot("drum-cavity", 450, 270, 132, "#fbfcfe")
    changes: list[Change] = []
    # Each lifter is attached at the perimeter. Its real polygon rotates about
    # its own centre while authored translations carry it around the drum axis.
    # A polyline's first-point/stroke pivot must never be used as the drum axis.
    for k in range(3):
        theta = math.radians(-90+k*120)
        c, s = math.cos(theta), math.sin(theta)
        x, y = 450+116*c, 270+116*s
        points = [[x+radial*c-tangent*s, y+radial*s+tangent*c]
                  for radial, tangent in ((-8,-13),(8,-13),(8,13),(-8,13))]
        lifter = polygon(d, f"lifter-{k}", points, INK)
        changes.append(orbit(lifter, x, y, 160))
    spinning = plan.id == "washing-machine" and index == 2
    slow_clothes: list[Change] = []
    fast_clothes: list[Change] = []
    for j in range(3):
        offset = (j-1)*32
        x, y = 450+offset, 350
        cloth = d.box(f"cloth-{j}", x-14, y-10, 28, 20, "#c48c5c")
        slow_clothes.append(transition(cloth, Pose(x=-5, y=-5), via=[
            Pose(x=360+.2*offset-x, y=290-y, angle=-30),
            Pose(x=370+.1*offset-x, y=210-y, angle=-60),
            Pose(x=440+.3*offset-x, y=310-y, angle=15),
        ]))
        theta = math.radians(60+j*40)
        start = Pose(x=450+108*math.cos(theta)-x, y=270+108*math.sin(theta)-y,
                     angle=60+j*40+90)
        fast_clothes.append(orbit(cloth, x, y, 160, before=start))
    changes.extend(fast_clothes if spinning else slow_clothes)
    if spinning:
        d.line("drain-passage", [[450, 420], [450, 445], [700, 445]], BLUE, 14)
        drop = d.dot("drain-water", 450, 420, 6, BLUE)
        changes.append(transition(drop, Pose(x=235, y=25), via=[Pose(y=25)]))
        d.text("drain-label", "To drain", 625, 475, 32)
    d.text("drum-label", "Rotating drum", 275, 90, 40)
    d.text("fabric-label", "Fabric", 680, 310, 40)
    d.line("fabric-pointer", [[670, 316], [550, 325]], INK, 2)
    d.text("mode", "Spin extracts water" if spinning else "Lift, then fall", 235, 500, 32)
    alt = freeze(changes)
    if plan.id == "washing-machine" and not spinning:
        # Fast-spin fabric travels with the wall, rather than staying frozen in
        # room coordinates while the lifters turn beneath it.
        alt = [*changes[:3], *fast_clothes]
    return Panel(d, changes, alt)


def contact(plan: SystemPlan, step: Step, index: int) -> Panel:
    d = base(plan, step, index)
    wheel = d.dot("wheel", 450, 265, 130, INK)
    d.dot("wheel-centre", 450, 265, 94, METAL)
    spoke = polygon(d, "spoke", [[444,180],[456,180],[456,350],[444,350]], BLUE)
    d.line("road", [[140, 396], [760, 396]], INK, 10)
    d.text("wheel-label", "Wheel", 120, 180, 40)
    d.line("wheel-pointer", [[220, 190], [330, 230]], INK, 2)
    changes = [transition(spoke, Pose(angle=150))]
    if step.style == "grip":
        arrow = d.arrow("road-force", 480, 425, 140, BLUE)
        d.text("force-label", "Road force on tire", 295, 500, 32)
        changes.append(transition(arrow, Pose(x=35)))
        alt = [changes[0], transition(arrow, Pose(opacity=0), Pose(opacity=0))]
    else:
        pad = d.box("brake-pad", 565, 240, 35, 65, WARM)
        d.text("brake-label", "Brake pad", 625, 240, 32)
        d.text("heat-label", "Motion → heat", 300, 480, 36)
        changes.append(transition(pad, Pose(x=-20)))
        alt = [changes[0], transition(pad, Pose(x=25), Pose(x=25))]
    # Wheel body is stable: spinning is indicated by a spoke, never a bouncing tyre.
    del wheel
    return Panel(d, changes, alt)
