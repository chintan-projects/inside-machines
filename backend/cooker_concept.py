"""Authored CE-1 mechanism using the shared teaching and rendering contracts."""

from pydantic import HttpUrl

from .contracts import LessonSpec, Source
from .other_concepts import add_core_labels, complete_concept
from .seed_cooker import cooker
from .teaching_authoring import Drawing, transition
from .teaching_contracts import Pose


def cooker_concept() -> LessonSpec:
    """Separate supplied energy, confinement and control in an electric cooker."""
    spec = cooker()
    spec.version, spec.canonical = 2, "pressure-cooker-ce-1"
    spec.title = spec.question = "Why does trapping steam change cooking?"
    spec.sources.append(
        Source(
            title="Instant Pot: frequently asked questions",
            url=HttpUrl("https://instantpot.com/pages/frequently-asked-questions"),
            supports="The clicking-sound answer identifies heating switching on/off to regulate temperature/pressure; the natural-release answer describes cooling over time.",
        )
    )
    add_core_labels(
        spec,
        [
            ("heater", "Heater", 60, 440),
            ("gasket", "Lid seal", 55, 160),
            ("regulator", "Regulator", 650, 140),
        ],
    )
    drawings: list[Drawing] = []
    changes: list[list[dict[str, object]]] = []
    for i in range(4):
        d = Drawing(f"cook{i}-")
        d.text(
            "heading",
            [
                "The heater supplies energy",
                "A seal limits vapor escape",
                "Controls manage heat supply",
                "Energy and confinement work together",
            ][i],
            80,
            55,
            34,
        )
        d.box("vessel", 215, 175, 380, 245, "#9faea2")
        d.box("space", 232, 190, 347, 210, "#f3f2ee")
        d.box("water", 238, 300, 335, 95, "#7eafb4")
        heater = d.box("heater", 250, 423, 300, 20, "#cda46f")
        seal = d.box("seal", 215, 167, 380, 13, "#6e8171")
        d.arrow("heat", 95, 365, 100, "#ca8c54")
        d.text("heat-label", "Heat in", 65, 320, 30)
        d.box("control", 660, 235, 135, 65, "#dce3d5")
        contact = d.line("contact", [[675, 270], [770, 270]], "#526b63", 7)
        power = d.box("power", 620, 425, 150, 12, "#b99461")
        d.text("power-label", "Power", 650, 465, 28)
        d.text("control-label", "Control", 650, 330, 30)
        bubbles = [d.dot(f"vapor-{j}", 280 + j * 55, 282, 9, "#8daeb0") for j in range(5)]
        moving = [transition(b, Pose(y=-50), Pose(y=35, opacity=0.15)).model_dump() for b in bubbles]
        if i == 0:
            moving.append(transition(heater, Pose(fill="#d7834a"), Pose(fill="#cda46f")).model_dump())
        if i == 1:
            moving.append(transition(seal, Pose(y=0), Pose(y=-50)).model_dump())
        if i == 2:
            moving.extend(
                [
                    transition(contact, Pose(angle=-25)).model_dump(),
                    transition(power, Pose(opacity=0.15)).model_dump(),
                    transition(heater, Pose(fill="#9faea2"), Pose(fill="#d7834a")).model_dump(),
                ]
            )
        drawings.append(d)
        changes.append(moving)
    rows = [
        (
            "Supply heat",
            "The heater transfers energy into the vessel and liquid. Some liquid becomes vapor. The energy comes from the heater; pressure is not a separate source of heat.",
            "heater",
            1,
            "Section 1.5: latent heat and phase change",
        ),
        (
            "Contain vapor",
            "A sealed lid limits vapor escape. As the contents heat, pressure can rise. Water then boils at a higher temperature than in an open pot at the same ambient pressure. The seal changes the condition, not the source of energy.",
            "gasket",
            1,
            "Section 1.5: boiling and pressure dependence",
        ),
        (
            "Control the supply",
            "An electric cooker's controller manages heating while pressure regulation and safety features constrain operation. Higher cooking temperature changes the rate of many cooking processes. Exact controls and limits depend on the appliance.",
            "regulator",
            2,
            "FAQ: clicking sound means heating turns on/off to regulate temperature/pressure; contact is a conceptual control schematic, not a wiring diagram",
        ),
        (
            "Put it together",
            "The heater supplies energy, the seal restricts escape, and the controls manage operation. Remove confinement and the same pressure-cooker condition cannot be maintained. Switch off heat and stored energy remains; cooling and condensation take time.",
            "heater",
            1,
            "Section 1.5: energy, condensation and vapor pressure",
        ),
    ]
    final = drawings[-1]
    return complete_concept(
        spec,
        drawings,
        changes,
        rows,
        {
            "goal": "Explain heat supply, confinement and boiling conditions, then predict why pressure does not vanish when heating stops.",
            "misconception": "Pressure itself supplies heat or disappears immediately with heater power.",
            "core": ["heater", "gasket", "regulator"],
            "operation": "controlled",
            "operation_note": "Heating, vapor formation and control interact; the chapters isolate their roles rather than prescribe operating steps.",
            "invariants": [
                "The heater supplies energy; pressure does not create energy.",
                "Switching off power does not instantly remove stored heat or pressure.",
            ],
            "prediction": {
                "prompt": "What explains the hotter cooking condition in a pressure cooker?",
                "choices": [
                    "Pressure creates extra energy",
                    "Supplied heat plus an altered boiling condition",
                ],
                "correct": 1,
                "explanation": "The heater supplies energy. Confinement allows pressure to rise, changing the temperature at which the liquid boils.",
                "reasoning": ["Energy comes from the heater", "Pressure changes the boiling condition"],
                "misconception": "Pressure is itself an additional heater.",
            },
            "transfer": {
                "prompt": "When heating stops, does all the pressure disappear immediately?",
                "choices": ["Yes, pressure follows the switch", "No, stored heat remains"],
                "correct": 1,
                "explanation": "The contents retain energy. Cooling and condensation take time, so switching off heat does not establish that pressure is gone. Use the actual manual for operation.",
                "reasoning": ["Stored thermal energy remains", "Cooling/condensation are gradual"],
                "misconception": "No electrical input means instantly no pressure.",
            },
            "teach_back": "What different jobs do the heater, seal and controls do?",
            "teach_back_reasoning": [
                "The heater supplies energy",
                "The seal restricts vapor escape",
                "Controls manage heating and pressure-related operation",
            ],
            "scenarios": [
                {
                    "id": "sealed",
                    "label": "Confined vapor",
                    "beat": "beat-3",
                    "kind": "qualitative",
                    "context": "none",
                    "outcome": "The boiling condition can shift",
                    "explanation": "With continued heating and limited vapor escape, pressure can be maintained above ambient. Exact conditions depend on the system.",
                    "claims": ["claim-1", "claim-3"],
                    "changes": [],
                },
                {
                    "id": "open",
                    "label": "Open-pot comparison",
                    "beat": "beat-3",
                    "kind": "qualitative",
                    "context": "none",
                    "outcome": "Vapor escapes toward ambient pressure",
                    "explanation": "This thought experiment changes confinement. An open vessel does not maintain the same pressure-cooker condition at the same ambient pressure.",
                    "claims": ["claim-1"],
                    "changes": [
                        transition(final.prefix + "seal", Pose(y=-55, opacity=0)).model_dump(),
                        *[
                            transition(
                                final.prefix + f"vapor-{j}", Pose(y=-135, opacity=0.1), Pose(y=35, opacity=1)
                            ).model_dump()
                            for j in range(5)
                        ],
                    ],
                },
            ],
        },
        states=[
            ("Energy", "Electrical input", "Thermal energy in contents"),
            ("Vapor", "Escape is restricted", "Pressure can rise with heating"),
            ("Heating", "Supplied electrical energy", "Managed by the controller"),
            ("Condition", "Limited vapor escape", "Higher boiling temperature possible"),
        ],
    )
