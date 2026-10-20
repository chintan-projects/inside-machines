"""Immutable CE-1 AC lesson: source-grounded causal storyboard and shared scenes."""

from pydantic import HttpUrl

from .ac_craft import aircon_craft
from .ac_graphics import ac_graphics
from .contracts import LessonSpec
from .renderer_assets import ac_renderer_fingerprint
from .teaching_contracts import Assessment, Beat, Claim, Property, Scenario, TeachingSpec

AC_ID = "air-conditioner-ce-1"


def aircon_concept() -> LessonSpec:
    """Author the complete AC teaching path without paid model calls."""
    spec = aircon_craft()
    spec.canonical, spec.version = AC_ID, 2
    spec.title = "Why does an AC need an outdoor unit?"
    spec.question = spec.title
    spec.assumptions[2] = (
        "All states are qualitative. The compression inset demonstrates a principle, not the internals of a particular compressor. Marker sizes/counts are illustrative."
    )
    spec.assumptions.append(
        "Energy accounting assumes steady cooling in an insulated room; auxiliary electrical work is included in supplied work. No room temperature or efficiency is calculated."
    )
    spec.sources.append(
        type(spec.sources[0])(
            title="Danfoss: refrigeration, an introduction to the basics",
            url=HttpUrl("https://assets.danfoss.com/documents/latest/35513/AN227186438976en-000301.pdf"),
            supports="The refrigeration process, pressure/enthalpy diagram and expansion valve explain pressure reduction and partial vaporization in the refrigerant circuit.",
        )
    )
    titles = [
        "Heat flows from warmer to cooler",
        "Room air gives heat to a colder coil",
        "Work makes the vapor hotter",
        "The outdoor coil gives the heat away",
        "A restriction prepares a cold mixture",
        "Put the whole system back together",
    ]
    explanations = [
        "Touch a cooler object with a warmer one and heat passes to the cooler object. An AC uses that familiar relationship twice: room air gives heat to a colder coil, and a hotter coil gives heat to outdoors.",
        "The coil is colder than the room air. Heat crosses its metal wall into the sealed refrigerant. Some liquid boils, absorbing energy. The air stays outside the pipe and returns to the room cooler.",
        "Heat cannot simply flow from a cooler room to warmer outdoors. The compressor uses electrical work to raise the vapor's pressure and temperature until it is hotter than the outdoor air. The inset shows a compression principle; real internals vary.",
        "Now the refrigerant is hotter than outdoor air, so heat can leave through the outdoor coil. Vapor condenses into liquid while releasing energy. The rejected heat includes the heat collected indoors and the work supplied to the system.",
        "Liquid passes through a narrow restriction. The downstream pressure is lower and some liquid flashes into vapor, leaving a cold mixture in this refrigeration regime. This valve does not extract heat like the indoor coil does.",
        "All four processes occur together in different parts of the running loop. Moving heat is only useful if it leaves the room. With both coils inside the same insulated room, the collected heat returns there, plus the supplied electrical work.",
    ]
    narration = [
        "Could this cool a sealed room with both units inside? Make a prediction. Start with something familiar: heat flows from a warmer object to a cooler one. An air conditioner uses that relationship twice. The puzzle is how to release room heat into warmer outdoors.",
        "Room air gives heat to the colder indoor coil. Heat crosses the metal into the fluid inside, called refrigerant. Some liquid boils into vapor, absorbing energy. The same room air comes back cooler; it never travels through the refrigerant pipes.",
        "The compressor adds electrical work to the vapor. Its pressure and temperature rise, making it hotter than the outdoor air. This inset illustrates compression, not a particular compressor's internals. Now heat can flow out to the warmer outdoors.",
        "At the outdoor coil, hot vapor gives heat to outdoor air and condenses into liquid. The fan carries heat away. The coil releases the heat collected from your room, plus the electrical work supplied to run the machine.",
        "The liquid passes through the expansion valve, a restriction. Its pressure drops and some liquid flashes into vapor. The resulting cold mixture can absorb room heat again. Pressure reduction here is different from removing heat at a coil.",
        "All four processes run together. Heat released equals room heat removed plus electrical work. Put both sides in the same insulated room and that heat returns, plus the electrical input: the room warms overall. Could an open refrigerator cool that room? Pause and explain why.",
    ]
    # Keep the inherited physical part references, but author new stage meaning in a new ID.
    for i, stage in enumerate(spec.stages):
        stage.title, stage.explanation, stage.narration = titles[i], explanations[i], narration[i]
        stage.duration = 20
    spec.stages[0].cause = "Heat passes from warmer to cooler; work is required to move it the other way."
    spec.stages[0].input_state, spec.stages[0].output_state = (
        "A warmer and a cooler object",
        "Heat transferred toward the cooler object",
    )
    spec.stages[4].source_indices = [0, 3]
    claim_data = [
        (
            "heat",
            "Heat transfers spontaneously from warmer to cooler; a refrigerator needs work to move heat the other way.",
            2,
            "Section 4.3, Figure 4.6 and discussion of the cold/hot reservoirs",
            "generic",
            "An idealized heat-transfer explanation, not a calculation of heat-transfer rate.",
        ),
        (
            "pickup",
            "Room heat crosses the indoor coil wall into refrigerant that evaporates; room air remains separate from the sealed fluid.",
            0,
            "How Does AC Work -- In More Detail; FAQ: Does AC take air from outside?",
            "generic",
            "Generic split-system cooling; separate ventilation and humidity removal are omitted.",
        ),
        (
            "compression",
            "The compressor raises refrigerant vapor pressure and temperature so heat can be rejected outdoors.",
            0,
            "Five-step summary, step 1; compressor discussion under In More Detail",
            "generic",
            "The piston inset illustrates compression; the actual pump may be rotary, scroll or another design.",
        ),
        (
            "release",
            "The outdoor coil rejects heat as vapor condenses, releasing collected room heat and supplied work.",
            2,
            "Section 4.3, Figures 4.6–4.7; conservation following Equation 4.3",
            "generic",
            "Steady operation and consistent energy boundary; no coefficient of performance is claimed.",
        ),
        (
            "throttle",
            "The expansion device reduces pressure and creates a cold liquid/vapor mixture in the refrigeration cycle.",
            3,
            "Printed page 20, sections 3.5 Expansion process and 3.6 Pressure sides; page 22 cycle diagram",
            "generic",
            "Throttling is not a reversed piston expansion or heat extraction; refrigerant-specific pressures are omitted.",
        ),
        (
            "balance",
            "With both sides in one insulated room, net energy added to that room equals the total electrical input.",
            2,
            "Inference from Figure 4.6 and energy conservation following Equation 4.3",
            "inference",
            "Our application of energy conservation to a common insulated boundary, over time with negligible stored-energy change.",
        ),
    ]
    claims = [
        Claim.model_validate(
            dict(id=id, statement=statement, source=source, locator=locator, scope=scope, limitation=limit)
        )
        for id, statement, source, locator, scope, limit in claim_data
    ]
    graphics, identifiers, changes, counterfactual = ac_graphics()
    properties = [
        [("Heat direction", "Warmer object", "Toward cooler object")],
        [
            ("Phase", "Liquid + vapor", "Vapor"),
            ("Pressure", "Low", "Low"),
            ("Heat", "In room air", "Absorbed by refrigerant"),
        ],
        [
            ("Phase", "Vapor", "Vapor"),
            ("Pressure", "Low", "High"),
            ("Temperature", "Below outdoors", "Above outdoors"),
        ],
        [
            ("Phase", "Vapor", "Liquid"),
            ("Pressure", "High", "High"),
            ("Heat", "In refrigerant", "Released into outdoor air"),
        ],
        [
            ("Phase", "Liquid", "Liquid + vapor"),
            ("Pressure", "High", "Low"),
            ("Temperature", "Warmer liquid", "Cold mixture"),
        ],
        [("Energy", "Room heat + supplied work", "Both released at the hot coil")],
    ]
    ids = ["familiar-heat", "pick-up", "add-work", "release-heat", "lower-pressure", "whole-system"]
    claim_ids = [
        ["heat"],
        ["pickup", "heat"],
        ["compression", "heat"],
        ["release"],
        ["throttle"],
        ["balance", "release"],
    ]
    actions = [
        "See the direction heat flows",
        "Let room heat enter the coil",
        "Add work to the vapor",
        "Let the hot coil release heat",
        "Pass liquid through the restriction",
        "Follow heat and electrical work",
    ]
    static = [
        "Heat passes from the warmer object to the cooler one. Work is needed to transfer it the other way.",
        "Heat enters through the pipe wall; liquid boils into vapor. Room air and refrigerant stay separate.",
        "Work compresses vapor into a smaller volume in this schematic, raising its pressure and temperature.",
        "Vapor loses energy to outdoor air and condenses. The collected heat and supplied work both leave here.",
        "After the restriction: lower pressure, some vapor and remaining liquid. This cold mixture is ready for the indoor coil.",
        "Trace room heat and supplied work to the hot coil. Both go wherever that coil releases heat.",
    ]
    beats = [
        Beat(
            id=ids[i],
            stage=i,
            short=[
                "Start with heat",
                "Pick up heat",
                "Add work",
                "Release heat",
                "Lower pressure",
                "Try the whole loop",
            ][i],
            requires=[] if i == 0 else [ids[i - 1]],
            claims=claim_ids[i],
            bridge=explanations[i].split(". ")[0] + ".",
            visible_change=static[i],
            static_explanation=static[i],
            action=actions[i],
            graphics=identifiers[i],
            changes=changes[i],
            properties=[Property(name=n, before=a, after=b) for n, a, b in properties[i]],
        )
        for i in range(6)
    ]
    claim_sources = {c.id: c.source for c in claims}
    for beat in beats:
        spec.stages[beat.stage].source_indices = sorted({claim_sources[c] for c in beat.claims})
    prediction = Assessment(
        prompt="Both units run in the same sealed, insulated room. What happens to the room overall?",
        choices=["It gets cooler", "It gets warmer", "It stays the same"],
        correct=1,
        explanation="The indoor coil removes room heat, but the other coil returns that same heat plus the supplied electrical work. Over time the room gains energy and warms overall.",
        reasoning=["Both coils exchange heat with the same room", "Electrical input adds net energy"],
        misconception="An AC manufactures cold, so it should cool any room it sits in.",
    )
    spec.teaching = TeachingSpec(
        spec_version="ce-1",
        renderer="ac-cutaway-v2",
        renderer_fingerprint=ac_renderer_fingerprint(),
        goal="Explain why work and an outdoor heat sink are needed, then predict the open-refrigerator case.",
        misconception=prediction.misconception,
        core=["evaporator", "compressor", "condenser", "expansion"],
        operation="simultaneous",
        operation_note="The chapters isolate attention. All four processes operate together during steady cooling.",
        invariants=[
            "Refrigerant stays in a sealed loop; the two air streams remain separate.",
            "Heat released equals heat removed plus total supplied work at steady operation.",
        ],
        claims=claims,
        beats=beats,
        prediction=prediction,
        transfer=Assessment(
            prompt="An electric refrigerator runs with its door open in a sealed, insulated room. Does it cool the room over time?",
            choices=["Yes, the room cools", "No, the room warms", "No energy is added"],
            correct=1,
            explanation="Both the cold interior and hot coil exchange heat with that same room. Heat removed returns there, plus electrical input. Over time the complete refrigerator warms the room.",
            reasoning=["Heat removed returns to the same room", "Electrical input adds energy overall"],
            misconception="A refrigerator keeps producing cold even when its door is open.",
        ),
        teach_back="How can this machine move heat from a cooler room to warmer outdoors?",
        teach_back_reasoning=[
            "Heat is absorbed at the cold indoor coil",
            "Electrical work raises the vapor temperature",
            "The hotter outdoor coil releases heat",
        ],
        scenarios=[
            Scenario(
                id="outside",
                label="Hot coil outside",
                beat="whole-system",
                kind="qualitative",
                context="outside",
                outcome="The room loses heat",
                explanation="Room heat and supplied work leave through the outdoor coil, beyond the room boundary.",
                claims=["release", "balance"],
                changes=[],
            ),
            Scenario(
                id="inside",
                label="Both coils in the room",
                beat="whole-system",
                kind="qualitative",
                context="inside",
                outcome="The room gains heat overall",
                explanation=prediction.explanation,
                claims=["balance"],
                changes=counterfactual,
            ),
        ],
    )
    spec.graphics = graphics
    return LessonSpec.model_validate(spec.model_dump())
