"""Authored AC teaching benchmark: connected hardware and a six-chapter explanation."""

from .ac_craft_geometry import ac_parts
from .contracts import LessonSpec
from .seed_geometry import stage

CANONICAL = "air-conditioner-craft"
CORE = ("evaporator", "compressor", "condenser", "expansion")


def aircon_craft() -> LessonSpec:
    """Use a generic cooling-mode split system without invented operating readings."""
    pieces = ac_parts()
    chapters = [
        stage(
            "Start with the two sides",
            "An AC moves heat out of a room. The indoor and outdoor fans move separate air streams. Only refrigerant circulates between them: a fluid that carries heat as it changes between liquid and gas. It stays inside sealed tubing.",
            "Heat needs a carrier to travel from the room to the outdoors.",
            list(CORE),
            narration="An air conditioner moves heat out of your room. These are its four working parts. The indoor and outdoor fans move separate air streams. Refrigerant is the fluid that carries heat between them, changing between liquid and gas inside sealed tubing.",
        ),
        stage(
            "1 · Room heat enters the indoor coil",
            "The indoor fan passes room air over a colder coil. Inside its tube, low-pressure refrigerant absorbs that heat and boils from liquid into vapor, its gaseous form. Cooler air returns to your room.",
            "Heat flows from warmer room air into the colder refrigerant. Boiling absorbs energy.",
            ["evaporator", "blower", "warm-air", "cool-air", "absorbed-heat"],
            narration="Start at the indoor coil, also called the evaporator. Room air gives heat to the colder refrigerant inside. The refrigerant boils into vapor, its gaseous form, as it absorbs energy. The same room air returns cooler.",
        ),
        stage(
            "2 · The compressor adds work",
            "The electric compressor takes in vapor from the indoor coil. It raises the vapor's pressure and temperature, making it hotter than the outdoor air. The refrigerant is still vapor here.",
            "Electrical work makes the refrigerant hot enough to release heat outdoors, even on a hot day.",
            ["compressor", "suction", "discharge", "power"],
            narration="The vapor reaches the compressor. This electric pump raises its pressure and temperature. Adding work makes the refrigerant hotter than outdoor air, so it can release heat outside. It is still vapor at this point.",
        ),
        stage(
            "3 · The outdoor coil releases heat",
            "Hot vapor enters the outdoor coil. Heat passes into outdoor air, helped by the fan. As the refrigerant loses heat, it condenses into liquid. Its pressure remains high.",
            "Heat flows outward because the refrigerant is hotter than the outdoor air. The rejected heat includes compressor work.",
            ["condenser", "fan", "outdoor-air", "released-heat", "liquid-line"],
            narration="At the outdoor coil, also called the condenser, heat passes from the hot refrigerant into outdoor air. The fan carries that heat away. The vapor condenses into liquid. This rejects both room heat and the energy added by the compressor.",
        ),
        stage(
            "4 · The valve makes a cold mixture",
            "High-pressure liquid reaches a narrow expansion valve. Its pressure drops across the restriction. Some liquid flashes into vapor, cooling the remaining mixture before it enters the indoor coil.",
            "The pressure drop creates a cold, low-pressure mixture that can absorb room heat again.",
            ["expansion", "liquid-line", "return-line", "evaporator"],
            narration="The liquid reaches the expansion valve. This restriction lowers its pressure. Some liquid flashes into vapor, leaving a cold mixture. That mixture returns to the indoor coil, ready to absorb more heat.",
        ),
        stage(
            "Now follow the whole loop",
            "The refrigerant repeats the same loop: indoor coil, compressor, outdoor coil, expansion valve. These processes run continuously in different parts while cooling is on; the chapters do not switch them on one at a time.",
            "The outdoor coil releases room heat plus the electrical work added by the compressor.",
            list(CORE)
            + ["suction", "discharge", "liquid-line", "return-line", "absorbed-heat", "released-heat"],
            narration="Follow the complete loop now. All four processes run together while cooling is on. Refrigerant circulates, while heat moves from the room to the outdoors. The outdoor coil also releases the energy added by the electric compressor.",
        ),
    ]
    states = [
        (
            "Warm room air; a powered cooling system",
            "Room heat carried outdoors through a sealed loop",
            "evaporator",
        ),
        (
            "Cold, low-pressure liquid-and-vapor mixture",
            "Low-pressure vapor carrying absorbed room heat",
            "evaporator",
        ),
        ("Low-pressure vapor + electrical work", "Hotter, high-pressure vapor", "compressor"),
        ("Hot, high-pressure vapor", "High-pressure liquid; heat released outdoors", "condenser"),
        ("High-pressure liquid", "Cold, low-pressure liquid-and-vapor mixture", "expansion"),
        ("Room heat + compressor work", "Heat released outdoors; refrigerant recirculates", "condenser"),
    ]
    for chapter, (incoming, outgoing, focus) in zip(chapters, states, strict=True):
        chapter.input_state, chapter.output_state, chapter.focus = incoming, outgoing, focus
        chapter.source_indices = [0, 2] if focus in ("compressor", "condenser") else [0, 1]
    return LessonSpec.model_validate(
        dict(
            version=1,
            title="How air conditioning moves heat",
            canonical=CANONICAL,
            aliases=["air conditioner", "air conditioning", "AC", "aircon"],
            family="Generic split-system air conditioner",
            question="How does an air conditioner move heat out of a room?",
            summary="Follow a sealed refrigerant loop through four labeled components, and see why heat can move outdoors even on a hot day.",
            big_idea="It carries heat out of your room. It does not bring outdoor air in.",
            category="Home",
            accent="#006d7c",
            assumptions=[
                "Generic split-system cooling mode; the cutaway is a teaching view, not an installation or service diagram.",
                "Processes run simultaneously while cooling is on. Chapter emphasis and moving chevrons show direction, not measured speed.",
                "Colors show qualitative refrigerant states, not measured temperatures or pressures. The compressor's internal pump is not shown.",
                "Humidity removal, controls, superheat/subcooling and refrigerant-specific details are omitted.",
            ],
            sources=[
                {
                    "title": "Carrier: how air conditioners work",
                    "url": "https://www.carrier.com/residential/en/ca/products/air-conditioners/how-do-air-conditioners-work/",
                    "supports": "Supports separate indoor and outdoor air streams, refrigerant phase changes, compressor work and the heat-transfer cycle.",
                },
                {
                    "title": "Carrier: the four essential AC components",
                    "url": "https://www.carrier.com/residential/en/ca/products/air-conditioners/air-conditioning-equipment/",
                    "supports": "Identifies the evaporator, compressor, condenser and expansion valve and their roles in a split system.",
                },
                {
                    "title": "OpenStax: refrigerator and heat-pump energy balance",
                    "url": "https://openstax.org/books/university-physics-volume-2/pages/4-3-refrigerators-and-heat-pumps",
                    "supports": "Explains that heat delivered to the warmer surroundings equals the heat removed from the cold space plus the work supplied to the cycle.",
                },
            ],
            parts=pieces,
            stages=chapters,
            questions=[
                {
                    "question": "Does it bring outside air into the room?",
                    "answer": "In this generic split-system cooling loop, the indoor and outdoor air streams stay separate. Refrigerant transports heat through the connecting tubes. Some installations add a separate ventilation system.",
                    "stage": 0,
                    "part": "evaporator",
                },
                {
                    "question": "Why can heat leave the room on a hot day?",
                    "answer": "The compressor adds electrical work, raising the vapor's pressure and temperature. The outdoor coil can then release heat because its refrigerant is hotter than the outdoor air.",
                    "stage": 2,
                    "part": "compressor",
                },
                {
                    "question": "Is the refrigerant used up?",
                    "answer": "Normally it circulates in a sealed loop, repeatedly changing state. It is not a fuel consumed by cooling. Refrigerant loss indicates a leak that needs appropriate professional attention.",
                    "stage": 5,
                    "part": "return-line",
                },
                {
                    "question": "Why is the air leaving the outdoor unit warm?",
                    "answer": "The outdoor coil rejects both the heat removed from the room and the work added by the electric compressor. That energy is carried away in the outdoor air.",
                    "stage": 3,
                    "part": "condenser",
                },
            ],
            prediction="If both units released their heat inside the same closed room, would the room get cooler overall?",
            prediction_answer="No. The cooling at the indoor coil would be outweighed by the heat released at the other coil: it includes the same room heat plus the compressor's electrical work. The room would gain heat overall.",
        )
    )
