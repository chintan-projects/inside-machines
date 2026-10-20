"""Original schematic insets: see a physical change rather than a highlighted shell."""

from .contracts import Part
from .teaching_authoring import Drawing, transition
from .teaching_contracts import Change, Pose


def ac_graphics() -> tuple[list[Part], list[list[str]], list[list[Change]], list[Change]]:
    """Author six linked visual experiments and the sealed-room counterfactual."""
    drawings: list[Drawing] = []
    changes: list[list[Change]] = []
    d = Drawing("intro-")
    d.text("warm-label", "Warmer object", 100, 110, 36)
    d.text("cold-label", "Cooler object", 530, 110, 36)
    d.box("warm", 100, 210, 320, 175, "#d99a70")
    d.box("cold", 420, 210, 320, 175, "#91bdc0")
    heat = d.arrow("heat", 340, 290, 180)
    d.text("heat-label", "Heat flows warmer → cooler", 200, 445, 32)
    drawings.append(d)
    changes.append([transition(heat, Pose(x=30), Pose(x=-35))])

    for name, condensing in (("pickup-", False), ("release-", True)):
        d = Drawing(name)
        d.text("heading", "Inside the outdoor coil" if condensing else "Inside the indoor coil", 205, 40, 38)
        d.box("tube-wall", 130, 205, 640, 160, "#a7b7a9")
        d.box("inside-tube", 145, 222, 610, 126, "#f3f2ee")
        fluid = d.box("liquid", 150, 267, 600, 76, "#78adb3")
        d.text("wall-label", "Tube wall", 330, 385, 30)
        d.text(
            "state-label", "Vapor becomes liquid" if condensing else "Liquid boils into vapor", 190, 440, 32
        )
        heat = d.arrow("heat", 650 if condensing else 30, 285, 190)
        d.text("heat-label", "Heat leaves the fluid" if condensing else "Heat enters the fluid", 230, 95, 30)
        beat_changes = (
            [transition(fluid, Pose(sy=1, y=0), Pose(sy=0.08, y=34))]
            if condensing
            else [transition(fluid, Pose(sy=0.08, y=34))]
        )
        beat_changes.append(
            transition(heat, Pose(x=10 if condensing else 20), Pose(x=-20 if condensing else -10))
        )
        for i in range(8):
            bubble = d.dot(f"vapor-{i}", 190 + i * 74, 245, 10, "#cfaa83" if condensing else "#719da5")
            beat_changes.append(
                transition(bubble, Pose(y=25, opacity=0), Pose())
                if condensing
                else transition(bubble, Pose(y=-12, opacity=1), Pose(y=50, opacity=0))
            )
        drawings.append(d)
        changes.append(beat_changes)

    d = Drawing("compress-")
    d.text("heading", "Work compresses the vapor", 165, 40, 38)
    d.box("cylinder", 170, 180, 550, 210, "#a9bbb0")
    d.box("chamber", 190, 199, 510, 171, "#f3f2ee")
    gas = d.box("gas", 195, 204, 460, 160, "#9bbfc3")
    piston = d.box("piston", 655, 201, 30, 168, "#657f70")
    rod = d.box("rod", 685, 273, 120, 25, "#a5b6a5")
    work = d.arrow("electric-work", 85, 135, 125, "#ad8752")
    d.text("work-label", "Electrical work", 90, 105, 30)
    d.text("schematic", "Compression principle · internals vary", 160, 435, 28)
    comp_changes = [
        transition(gas, Pose(sx=0.5, x=-115, fill="#d5946b"), Pose(fill="#9bbfc3")),
        transition(piston, Pose(x=-230)),
        transition(rod, Pose(x=-230)),
        transition(work, Pose(x=50)),
    ]
    for i in range(8):
        x, y = 230 + (i % 4) * 115, 240 + (i // 4) * 85
        marker = d.dot(f"vapor-{i}", x, y, 10)
        comp_changes.append(
            transition(marker, Pose(x=-(x - 195) * 0.5, fill="#bf7548"), Pose(fill="#72a9ad"))
        )
    # Insert compression before heat rejection, preserving the conceptual dependency.
    drawings.insert(2, d)
    changes.insert(2, comp_changes)

    d = Drawing("valve-")
    d.text("heading", "A restriction lowers pressure", 130, 80, 36)
    d.box("pipe", 90, 205, 720, 140, "#b9a07a")
    d.box("fluid", 102, 218, 695, 114, "#d4b894")
    downstream = d.box("downstream-liquid", 455, 218, 340, 114, "#93b9be")
    d.box("throat-top", 403, 205, 48, 49, "#7c8170")
    d.box("throat-bottom", 403, 288, 48, 57, "#7c8170")
    d.text("liquid-label", "Liquid", 160, 150, 34)
    d.text("mixture-label", "Liquid + vapor", 500, 150, 34)
    d.text("valve-label", "Expansion valve", 288, 380, 34)
    d.text("limit", "Pressure reduction, not heat removal", 140, 443, 28)
    valve_changes: list[Change] = [transition(downstream, Pose(fill="#93b9be"), Pose(fill="#d4b894"))]
    for i in range(6):
        marker = d.dot(f"fluid-{i}", 215 + (i % 3) * 48, 247 + (i // 3) * 50, 9, "#b59062")
        valve_changes.append(
            transition(
                marker,
                Pose(x=300, y=(-12 if i % 2 else 12), sx=1.6, sy=1.6, fill="#659ca7"),
                Pose(fill="#b59062"),
                via=[Pose(x=427 - (215 + (i % 3) * 48), y=271 - (247 + (i // 3) * 50), fill="#b59062")],
            )
        )
    drawings.append(d)
    changes.append(valve_changes)

    d = Drawing("whole-")
    d.text("heading", "Account for all the energy", 160, 65, 38)
    wash = d.box("room", 80, 140, 325, 245, "#bed4cd")
    d.text("room-label", "Room", 175, 160, 36)
    taken = d.arrow("room-heat", 180, 245, 165)
    work = d.arrow("work", 390, 330, 130, "#ad8752")
    rejected = d.arrow("heat-released", 550, 245, 195)
    d.text("work-label", "+ electrical work", 350, 385, 30)
    d.text("out-label", "Heat released", 550, 155, 32)
    d.text("balance", "Heat out = room heat + supplied work", 100, 455, 30)
    drawings.append(d)
    changes.append(
        [
            transition(taken, Pose(x=45)),
            transition(work, Pose(y=-65)),
            transition(rejected, Pose(x=30)),
            transition(wash, Pose(fill="#dae6de"), Pose(fill="#bed4cd")),
        ]
    )
    counterfactual = [
        transition(rejected, Pose(x=-370, y=65, angle=180)),
        transition(work, Pose(x=-140, y=-40)),
        transition(wash, Pose(fill="#e1b28c"), Pose(fill="#bed4cd")),
    ]
    return (
        [p for drawing in drawings for p in drawing.parts],
        [[p.id for p in drawing.parts] for drawing in drawings],
        changes,
        counterfactual,
    )
