"""Cleaning and airflow systems retain distinct physical jobs under shared contracts."""

from .plans import Step as B
from .plans import SystemPlan as S
from .plans import check as Q
from .plans import source as R

WASHER = S("washing-machine", "Washing machine", "Home", "Generic front-load washing machine",
    "Gentle tumbling cleans; draining and faster rotation remove the used water.",
    ("Inlet valve", "Drum and motor", "Drain pump"), (
        B("Admit a working amount of water", "valve", 0, "The inlet valve admits water into the tub around the perforated drum. Water and detergent form the wash solution. The control system manages the amount; this is not a cabinet filled to the top.", "Supply water", "Wash solution in the tub", 0, "Front-load washer: small water amount and detergent"),
        B("Lift and drop the clothes", "drum", 1, "The motor turns the horizontal drum slowly enough for clothes to lift and fall through the solution. Movement and detergent help remove soil. The drum and the water-holding outer tub are different parts.", "Motor work and wash solution", "Laundry repeatedly moves through water", 0, "How do front load washers work?"),
        B("Drain, then spin", "drum", 2, "The pump removes used water. During faster spin, the drum constrains the clothes to turn while water can leave through its holes and be pumped away. Rinsing replaces the dirty solution with cleaner water.", "Wet laundry and used water", "Drained water and less-wet laundry", 0, "After washing and rinsing: high-speed spin and drain"),
    ), (R("Samsung: front-load washing mechanism", "https://www.samsung.com/us/home-appliances/buying-guide/difference-between-top-load-and-front-load-washers/", "Horizontal-drum tumbling, small water amount, rinse and spin extraction."),
        R("GE: variable-speed washer motors", "https://products.geappliances.com/appliance/gea-support-search-content?contentId=22431", "Motor speed changes for agitation and spinning; depends on load and program.")),
    Q("Why not use the fastest spin for the whole wash?", "Faster is always better cleaning", "Clinging clothes do not tumble the same way", 1, "Slow tumbling repeatedly rearranges the load. Fast spinning serves water extraction; the two modes have different jobs."),
    Q("If water leaves the fabric but cannot leave the tub, is the drain job complete?", "Yes, spin destroys the water", "No, the collected water still needs an outlet", 1, "Spinning and pumping are separate. Water that leaves the clothes remains in the system until it can drain."),
    1, ("Slow tumble", "Clothes are lifted, then fall through the wash solution."),
    ("Fast-spin comparison", "The load stays against the drum instead of undergoing the same lift-and-drop motion. Real speeds are not specified."),
    "Front-load example. No cycle times, load limits or measured speed threshold; controls, suspensions and pumps vary.", ("washer", "front load washer"))

VACUUM = S("vacuum-cleaner", "Vacuum cleaner", "Home", "Generic bagged vacuum with a motor-driven fan",
    "The fan moves air; moving air carries dirt; a porous filter separates them again.",
    ("Motor and fan", "Floor nozzle", "Porous bag", "Exhaust"), (
        B("Give air momentum", "gear", 0, "The motor turns a fan that transfers work into the air. Air is discharged toward the exhaust, helping maintain a pressure difference across the machine. Suction is not a substance stored inside a box.", "Electrical work", "Driven airflow", 0, "Fan, airflow and exhaust filtration path"),
        B("Carry dirt from the floor", "flow", 1, "Room air enters the nozzle and travels through the hose. That moving air can carry loose particles toward the collection chamber. The motor, nozzle and exhaust are parts of one continuous air path.", "Room air and loose particles", "Air and dirt enter the hose", 0, "Airflow through the bagged system"),
        B("Keep dirt, release air", "filter", 2, "Air passes through a porous bag and downstream filters while collected dirt remains. Filter resistance matters: a clogged path can reduce airflow even though the motor is powered and the fan still turns.", "Air carrying particles", "Filtered air and retained dirt", 1, "FilterBag, motor protection and exhaust filter resistance"),
    ), (R("Miele: bagged vacuum airflow and filtration", "https://media.miele.com/downloads/4e/71/06_C7F13838F09D1EEEAAF3A1966FE64E71.pdf", "Airflow through a bagged vacuum and the collection/filter arrangement."),
        R("Miele: reduced cleaning performance", "https://www.mieleusa.com/support/customer-assistance/canister_vacuum_cleaner-1326/all/cleaning_performance_reduced_with_filterbag-92265764619", "A full bag or blocked filters can reduce suction performance.")),
    Q("Is an airtight bag as useful as a porous filter bag?", "Yes, it traps everything perfectly", "No, air also needs a through-path", 1, "Collection must separate particles while allowing air through. An airtight barrier prevents sustained throughflow in this declared comparison."),
    Q("Can the motor run while little air reaches the nozzle?", "Yes, a restricted path can limit airflow", "No, motor motion guarantees nozzle flow", 0, "Fan power and path resistance are separate. A powered fan does not guarantee a useful throughflow through a restricted machine."),
    2, ("Porous collection wall", "Air passes through while the modeled dirt is retained."),
    ("Airtight-wall thought experiment", "No air passes this wall; upstream throughflow stops in the steady comparison. The powered motor is not thereby switched off."),
    "Air paths and representative particles are enlarged. No vacuum level or particle-capture percentage; cyclonic designs require a different separator view.", ("vacuum", "hoover", "bagged vacuum"))

FAN = S("table-fan", "Table fan", "Home", "Generic motor-driven axial fan",
    "The motor turns shaped blades; moving air helps your body lose heat.",
    ("Electric motor", "Angled blades", "Air around you"), (
        B("Turn the shaft", "gear", 0, "Electrical energy drives a motor and turns its shaft. The blades are attached to that shaft. The motor supplies mechanical work rather than making cold air by refrigeration.", "Electrical energy", "Rotating shaft", 0, "Motor-driven blades and their angle"),
        B("Push on the air", "flow", 1, "Angled moving blades push on surrounding air. Air gains momentum and moves through the fan's open flow path. The guard is a physical boundary, not a sealed container.", "Blade work", "Moving air", 0, "Each blade is angled and forces air forward"),
        B("Carry heat away from you", "flow", 2, "Air movement can increase heat transfer from warmer skin and help sweat evaporate. A fan can feel cooling without lowering the whole room's temperature. Its electrical work ultimately adds energy indoors.", "Warm skin and moving air", "Greater heat transfer from the person", 1, "Fans cool people, not rooms"),
    ), (R("James Dyson Foundation: fan engineering", "https://media.dyson.com/downloads/jdf/idea_teachers_pack.pdf", "Angled blades driven by a motor move air; conventional fan example."),
        R("DOE: fans and comfort", "https://www.energy.gov/articles/top-11-things-you-didnt-know-about-saving-energy-home-summer-edition", "Fans cool people rather than refrigerating a room.")),
    Q("Does a table fan refrigerate the whole room?", "Yes, spinning creates cold", "No, it mainly changes air movement", 1, "Air movement changes how your body exchanges heat and moisture. It does not establish that the room's air has become colder."),
    Q("Why can still air and moving air at the same temperature feel different?", "Air movement changes heat and evaporation at skin", "The fan must change the thermometer reading", 0, "The rate of heat and moisture transfer matters as well as air temperature. This effect depends on actual conditions; no comfort or health guarantee is implied."),
    1, ("Motor turning blades", "Blade motion drives an air stream through the open guard."),
    ("Motor stopped", "The fan no longer supplies sustained forced airflow. Residual motion and natural room currents are omitted."),
    "Qualitative airflow, not an aerodynamic or comfort simulation. No claimed air speed, cooling capacity or universal heat-stress advice.", ("fan", "desk fan"))

DRYER = S("clothes-dryer", "Clothes dryer", "Home", "Generic vented electric tumble dryer",
    "Heating, tumbling and a path for humid air work together to remove water from fabric.",
    ("Air heater", "Rotating drum", "Blower and exhaust"), (
        B("Warm the incoming air", "heat", 0, "Room air passes a heater and gains thermal energy. Heat speeds evaporation from wet fabric. This example uses an electric element; gas and heat-pump dryers arrange the energy supply differently.", "Room air and electrical input", "Warmer drying air", 0, "Heat: air is drawn in and heated"),
        B("Expose wet fabric", "drum", 1, "A motor turns a drum with internal lifters. Clothes move and separate so air can reach more wet surfaces. Tumbling helps contact; it does not destroy the water stored in the fabric.", "Wet fabric and drum work", "Wet surfaces exposed to airflow", 0, "Tumbling and baffles"),
        B("Give moisture an exit", "flow", 2, "A blower carries air through the drum and lint filter toward the exhaust. Evaporated water leaves with that humid air. In a vented dryer, heating alone is not the complete moisture-removal pathway.", "Warm air plus evaporated water", "Humid air reaches the exhaust", 0, "Air Flow: moisture needs a passage out"),
    ), (R("Whirlpool: heat, tumbling and airflow", "https://producthelp.whirlpool.com/Laundry/Dryers/Product_Info/Dryer_Product_Assistance/How_does_a_Dryer_Dry_Clothing%3F", "The separate jobs of heat, drum motion and a route for moisture to leave."),),
    Q("Does turning the drum make water cease to exist?", "Yes, motion destroys moisture", "No, water must evaporate and leave", 1, "The dryer transfers water from fabric into air, then transports humid air out along the exhaust route."),
    Q("Would continued heat alone establish a complete drying system with no moisture outlet?", "Yes, moisture has no need to leave", "No, moisture removal needs a route", 1, "The declared vented system needs a path to remove humid air. This is a model comparison, not an instruction to obstruct an appliance."),
    2, ("Open humid-air path", "The model transports humid air toward the outlet."),
    ("No through-path in the model", "Sustained exhaust flow is absent. A powered heater does not create an outlet; real appliance protections are not simulated."),
    "Vented dryer only. Condensing and heat-pump machines recover water differently. Particle counts, flow and drying times are illustrative.", ("dryer", "tumble dryer"))

AC = S("air-conditioner", "Air conditioner", "Home", "Generic split-system air conditioner in cooling mode",
    "Heat goes outside through refrigerant tubing; the indoor air does not travel through that tubing.",
    ("Indoor cold coil", "Compressor", "Outdoor warm coil", "Expansion device"), (
        B("Take heat from indoor air", "coil", 0, "The indoor blower moves room air over a cold coil. Heat passes into refrigerant inside sealed tubing, where liquid evaporates. Air and refrigerant remain separate substances on opposite sides of a wall.", "Room air warmer than the coil", "Heat enters refrigerant", 0, "Cold side and evaporator"),
        B("Use work to make a hot side", "piston", 1, "The compressor draws vapor and raises its pressure and temperature using work. The outdoor coil can then transfer heat to outdoor air. Heat rejection includes the indoor heat and the supplied work.", "Low-pressure vapor plus work", "Hotter refrigerant rejects heat", 1, "Compression and condensation"),
        B("Restore low pressure", "valve", 3, "An expansion device sustains the pressure drop before the indoor coil. The cycle continues: collect heat, add work, reject heat, restore the cold side. These jobs overlap in different parts of the operating loop.", "Liquid on the high-pressure side", "Low-pressure evaporator supply", 1, "Expansion and the repeating cycle"),
    ), (R("Carrier: how air conditioners work", "https://www.carrier.com/us/en/residential/hvac-resources/air-conditioners/how-do-air-conditioners-work/", "Indoor/outdoor heat exchange, separate air and refrigerant paths, continuous operation."),
        R("Carrier: refrigerant cycle", "https://www.carrier.com/residential/en/ca/products/air-conditioners/ac-refrigerant/", "Evaporation, compression, condensation and expansion.")),
    Q("Does the refrigerant pipe bring outside air into the room?", "Yes, that is what the pipe carries", "No, it carries a sealed working fluid", 1, "Room air crosses the coil on the outside of the metal tube. Refrigerant carries heat inside the tube; ventilation, if present, is a separate system."),
    Q("Could cooling continue indefinitely if the warm side could reject no heat?", "Yes, the cold coil stores unlimited energy", "No, sustained operation needs heat rejection", 1, "The incoming heat and work need an exit from the cycle. The system cannot store them indefinitely."),
    0, ("Cold coil absorbs heat", "Heat passes from room air into the colder working fluid."),
    ("No temperature difference", "At the declared equal-temperature comparison, there is no net heat transfer through the coil wall. No transient is simulated."),
    "Cooling mode and qualitative coil sections. No temperatures, pressures, refrigerant specification or actual installation layout is predicted.", ("AC", "air conditioning", "aircon"))

HOME = (WASHER, VACUUM, FAN, DRYER, AC)
