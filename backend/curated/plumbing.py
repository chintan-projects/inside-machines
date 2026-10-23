"""Plumbing principles, not diagnosis, installation or repair instructions."""

from .plans import Step as B
from .plans import SystemPlan as S
from .plans import check as Q
from .plans import source as R

TOILET = S("toilet", "Toilet", "Home", "Generic gravity-tank siphonic toilet",
    "Stored water starts a flush; the trapway carries waste away; the supply refills the tank.",
    ("Tank and flush valve", "Bowl and trapway", "Fill valve and float"), (
        B("Release stored water", "valve", 0, "Opening the flush valve lets stored tank water enter the bowl. Gravity supplies the initial motion. The flush valve and the separate supply fill valve do different jobs.", "Water stored in the tank", "Water delivered to the bowl", 0, "How a Toilet Flushes: tank and flush valve"),
        B("Start the bowl's siphon", "trap", 1, "Enough entering water fills the shaped trapway and establishes a siphon in this example. Water and waste move toward the drain. Air entering later breaks the siphon; the flow cannot continue forever.", "Water entering the bowl", "Flow through the trapway to drain", 0, "Siphon formation and termination"),
        B("Refill and close the supply", "tank", 2, "As tank level falls, the fill valve admits supply water. A rising float eventually shuts that valve. Refilled bowl water also restores the trap's water seal, ready for the next cycle.", "Lower tank level and supply", "Refilled tank and water seal", 0, "Fill valve and float sequence"),
    ), (R("Kohler: how a toilet flushes", "https://assist.kohler.com/en/toilets-and-seats/How-a-Toilet-Flushes", "Gravity-tank flush, siphonic trapway, air break and float-controlled refill."),),
    Q("Are the flush valve and fill valve the same job?", "Yes, one valve does everything", "No, one releases storage and one refills it", 1, "The flush valve connects tank to bowl. The fill valve controls supply entering the tank. Keeping these jobs separate explains the cycle."),
    Q("With supply absent but a full tank, is all stored flush energy already gone?", "Yes, no supply means an empty tank", "No, stored water can still fall", 1, "A full tank stores gravitational potential energy. Removing the future supply does not instantly remove the existing water; subsequent refilling would be unavailable."),
    2, ("Tank refilling", "Supply enters while the float is below its closing level."),
    ("Float reaches shutoff", "The rising float closes the fill valve; the modeled refill stream stops."),
    "Siphonic gravity-tank example, not every toilet design. Pipe dimensions, flush volume, timing, venting and service procedures are omitted.")

TRAP = S("sink-trap", "Sink drain and P-trap", "Home", "Generic vented sink drain with a water-sealed trap",
    "The bend deliberately keeps water: that water separates room air from drain gases.",
    ("Sink outlet", "Water-sealed bend", "Drain and vent"), (
        B("Give used water a route", "flow", 0, "Wastewater leaves the sink and moves through the drain opening into the trap. This is a connected passage, not a solid pipe drawn over a moving dot.", "Water in the sink", "Water enters the drain", 0, "How Does a P-Trap Work?"),
        B("Keep a water barrier", "trap", 1, "The curved trap retains water below the outlet's spill level. New water can pass onward while a water seal remains. A trap is not meant to be empty after every use.", "Water passes through the bend", "A water seal remains", 0, "J-bend, weir and retained water seal"),
        B("Separate air, not just collect debris", "trap", 2, "The retained water interrupts the open gas path from the drain to the room. Venting helps protect that seal from pressure disturbances. If the trap dries, the same gas barrier is no longer present.", "Drain-side gases and room air", "Water interrupts the gas path", 1, "Water seals and the difference between P- and S-traps"),
    ), (R("Oatey: what a P-trap does", "https://www.oatey.com/faqs-blog-videos-case-studies/blog/what-p-trap-and-how-does-it-work", "Trap geometry, weir and a retained water seal preventing sewer gases entering the room."),
        R("Oatey: P-trap versus S-trap", "https://www.oatey.com/faqs-blog-videos-case-studies/blog/whats-difference-between-p-trap-and-s-trap", "Maintaining the water seal and avoiding siphoning.")),
    Q("Is water left in the trap automatically a blockage?", "Yes, a drain should always end dry", "No, retained water is part of its job", 1, "The bend is meant to retain a water seal while allowing incoming wastewater to displace water onward."),
    Q("If the retained water evaporates, does the shape alone still supply that water barrier?", "Yes, the pipe shape is an airtight wall", "No, the water seal is absent", 1, "The trap's protective barrier is retained water, not just the letter-shaped outline. A dry passage no longer contains that water seal."),
    1, ("Water seal present", "A continuous retained water region separates the gas spaces."),
    ("Dry-trap comparison", "The retained water is absent; the gas spaces have an open passage. This is a conceptual comparison, not a diagnosis."),
    "Generic vented drain, not a plumbing-code or repair guide. No seal depth, vent design or source of a real odor is diagnosed.", ("P trap", "kitchen sink drain", "sink plumbing"))

FAUCET = S("faucet", "Faucet and water pressure", "Home", "Generic ceramic-disc mixing faucet supplied by pressurized water",
    "Supply pressure drives the water; the cartridge changes which openings it can pass through.",
    ("Hot and cold supply", "Sliding ceramic discs", "Spout outlet"), (
        B("Start with a pressure difference", "flow", 0, "A supplied faucet has water at higher pressure than its open outlet. When there is a connected path, that pressure difference can drive flow. The handle is not an electric pump.", "Pressurized supply", "A possible path toward the outlet", 0, "Understanding Valves: hot/cold water enters the cartridge"),
        B("Change the openings", "valve", 1, "Moving a ceramic-disc cartridge changes the overlap of its holes. That changes how much hot and cold water can enter the mixing path. Closing the path stops sustained flow at the outlet.", "Handle movement", "Flow openings change", 0, "Understanding Discs"),
        B("Deliver a mixed stream", "flow", 2, "Water from the selected openings combines and leaves through the spout. The inlet temperatures and flow proportions determine the mixture; no universal handle angle guarantees one exact temperature.", "Selected hot and cold flows", "A mixed outlet stream", 0, "Understanding Valves: water combines inside the disc"),
    ), (R("Delta: how a faucet works", "https://www.deltafaucet.com/il/home-improvement-101/how-does-faucet-work", "Cartridge, sliding disc openings and hot/cold mixing; one faucet family."),),
    Q("Does opening a faucet create its supply pressure?", "Yes, the handle pumps water", "No, it opens a path from the supply", 1, "The supply provides the pressure condition. The cartridge changes access to the outlet."),
    Q("At fixed supply conditions, what does closing every cartridge opening do?", "Stop the sustained outlet flow", "Make water pass through solid ceramic", 0, "With no open path through the declared valve, sustained flow cannot reach the spout in this model."),
    1, ("Open passage", "The moving disc leaves an opening for water to pass."),
    ("Closed passage", "The disc covers the opening. The steady throughflow stops; transient pipe pressures and leakage are not modeled."),
    "One ceramic-disc cartridge, not all faucets. No pressure readings, temperature prediction, water-hammer simulation or service instructions.", ("tap", "water tap", "water pressure"))

PLUMBING = (TOILET, TRAP, FAUCET)
