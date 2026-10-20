"""Authored CE-1 mechanism using the shared teaching and rendering contracts."""

from pydantic import HttpUrl

from .contracts import LessonSpec, Source
from .other_concepts import add_core_labels, complete_concept
from .seed_washer import washer
from .teaching_authoring import Drawing, transition
from .teaching_contracts import Pose


def washer_concept() -> LessonSpec:
    """Differentiate cleaning by tumbling from extracting water during spin."""
    spec = washer()
    spec.version, spec.canonical = 2, "washing-machine-ce-1"
    spec.title = spec.question = "Why wash slowly, then spin quickly?"
    spec.sources.append(
        Source(
            title="Whirlpool: parts of a washing machine",
            url=HttpUrl("https://www.whirlpool.com/blog/washers-and-dryers/parts-of-a-washing-machine.html"),
            supports="Sections 1–2 describe drainage; section 4 identifies the perforated inner drum and outer tub; section 6 describes the motor.",
        )
    )
    spec.parts = [p for p in spec.parts if p.id not in ("water", "clothes")]
    add_core_labels(
        spec, [("drum", "Drum", 55, 165), ("motor", "Motor", 65, 440), ("pump", "Drain pump", 665, 420)]
    )
    spec.assumptions.append(
        "The static cutaway locates the parts. Insets show qualitative lift/drop and water paths, not measured fabric dynamics or a complete cycle simulation."
    )
    drawings: list[Drawing] = []
    changes: list[list[dict[str, object]]] = []
    for i in range(4):
        d = Drawing(f"wash{i}-")
        d.text(
            "heading",
            [
                "Lift, then let gravity act",
                "Water passes through holes",
                "The pump moves collected water",
                "Different speeds, different jobs",
            ][i],
            105,
            65,
            34,
        )
        d.dot("outer-tub", 390, 285, 160, "#99b3ab")
        d.dot("drum", 390, 285, 140, "#e3e8df")
        for j, (x, y) in enumerate(
            [(300, 185), (390, 155), (480, 185), (520, 280), (480, 380), (390, 415), (300, 380), (260, 280)]
        ):
            d.dot(f"hole-{j}", x, y, 6, "#758e84")
        fabric = d.box("fabric", 335, 230, 75, 55, "#c89d70")
        water = d.dot("water", 440, 330, 11, "#609da8")
        d.line("drain-path", [[390, 445], [390, 480], [650, 480], [730, 380]], "#5e8c91", 8)
        d.dot("pump", 620, 480, 24, "#819b8e")
        impeller = d.box("pump-impeller", 601, 475, 38, 10, "#ecede6")
        d.text("pump-label", "Pump", 590, 370, 30)
        if i == 0:
            movement = transition(fabric, Pose(x=20, y=100), Pose(x=-45, y=-50))
        elif i == 1:
            movement = transition(water, Pose(x=-50, y=100), Pose())
        elif i == 2:
            movement = transition(
                water,
                Pose(x=290, y=50),
                Pose(x=-50, y=100),
                via=[Pose(x=-50, y=150), Pose(x=180, y=150), Pose(x=210, y=150)],
            )
        else:
            movement = transition(fabric, Pose(x=110, y=0), Pose(x=-45, y=70))
        drawings.append(d)
        changes.append(
            [movement.model_dump(), transition(impeller, Pose(angle=120 if i == 2 else 0)).model_dump()]
        )
    rows = [
        (
            "Lift and drop",
            "At a washing speed, the drum lifts wet fabric and gravity makes it fall. That tumbling moves clothes against water, detergent and one another, loosening soil. Faster motion is not automatically better washing.",
            "drum",
            0,
            "How a washing machine works, Step 3; front-load versus top-load wash action",
        ),
        (
            "Let water pass",
            "The inner drum is perforated. During spin, the drum constrains the clothes to a circular path while water can move outward through the holes into the stationary outer tub. The illustration is qualitative; no extraction rate is calculated.",
            "drum",
            1,
            "Section 4: Tub/drum; circular-path explanation is a qualitative mechanics inference from the perforated geometry",
        ),
        (
            "Pump it away",
            "Water collected outside the drum still needs to leave the machine. A drain pump moves it through the drain hose. The normal sequence drains the tub before high-speed spin; spinning in a full tub is not the model shown here.",
            "pump",
            1,
            "Sections 1–2: Water pump and drain pipe; normal drain/spin order from the cycle source",
        ),
        (
            "Reunite the cycle",
            "The motor supplies the drum's motion, the holes give water a path out, and the pump carries it away. Slow tumbling and fast spin serve different jobs. At sufficient speed clothes follow the drum instead of repeatedly falling through it.",
            "motor",
            0,
            "Step 3 versus Step 5: wash action and spin extraction",
        ),
    ]
    final = drawings[-1]
    concept = complete_concept(
        spec,
        drawings,
        changes,
        rows,
        {
            "goal": "Explain the different jobs of tumbling, perforations and pumping, then predict what happens without lift/drop.",
            "misconception": "Increasing speed always improves the washing action.",
            "core": ["drum", "motor", "pump"],
            "operation": "controlled",
            "operation_note": "A controller sequences washing, draining, rinsing and spinning; these are not all active together.",
            "invariants": [
                "The inner drum turns inside a stationary outer tub.",
                "Normal high-speed spin follows draining.",
            ],
            "prediction": {
                "prompt": "Would keeping clothes against the drum wall at high speed always give better washing?",
                "choices": ["Yes, faster always washes better", "No, it changes the action"],
                "correct": 1,
                "explanation": "Tumbling needs fabric to lift and fall. At sufficient speed the fabric follows the drum. Fast spin has a different job: extracting water.",
                "reasoning": ["Cleaning uses tumbling", "Spin removes water"],
                "misconception": "All drum motion has the same cleaning purpose.",
            },
            "transfer": {
                "prompt": "If fabric follows the drum without falling, does it still get the same lift-and-drop action?",
                "choices": ["Yes, it tumbles more", "No, it follows the drum"],
                "correct": 1,
                "explanation": "It no longer repeatedly lifts and drops through the drum. That is useful during spin extraction, but different from tumbling during washing.",
                "reasoning": [
                    "Following the wall removes the repeated drop",
                    "Washing and spin extraction have different jobs",
                ],
                "misconception": "Faster rotation simply increases the same washing action.",
            },
            "teach_back": "Why does a washer need a drum, holes and a pump rather than just a fast motor?",
            "teach_back_reasoning": [
                "The drum moves fabric",
                "Holes let water reach the outer tub",
                "The pump removes collected water",
            ],
            "scenarios": [
                {
                    "id": "fast",
                    "label": "Fast spin",
                    "beat": "beat-3",
                    "kind": "qualitative",
                    "context": "none",
                    "outcome": "Fabric follows the wall",
                    "explanation": "At sufficient speed, clothes follow the drum and water can pass through its holes; the pump removes collected water.",
                    "claims": ["claim-3"],
                    "changes": [],
                },
                {
                    "id": "slow",
                    "label": "Slow tumble",
                    "beat": "beat-3",
                    "kind": "qualitative",
                    "context": "none",
                    "outcome": "Fabric lifts and falls",
                    "explanation": "At a tumbling speed, gravity makes lifted fabric fall. This is the washing action, not high-speed extraction.",
                    "claims": ["claim-0", "claim-3"],
                    "changes": [
                        transition(
                            final.prefix + "fabric", Pose(x=20, y=100), Pose(x=-45, y=-50)
                        ).model_dump()
                    ],
                },
            ],
        },
        states=[
            ("Fabric motion", "Lifted by the drum", "Falls under gravity"),
            ("Water path", "Within fabric/drum", "Collected in the outer tub"),
            ("Water location", "Outer tub", "Through the hose to the drain"),
            ("Drum regime", "Slow tumbling", "Fast spin extraction"),
        ],
    )

    assert concept.teaching is not None
    for index in (1, 3):
        concept.teaching.claims[index].scope = "inference"
        concept.teaching.claims[
            index
        ].limitation += " The circular-path explanation is inferred from basic mechanics, not a measured manufacturer spin threshold."
    return concept
