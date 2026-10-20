"""Trusted job relationships for recombining the core; never literal pipe layouts."""

from ..seed_geometry import part
from ..teaching_authoring import Drawing, transition
from ..teaching_contracts import Pose
from .panels import BLUE, INK, METAL, WARM, Panel
from .plans import SystemPlan

# source, destination, relationship, transfer kind. Control links are not fluid.
LINKS: dict[str, tuple[tuple[int, int, str, str], ...]] = {
    "car": ((0,1,"Engine turns drivetrain","work"),(1,2,"Torque reaches tires","work"),(3,2,"Brakes oppose rotation","work")),
    "gpu": ((0,2,"Program defines work","signal"),(1,2,"Memory supplies inputs","signal"),(2,3,"Results are stored","signal")),
    "refrigerator": ((0,1,"Cold-coil vapor reaches compressor","fluid"),(1,2,"Hot vapor reaches warm coil","fluid"),(2,3,"Liquid reaches restriction","fluid"),(3,0,"Low-pressure mixture returns","fluid")),
    "microwave": ((0,1,"Microwaves enter cavity","work"),(1,2,"Food absorbs energy","work"),(3,2,"Turntable moves food","work")),
    "dishwasher": ((0,1,"Inlet supplies wash pool","fluid"),(1,2,"Pump feeds spray jets","fluid"),(2,3,"Used water reaches filter","fluid"),(3,1,"Filtered water recirculates","fluid")),
    "induction-cooktop": ((0,1,"Field transfers energy into pan","work"),(1,2,"Pan transfers heat into food","work")),
    "electric-oven": ((0,1,"Elements heat cavity","work"),(1,2,"Sensor observes temperature","signal"),(2,0,"Control cycles element input","signal"),(3,1,"Fan moves cavity air","work")),
    "washing-machine": ((0,1,"Inlet supplies wash water","fluid"),(1,2,"Used water reaches drain pump","fluid")),
    "vacuum-cleaner": ((1,2,"Nozzle and hose carry dirt","fluid"),(2,0,"Filtered air reaches fan","fluid"),(0,3,"Driven air leaves exhaust","fluid")),
    "table-fan": ((0,1,"Motor turns blades","work"),(1,2,"Blades give air momentum","work")),
    "clothes-dryer": ((0,1,"Heated air meets fabric","fluid"),(1,2,"Humid air reaches exhaust","fluid")),
    "air-conditioner": ((0,1,"Vapor returns to compressor","fluid"),(1,2,"Hot vapor reaches outdoor coil","fluid"),(2,3,"Liquid reaches expansion device","fluid"),(3,0,"Cold mixture feeds indoor coil","fluid")),
    "electric-kettle": ((0,1,"Heater supplies energy to water","work"),(1,2,"Steam reaches control","fluid"),(2,0,"Control disconnects heating","signal")),
    "pressure-cooker": ((0,1,"Heater adds energy to contents","work"),(1,2,"Feedback reaches control","signal"),(2,0,"Controller manages heating","signal")),
    "espresso-machine": ((0,1,"Pump delivers water to heater","fluid"),(1,2,"Hot water reaches coffee bed","fluid"),(2,3,"Coffee solution reaches cup","fluid")),
    "water-heater": ((0,1,"Element heats stored water","work"),(2,1,"Supply replaces drawn water","fluid"),(1,2,"Hot water leaves top outlet","fluid"),(1,3,"Sensor observes temperature","signal"),(3,0,"Thermostat manages heater","signal")),
    "heat-pump": ((1,3,"Hot vapor reaches reversing valve","fluid"),(3,2,"Heating route feeds indoor coil","fluid"),(2,4,"Liquid reaches expansion device","fluid"),(4,0,"Cold supply reaches outdoor coil","fluid"),(0,3,"Vapor returns to valve","fluid"),(3,1,"Return reaches compressor","fluid")),
    "toilet": ((0,1,"Tank releases water to bowl","fluid"),(2,0,"Fill valve restores tank water","fluid")),
    "sink-trap": ((0,1,"Sink water enters retained seal","fluid"),(1,2,"Displaced water reaches drain","fluid")),
    "faucet": ((0,1,"Supply reaches cartridge","fluid"),(1,2,"Openings feed mixed outlet","fluid")),
}


def reunion(plan: SystemPlan, index: int) -> Panel:
    """Label every component and reconnect jobs without claiming a physical cutaway."""
    d = Drawing(f"c{index}-")
    d.text("title", "The connected jobs", 60, 25, 40)
    d.text("scope", "System map · not physical layout", 60, 75, 30)
    for i, name in enumerate(plan.core):
        y = 120 + i*74
        d.box(f"node-{i}", 55, y-10, 605, 68, "#edf2f7")
        d.text(f"name-{i}", name, 75, y, 36)
        d.dot(f"port-{i}", 660, y+25, 7, METAL)
    changes = []
    colors = {"fluid":BLUE,"work":WARM,"signal":INK}
    for j, (a,b,_label,kind) in enumerate(LINKS[plan.id]):
        ya,yb,x = 145+a*74,145+b*74,705+j*24
        points = [[660.0, float(ya)], [float(x), float(ya)], [float(x), float(yb)], [660.0,float(yb)]]
        d.line(f"link-{j}", points, colors[kind], 4)
        d.parts.append(part(d.prefix+f"direction-{j}", "Transfer direction", "Direction of this declared job relationship, not a literal pipe layout.",
                            "polygon", 660, yb-8, 20, 16, points=[[660,yb],[680,yb-8],[680,yb+8]],
                            color=colors[kind], stroke=colors[kind], layer=len(d.parts)))
        marker = d.dot(f"transfer-{j}", 660, ya, 6, colors[kind])
        changes.append(transition(marker, Pose(y=yb-ya), via=[Pose(x=x-660),Pose(x=x-660,y=yb-ya)]))
    d.text("legend", "Blue: flow · amber: energy · dark: control/data", 55, 495, 28)
    return Panel(d, changes, list(changes))
