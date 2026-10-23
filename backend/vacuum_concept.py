"""Authored bagged-vacuum teaching candidate; shared player/state/publication."""

from .contracts import LessonSpec
from .other_concepts import complete_concept
from .section_assets import vacuum_art_fingerprint
from .teaching_authoring import transition
from .teaching_contracts import Claim, Pose
from .vacuum_graphics import bag_section, fan_section, inlet_section, overview

CANONICAL = "bagged-vacuum-ce-5"


def vacuum_concept() -> LessonSpec:
    """Explain moving air, then test why a spinning motor is insufficient."""
    parts = overview()
    for p in parts:
        if p.id in ("fan", "nozzle", "bag"):
            p.name = {"fan": "Fan", "nozzle": "Floor nozzle", "bag": "Porous bag"}[p.id]
    spec = LessonSpec.model_validate(
        {
            "version": 1,
            "canonical": CANONICAL,
            "title": "What actually lifts the dirt?",
            "question": "What actually lifts the dirt?",
            "aliases": ["vacuum cleaner", "bagged vacuum", "household vacuum cleaner"],
            "family": "Inside a bagged vacuum cleaner",
            "category": "Home",
            "accent": "#2676df",
            "summary": "A powered fan moves air. That moving air carries dirt from the floor into a bag that lets air pass through.",
            "big_idea": "A turning motor is only useful for pickup when air can move through the whole path.",
            "assumptions": [
                "Generic bagged canister with the collection bag before the fan. Not an exact product or a repair guide.",
                "Sectioned geometry, openings and arrows are enlarged for explanation; not manufacturing dimensions, actual particles or computed flow rates.",
                "Bag filtration is incomplete; additional filters, cooling bypasses and safety controls are omitted. No HEPA performance is claimed.",
            ],
            "sources": [
                {
                    "title": "Dyson: vacuum cleaner principles",
                    "url": "https://www.dyson.com/vacuum-cleaners.asp",
                    "supports": "FAQ on how vacuums work: a low-pressure zone inside the machine causes outside air and loose dirt to enter. General principle only, not this bagged design.",
                },
                {
                    "title": "Dyson: Filtration at Dyson",
                    "url": "https://www.dyson.com/discover/innovation/behind-the-invention/filtration-at-dyson",
                    "supports": "It started with a cyclone: a porous vacuum bag passes air and retains dust; dust loading clogs the bag. No product-specific filtration percentage is used.",
                },
                {
                    "title": "Miele: motor, floorhead and airflow",
                    "url": "https://www.mieleusa.com/c/vacuum-cleaner-insights-how-to-choose-a-miele-vacuum-cleaner-with-outstanding-suction-power-7561.htm",
                    "supports": "Explains the balance of efficient motor, sealed floorhead and streamlined airflow. The section drawing illustrates qualitative mechanical work, not a specific motor.",
                },
            ],
            "parts": [p.model_dump() for p in parts],
            "stages": [
                {
                    "title": "Start the fan",
                    "explanation": "The motor turns the fan, transferring motion to the surrounding air.",
                    "narration": "The motor turns the fan, transferring motion to the surrounding air.",
                    "duration": 12,
                    "parts": ["fan"],
                    "cause": "A powered fan transfers mechanical energy to air.",
                }
            ]
            * 3,
            "questions": [
                {
                    "question": "Does the motor pull on the dirt directly?",
                    "answer": "No. The motor turns the fan. Moving air through the nozzle carries loose dirt; the motor does not reach out and pull individual dirt particles.",
                    "stage": 0,
                    "part": "fan",
                },
                {
                    "question": "Why does air enter at the floor?",
                    "answer": "The fan maintains lower pressure on its inlet side while the path is open. Higher-pressure room air flows into the nozzle, carrying loose dirt along with it.",
                    "stage": 1,
                    "part": "nozzle",
                },
                {
                    "question": "Does the bag stop all particles?",
                    "answer": "No. This generic bag retains some dirt while air passes through its porous wall. Real machines may need additional filters and seals, and this lesson makes no HEPA claim.",
                    "stage": 2,
                    "part": "bag",
                },
            ],
            "prediction": "If the nozzle were completely sealed, could the running motor keep carrying dirt through it?",
            "prediction_answer": "No sustained airflow can pass through a completely sealed opening. A running motor does not guarantee air movement through that path; real machines may have separate bypasses.",
        }
    )
    spec.version = 2
    sections = [fan_section(), inlet_section(), bag_section()]
    drawings = [d for d, _ in sections]
    changes = [c for _, c in sections]
    rows = [
        (
            "The fan gives air a push",
            "The motor turns the fan. Its blades transfer energy to air, maintaining a pressure difference when the air path is open.",
            "fan",
            2,
            "Motor, floorhead and airflow balance; energy-transfer explanation is a qualitative mechanics inference.",
        ),
        (
            "Room air carries dirt inside",
            "With lower pressure inside the open nozzle, room air flows in. This moving air carries loose dirt through the hose to the bag.",
            "nozzle",
            0,
            "FAQ: How do vacuums work? Low pressure inside, air and loose dirt enter from outside.",
        ),
        (
            "The bag keeps dirt. Air moves on.",
            "The porous bag retains some dirt while air passes through its wall toward the fan and outlet. The nozzle, hose, bag and powered fan form one connected path.",
            "bag",
            1,
            "It started with a cyclone: porous bag, trapped dust, clogging and reduced suction.",
        ),
    ]
    final = drawings[-1]
    restricted = [transition(final.prefix + f"pore-{i}", Pose(fill="#b38d5e")) for i in range(5)]
    for i in range(3):
        restricted.append(transition(final.prefix + f"air-{i}", Pose(x=15, opacity=0.3)))
        restricted.append(transition(final.prefix + f"dust-{i}", Pose(x=10)))
    concept = complete_concept(
        spec,
        list(drawings),
        [[c.model_dump() for c in group] for group in changes],
        rows,
        {
            "goal": "Trace motor to fan to moving air to carried dirt, then explain why clogging the bag weakens pickup.",
            "misconception": "If the motor is turning, dirt pickup must be unchanged even when the air path is blocked.",
            "core": ["fan", "nozzle", "bag"],
            "operation": "simultaneous",
            "operation_note": "One open path: nozzle → hose → porous bag → fan → outlet. The motor supplies work throughout; these views show simultaneous operation. Arrows show paths, not measured speed.",
            "invariants": [
                "The bag sits before the fan in this generic design.",
                "A sealed opening cannot support sustained throughflow through that opening.",
                "A turning motor alone does not establish useful airflow.",
            ],
            "prediction": {
                "prompt": spec.prediction,
                "choices": ["Yes, the motor is still on", "No, the air path is closed"],
                "correct": 1,
                "explanation": spec.prediction_answer,
                "reasoning": ["Moving air carries dirt", "A sealed path prevents throughflow"],
                "misconception": "A running motor guarantees pickup.",
            },
            "transfer": {
                "prompt": "The bag is clear, but the hose is kinked shut. Does a turning motor guarantee dirt pickup?",
                "choices": ["Yes, the bag is clear", "No, the air path is blocked"],
                "correct": 1,
                "explanation": "A kinked-shut hose blocks this air path even with a clear bag. Without throughflow at the nozzle, moving air cannot keep carrying dirt inside. A turning motor alone does not guarantee pickup.",
                "reasoning": ["The hose can also restrict the air path", "Moving air is what carries dirt"],
                "misconception": "Motor motion alone determines dirt pickup.",
            },
            "teach_back": "Explain how a motor at one end can help lift dirt from the floor at the other.",
            "teach_back_reasoning": [
                "The motor drives a fan",
                "The pressure difference drives air through an open path",
                "Air carries dirt; the bag retains some dirt and passes air",
            ],
            "scenarios": [
                {
                    "id": "open",
                    "label": "Clear bag",
                    "beat": "beat-2",
                    "kind": "qualitative",
                    "context": "none",
                    "outcome": "Air passes through; dirt stays behind",
                    "explanation": "Follow the blue air arrows through the porous wall. The brown dirt markers remain inside. This does not claim complete filtration.",
                    "claims": ["claim-2"],
                    "changes": [],
                },
                {
                    "id": "clogged",
                    "label": "Clog the bag",
                    "beat": "beat-2",
                    "kind": "qualitative",
                    "context": "none",
                    "outcome": "The fan turns, but throughflow is restricted",
                    "explanation": "Dust blocks more of the porous wall. Air markers now move much less while the fan still turns. This is a qualitative comparison; actual flow depends on the fan and the whole path.",
                    "claims": ["claim-2"],
                    "changes": [c.model_dump() for c in restricted],
                },
            ],
        },
        states=[
            ("Power → air", "Motor supplies motion", "Fan transfers energy to air"),
            ("Open intake", "Room air and loose dirt", "Air carries dirt into the hose"),
            ("Separation", "Air carrying dirt", "Some dirt retained; air continues"),
        ],
    )
    assert concept.teaching is not None
    concept.teaching.renderer = "authored-sections-v1"
    concept.teaching.renderer_fingerprint = vacuum_art_fingerprint()
    concept.teaching.claims.append(
        Claim(
            id="claim-clog",
            statement="As dust clogs the bag, less air can move through the path even with the motor still turning.",
            source=1,
            locator=concept.teaching.claims[2].locator,
            scope="generic",
            limitation="Qualitative comparison; no flow rate or filtration percentage is claimed.",
        )
    )
    concept.teaching.scenarios[1].claims = ["claim-clog"]
    for i, (short, action, bridge) in enumerate(
        [
            (
                "Move air",
                "Turn the fan",
                "Like a hand fan, powered blades transfer motion to the surrounding air.",
            ),
            (
                "Carry dirt",
                "Follow the air",
                "An open doorway lets a breeze pass. The nozzle gives room air a way in.",
            ),
            (
                "Keep dirt",
                "Trace the whole path",
                "Like a strainer with much finer openings, the bag lets air through while retaining some dirt.",
            ),
        ]
    ):
        beat = concept.teaching.beats[i]
        beat.short, beat.action, beat.bridge = short, action, bridge
    concept.teaching.claims[0].scope = "inference"
    concept.teaching.claims[
        0
    ].limitation += " The blade/shaft section is an illustrative mechanics model, not a manufacturer's measured fan geometry."
    return LessonSpec.model_validate(concept.model_dump())
