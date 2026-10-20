"""Kitchen mechanisms: source-grounded, explicitly scoped generic teaching plans."""

from .plans import Step as B
from .plans import SystemPlan as S
from .plans import check as Q
from .plans import source as R

FRIDGE = S("refrigerator", "Refrigerator", "Kitchen", "Generic vapor-compression refrigerator",
    "It carries heat out of the food compartment; electricity keeps the journey going.",
    ("Cold coil", "Compressor", "Warm coil", "Narrow tube"), (
        B("Take heat from the cabinet", "coil", 0, "Heat passes from warmer cabinet air through a metal tube into colder refrigerant. At low pressure, liquid can boil at a cold temperature, carrying that energy away as vapor.", "Warmer cabinet air", "Energy enters refrigerant", 0, "Sealed System Operation, evaporator and return steps"),
        B("Add work to the vapor", "piston", 1, "The compressor takes in vapor and uses electrical work to raise its pressure. The vapor becomes hotter. This piston is one compressor design, not a diagram of every refrigerator.", "Low-pressure vapor", "Hotter, higher-pressure vapor", 0, "Sealed System Operation, compressor steps 1–2"),
        B("Release heat to the kitchen", "coil", 2, "The outside coil is warmer than the kitchen air, so heat flows out. Vapor condenses into liquid. This released energy includes both the cabinet heat and the compressor's added work.", "Hot refrigerant", "Heat leaves; liquid forms", 0, "Sealed System Operation, condenser steps 3–4"),
        B("Restore the cold side", "restrictor", 3, "The narrow capillary sustains a pressure drop. Some liquid flashes into vapor, leaving a colder mixture for the inside coil. Different parts do these jobs together while the compressor runs.", "High-pressure liquid", "Low-pressure mixture", 0, "Sealed System Operation, capillary and evaporator steps 5–7"),
    ), (R("GE Appliances: sealed system operation", "https://products.geappliances.com/appliance/gea-support-search-content?contentId=16911", "Compressor, condenser, capillary and evaporator around a sealed loop."),
        R("OpenStax: heat pumps and refrigerators", "https://openstax.org/books/college-physics-2e/pages/15-5-applications-of-thermodynamics-heat-pumps-and-refrigerators", "The warm side rejects removed heat plus work; the same-room result is an energy-balance inference.")),
    Q("Does the refrigerator make heat disappear?", "Yes, it destroys heat", "No, it moves energy elsewhere", 1, "Energy removed from the cabinet is released into the kitchen, together with the electrical work supplied to the cycle."),
    Q("Would an open refrigerator cool a closed kitchen overall?", "Yes, because cold air escapes", "No, both sides exchange heat with that room", 1, "The warm side returns the removed heat plus added work. A cool patch near the door does not establish net room cooling."),
    1, ("Compressor running", "Work maintains sustained circulation around the loop."),
    ("Compressor stopped", "Sustained pumping stops. The real cold coil can still absorb heat briefly; that transient is omitted."),
    "Exposed service-layout cutaway; real coil placement and compressors vary. The front opening is a drawing aid. No temperatures, pressures or efficiency are predicted.", ("fridge",))

MICROWAVE = S("microwave", "Microwave oven", "Kitchen", "Generic turntable microwave oven",
    "Electrical energy becomes microwaves, then thermal energy within absorbing food.",
    ("Magnetron", "Metal cavity", "Food", "Turntable"), (
        B("Make an electromagnetic wave", "field", 0, "Electrical power feeds a magnetron, which produces microwaves. They carry energy into the cooking cavity. The drawn wave is a signal diagram, not a visible beam or a measured field pattern.", "Electrical energy", "Microwave energy", 0, "Cooking with Microwaves: magnetron"),
        B("Transfer energy into food", "field", 2, "The changing electric field interacts with polar molecules and mobile ions in food. Absorbed energy becomes thermal motion. The food is heated; it does not become radioactive.", "Electromagnetic energy", "Thermal energy in food", 1, "Microwave heating mechanisms: dipolar and ionic contributions"),
        B("Spread the heating", "gear", 3, "Metal walls reflect microwaves, producing an uneven energy pattern. Moving the food exposes it to different regions. Heat also spreads by conduction, so a thick center is not magically heated first.", "Uneven energy deposition", "Redistributed exposure and heat", 0, "Cooking with Microwaves: reflection and thick foods"),
    ), (R("FDA: microwave ovens", "https://www.fda.gov/radiation-emitting-products/resources-you-radiation-emitting-products/microwave-ovens", "Magnetron, reflection, absorption, non-ionizing energy and thick-food conduction."),
        R("FDA: alternative food processing technologies", "https://www.fda.gov/media/103619/download", "Microwave heating mechanisms include dipolar response and ionic migration.")),
    Q("Does a microwave always cook food from the inside out?", "Yes, the center heats first", "No, absorption and conduction determine heating", 1, "Microwaves deposit energy where food absorbs them. Heat conduction remains important inside thick food; heating is not guaranteed to be uniform."),
    Q("If the turntable stops, must all heating stop too?", "Yes, rotation produces the energy", "No, rotation redistributes exposure", 1, "The magnetron supplies microwave energy. Rotation changes exposure to the field; it is not the heat source."),
    2, ("Food rotates", "Motion changes which regions of food meet the illustrated field pattern."),
    ("Food held still", "The source can still supply energy; this static exposure may leave a less even result. The pattern is illustrative."),
    "Field arrows show energy transfer, not an actual electromagnetic simulation. Appliance shielding and interlocks are not service diagrams.", ("microwave oven",))

DISHWASHER = S("dishwasher", "Dishwasher", "Kitchen", "Generic recirculating dishwasher",
    "A little water is heated, pumped through jets, filtered and eventually replaced.",
    ("Water inlet", "Circulation pump", "Spray arm", "Filter and drain"), (
        B("Fill a small working pool", "valve", 0, "The inlet admits water into the lower tub, rather than filling the entire cabinet. Heat and detergent prepare this water for cleaning; exact heating arrangements depend on the model.", "Supply water", "Warm detergent solution", 0, "Steps 1–3: fill, heat and dispense"),
        B("Pump water onto the dishes", "spray", 1, "A circulation pump drives water through the spray arms. Jets strike exposed surfaces and help dislodge food. Water motion, detergent and heat do different jobs; no one of them explains cleaning alone.", "Pooled wash water", "Directed jets at dish surfaces", 0, "Step 4: spray arms circulate water"),
        B("Separate dirt and rinse", "filter", 3, "Water returns to the bottom and passes the filter. Dirty water is drained, then clean water rinses remaining detergent away. Drying may use heat, airflow or another model-specific approach.", "Used wash water", "Filtered circulation, then fresh rinse", 0, "Steps 5–7 and How does a dishwasher drain?"),
    ), (R("Whirlpool: how a dishwasher works", "https://www.whirlpool.com/blog/kitchen/how-does-a-dishwasher-work.html", "Fill, heating, detergent, circulation, filtering, draining, rinsing and drying."),),
    Q("Does the cabinet fill completely with water?", "Yes, dishes soak in a full tank", "No, a lower pool feeds the spray system", 1, "The pump recirculates water from the lower tub through jets. The cabinet does not need to become a full tank."),
    Q("Why might a surface shielded from every jet clean less well?", "The spray cannot directly reach that surface", "The pump makes water pass through solid dishes", 0, "Water jets follow real openings. Detergent may reach by other paths, but a solid obstruction prevents the illustrated direct jet from reaching the shielded patch."),
    1, ("Jet reaches a dish", "The directed stream reaches the exposed surface."),
    ("Surface shielded", "A solid obstruction intercepts this jet; the region behind it is not directly sprayed in this model."),
    "One circulation path and one dish are enlarged. Filter designs, drying methods and cycle timing vary; no cleaning-performance prediction is made.")

INDUCTION = S("induction-cooktop", "Induction cooktop", "Kitchen", "Generic induction heating with compatible cookware",
    "A changing magnetic field induces currents in the pan; the pan itself heats up.",
    ("Powered coil", "Cookware base", "Food"), (
        B("Create a changing field", "field", 0, "Alternating current in a coil produces a changing magnetic field. Energy can cross the glass without a flame or a glowing hotplate first transferring heat into the pan.", "Alternating electrical supply", "Changing magnetic field", 0, "How it Works"),
        B("Generate heat in the pan", "heat", 1, "The field induces currents in suitable cookware. Electrical losses generate thermal energy within the base. Coupling depends on the cookware, which is why a pan that works on gas may not work here.", "Field coupled to cookware", "Thermal energy in the base", 0, "How it Works and compatible cookware"),
        B("Pass heat into the food", "heat", 2, "The hot base transfers heat into the food. The glass may become hot from contact with that pan. Stopping power stops new electrical input, not the stored heat already in the cookware.", "Hot pan base", "Heat enters food", 0, "How it Works; heat is created within the cookware"),
    ), (R("DOE: induction cooktops", "https://www.energy.gov/articles/making-switch-induction-stoves-or-cooktops", "Changing field, currents in compatible cookware and heat created in the cookware."),),
    Q("Where is heat generated first in this teaching model?", "Inside the compatible pan base", "In a flame below the glass", 0, "The powered coil couples electromagnetic energy into the pan. The pan then transfers heat to the food and nearby glass."),
    Q("Does switching off power make a hot pan cold immediately?", "Yes, the field was the temperature", "No, the pan retains thermal energy", 1, "Removing input is different from removing stored energy. The pan must still transfer that energy to its surroundings as it cools."),
    1, ("Coupled cookware", "Energy is transferred into the compatible base."),
    ("Uncoupled comparison", "This declared non-coupled load receives no induction heating. Actual cooktop detection and compatible materials vary."),
    "Qualitative coupling, not a magnetic-field or material simulation. Stored heat and surface temperatures are not numerically modeled.", ("induction stove",))

OVEN = S("electric-oven", "Electric oven", "Kitchen", "Generic electric oven with optional convection fan",
    "Elements supply heat; radiation, moving air and contact transfer it into food.",
    ("Heating element", "Oven cavity", "Temperature control", "Convection fan"), (
        B("Turn electricity into heat", "heat", 0, "Electrical current heats resistive elements. Their radiation and the warming air transfer energy into the oven load. Bake and broil arrangements vary; this is a general energy pathway.", "Electrical input", "Thermal energy at elements", 0, "Understanding how ovens work: electric ovens"),
        B("Move heat through the cavity", "flow", 3, "Hot surfaces radiate toward the food, air carries energy, and contact transfers heat through the pan. A convection fan moves air; it helps redistribute energy rather than becoming a separate unlimited heat source.", "Heated surfaces and air", "Energy transferred into the load", 0, "Heat transfer and convection"),
        B("Regulate, rather than heat forever", "valve", 2, "A temperature sensor and controller cycle the heating input. Off intervals are normal. The cavity and food retain heat between cycles, so the heating switch does not directly equal the food's temperature.", "Temperature feedback", "Heating input cycles", 1, "Electric Range Operation of the Elements During Bake"),
    ), (R("Whirlpool: how ovens work", "https://www.whirlpool.com/blog/kitchen/how-do-ovens-work.html", "Electric elements and the roles of convection, conduction and radiant heating."),
        R("GE: cycling elements during baking", "https://products.geappliances.com/appliance/gea-support-search-content?contentId=16976", "Heating elements cycle during a normal bake operation.")),
    Q("Does an off interval mean the food instantly stops receiving heat?", "Yes, everything becomes cold", "No, hot surroundings retain energy", 1, "Stored thermal energy remains in the oven and food. Element cycling controls input over time."),
    Q("Would a fan alone supply an oven's continuing cooking energy?", "Yes, air motion creates unlimited heat", "No, energy still needs a source", 1, "A fan redistributes air and uses some electrical work. The oven's heating system supplies the cooking heat in this model."),
    1, ("Fan-assisted circulation", "Air is moved through the cavity; radiation and contact transfer remain."),
    ("Fan stopped", "Forced circulation stops. Radiation and natural convection can still transfer heat; the oven does not instantly stop cooking."),
    "Illustrative heat paths, not measured air currents or cooking times. Broil, bake and convection controls differ across models.", ("oven",))

KITCHEN = (FRIDGE, MICROWAVE, DISHWASHER, INDUCTION, OVEN)
