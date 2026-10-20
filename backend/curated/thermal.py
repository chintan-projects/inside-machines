"""Small thermal appliances with source-specific controls and honest stored-energy limits."""

from .plans import Step as B
from .plans import SystemPlan as S
from .plans import check as Q
from .plans import source as R

KETTLE = S("electric-kettle", "Electric kettle", "Kitchen", "Generic automatic electric kettle",
    "The heater adds energy to water; boiling and automatic shutoff are different jobs.",
    ("Heating element", "Water vessel", "Steam control"), (
        B("Supply heat", "heat", 0, "An electrical heating element transfers energy through its surface into water. Moving water redistributes this energy. Electricity supplies the heat; the switch decides when that supply is connected.", "Electrical energy", "Energy enters the water", 0, "Heating and boiling: electrical heating and water vessel"),
        B("Form vapor", "tank", 1, "As water reaches its boiling condition, some liquid becomes vapor. Continued phase change needs energy. Boiling temperature depends on the surrounding pressure, rather than one universal setting for every altitude.", "Liquid at its boiling condition", "Vapor forms", 1, "Phase changes and latent heat"),
        B("Detect and switch off", "valve", 2, "In this steam-controlled example, steam reaches the automatic control and interrupts the electrical supply. The water stays hot after switch-off because it still contains stored thermal energy.", "Steam reaches the control", "Heating supply interrupted", 0, "Steam used to switch the kettle off automatically"),
    ), (R("Russell Hobbs: kettle operating principles", "https://core-cdn.russellhobbs.com/pdf/rhk32_fa_140113.pdf", "Heating, automatic shutoff and steam used to operate the control; one documented design."),
        R("OpenStax: phase change and latent heat", "https://openstax.org/books/college-physics-2e/pages/14-3-phase-change-and-latent-heat", "Phase change requires energy; liquid/vapor behavior depends on conditions.")),
    Q("Does the switch remove the heat already in the water?", "Yes, off means cold", "No, it stops additional electrical input", 1, "Switching off disconnects an energy source. It does not instantly remove stored thermal energy from the water or vessel."),
    Q("At a lower outside pressure, must water still boil at the same temperature?", "Yes, every kettle fixes that temperature", "No, the boiling condition depends on pressure", 1, "A kettle supplies heat; it does not set the water's phase diagram. Changing ambient pressure changes the boiling condition."),
    0, ("Heater supplied", "Electrical energy continues to enter the water."),
    ("Supply switched off", "New heater input stops, while already-hot water retains energy. Cooling is not instantaneous."),
    "A conceptual steam-controlled design, not an internal wiring diagram. No boiling time, temperature or protection performance is predicted.", ("kettle",))

PRESSURE = S("pressure-cooker", "Pressure cooker", "Kitchen", "Generic electric pressure cooker",
    "Heat supplies energy; confinement changes the boiling condition; controls manage operation.",
    ("Heater", "Sealed vessel", "Controller and regulator"), (
        B("Put energy into the contents", "heat", 0, "The electric heater transfers energy into the vessel and its contents. Liquid can become vapor. Pressure is not an extra source of energy; the energy still comes from the heater.", "Electrical input", "Stored heat and vapor", 0, "How pressure cooking works: heating and steam"),
        B("Change the boiling condition", "tank", 1, "Restricting vapor escape lets pressure rise as the contents heat. Water can then boil at a higher temperature than in an open pot under the same outside conditions.", "Heated confined contents", "Higher boiling temperature possible", 0, "Increased pressure raises the boiling point"),
        B("Manage the energy supply", "valve", 2, "The controller manages heating while regulating and safety features constrain operation. The heat source, seal and controls do different jobs. Their details depend on the actual appliance.", "Feedback about operation", "Heating is managed", 1, "Automatic temperature control and pressure regulation"),
    ), (R("Instant Pot: pressure cooking principles", "https://instantpot.co.uk/how-does-pressure-cooking-work/", "Heating confined contents and the pressure-dependent boiling condition."),
        R("Instant Pot: control functions", "https://www.instantpot.com.ph/safety-features/", "Automatic temperature control and pressure-regulation functions; exact design varies.")),
    Q("What supplies the cooking energy?", "The heater", "Pressure creates new energy", 0, "The heater supplies energy. Confinement changes which pressure and boiling conditions can be maintained."),
    Q("If heating stops, must the pressure vanish immediately?", "Yes, pressure is the power switch", "No, stored energy remains", 1, "The contents retain thermal energy. Cooling and condensation take time; switch position does not establish the remaining pressure."),
    1, ("Confined vapor", "Continued heating and restricted escape can maintain pressure above ambient."),
    ("Open-pot comparison", "Vapor can leave toward ambient pressure; the same pressure-cooker condition cannot be maintained."),
    "Thought experiments only, not operating or repair steps. Exact pressure, temperature, release behavior and protections require the actual manual.", ("instant pot", "electric pressure cooker"))

ESPRESSO = S("espresso-machine", "Espresso machine", "Kitchen", "Generic pump-driven espresso system",
    "A heater warms water; a pump drives it through a resisting bed of ground coffee.",
    ("Pump", "Water heater", "Coffee bed", "Cup outlet"), (
        B("Move water from the reservoir", "piston", 0, "A pump supplies the pressure difference that moves water through the brewing path. This is not steam pushing water from a moka pot; different coffee machines use different mechanisms.", "Reservoir water", "Driven water flow", 0, "Pump and extraction system"),
        B("Supply thermal energy", "heat", 1, "A boiler or flow-through heater warms the water. The heater controls thermal input; the pump supplies mechanical work. These are separate jobs even when one controller coordinates them.", "Cooler supply water", "Heated brew water", 0, "Thermocoil heating system"),
        B("Pass through a porous coffee bed", "filter", 2, "Water passes among coffee particles and carries dissolved material into the cup. Finer or more compact grounds can resist flow more. Pressure, temperature and time interact; a pump rating is not a flavor guarantee.", "Hot water at the coffee bed", "Coffee solution at the outlet", 1, "Extraction guidance: flow too fast or slow through ground coffee"),
    ), (R("Breville: pump and heating example", "https://www.breville.com/en-us/product/bes870", "Pump-driven extraction and a controlled thermocoil heater; specifications are not generalized."),
        R("Breville: extraction and coffee-bed flow", "https://assets.breville.com/BES870/BES870_USCM_IB_O21.pdf", "Extraction guidance and how grind/flow conditions alter the result.")),
    Q("Does a higher pump rating alone guarantee better espresso?", "Yes, pressure alone determines flavor", "No, flow, heat and the coffee bed matter", 1, "The pump, heater and coffee bed have different roles. A quoted pump rating is not the complete brewing condition."),
    Q("At a fixed pressure difference, what does more flow resistance tend to do?", "Reduce the flow", "Make water ignore the coffee bed", 0, "A more resisting porous bed restricts flow under the declared fixed-pressure comparison. This is qualitative; no extraction recipe or flavor prediction is supplied."),
    2, ("More open bed", "The illustrated water path has lower resistance."),
    ("More resisting bed", "Less water passes in the declared comparison; particles still occupy a porous bed, not an airtight solid."),
    "Generic pump-driven path. Pump design, boiler/thermocoil, pressure regulation and extraction conditions vary; no universal brewing numbers.", ("coffee machine",))

WATER = S("water-heater", "Water heater", "Home", "Generic electric storage water heater",
    "A tank stores hot water; cold replacement water enters as hot water is drawn.",
    ("Immersed heater", "Insulated tank", "Cold inlet and hot outlet", "Thermostat"), (
        B("Heat and store water", "heat", 0, "Immersed electrical elements transfer energy into the tank's water. Insulation slows energy leaving the tank. This example uses electric resistance heating rather than gas combustion or a heat pump.", "Electrical input", "Thermal energy stored in water", 0, "Technology Overview: Conventional Storage"),
        B("Replace what is drawn", "flow", 2, "Hot water is drawn from the upper outlet while supply water enters through a dip tube toward the bottom. A full tank can deliver hot water without emptying like an open bucket.", "Cold replacement water", "Hot water delivered from the top", 1, "Dip Tube definition"),
        B("Maintain the stored supply", "valve", 3, "Temperature controls manage heater input as stored water cools or is replaced. The tank has a finite thermal store; enough continued draw can use it faster than the heater restores it.", "Temperature feedback and draw", "Heating input managed", 0, "Conventional storage maintains a tank set point"),
    ), (R("DOE/NREL: residential water heaters", "https://www.energy.gov/sites/prod/files/2014/01/f7/20110224_residential_water_heater_webinar.pdf", "Conventional electric storage: immersed elements, insulation, dip tube, outlet and thermostats."),
        R("Rheem: water-heater components", "https://www.rheem.com/producteducation/", "Dip tube directs incoming cold water toward the bottom.")),
    Q("Must the tank empty before fresh water enters?", "Yes, it behaves like a bucket", "No, supply replaces water as it is drawn", 1, "In the supplied storage system, incoming water replaces the drawn volume. The dip tube and upper outlet help preserve a hot-water layer."),
    Q("Could hot water continue briefly after heater power is stopped?", "Yes, stored hot water still has energy", "No, power-off instantly makes it cold", 0, "The tank stores thermal energy. How long it can supply a useful temperature depends on draw and the appliance, which this model does not predict."),
    0, ("Heater input on", "Energy enters the water through the immersed element."),
    ("Heater input off", "Additional input stops. Stored thermal energy remains and is not erased by the switch."),
    "Simplified electric storage tank. Stratification, mixing, controls, corrosion protection and relief devices are not simulated; no service instructions.", ("hot water heater", "geyser"))

HEATPUMP = S("heat-pump", "Heat pump", "Home", "Generic reversible air-source heat pump",
    "The cycle moves heat; a valve changes which coil receives hot refrigerant.",
    ("Outdoor coil", "Compressor", "Indoor coil", "Reversing valve", "Expansion device"), (
        B("Collect heat from outside", "coil", 0, "In heating mode, cold refrigerant can absorb energy from colder outdoor air that is still warmer than the refrigerant. Cold weather does not mean there is no thermal energy outside.", "Outdoor air and colder fluid", "Heat enters the refrigerant", 0, "How heat pumps work: heating mode"),
        B("Add work and deliver heat", "piston", 1, "The compressor adds work and raises the vapor's pressure and temperature. The indoor coil then releases heat into the home as refrigerant condenses. Indoor heat includes collected outdoor energy plus supplied work.", "Collected heat and work", "Heat delivered indoors", 0, "Heat transfer and compressor work"),
        B("Restore the cold supply", "restrictor", 4, "After releasing heat, the liquid passes an expansion device. The pressure drop supplies a colder mixture to the outdoor coil in heating mode. The compressor and restriction maintain different pressure regions in the operating loop.", "Higher-pressure liquid", "Colder low-pressure mixture", 1, "Heat Pump Basics: refrigerant expansion and coil roles"),
        B("Reverse the job", "valve", 3, "A reversing valve redirects refrigerant so the coils exchange roles. In cooling mode, the indoor coil collects heat and the outdoor coil releases it. The compressor is not simply a fan running backward.", "Changed refrigerant routing", "Coils exchange heating/cooling roles", 1, "Appendix: Heat Pump Basics, Reversing Valve"),
    ), (R("DOE: heat pump systems", "https://www.energy.gov/energysaver/heat-pump-systems", "Heat transfer between home and outdoors, work input and reversible operation."),
        R("DOE/NREL: heat pump system basics", "https://betterbuildingssolutioncenter.energy.gov/sites/default/files/attachments/87812.pdf", "Appendix: reversing valve and coil roles.")),
    Q("Does cold outdoor air mean there is no energy to collect?", "Yes, cold means no thermal energy", "No, heat can move into still-colder refrigerant", 1, "Heat transfer depends on the temperature difference. The working fluid can be colder than outdoor air; available capacity still depends on conditions."),
    Q("What must change to cool the house instead?", "The coils must exchange their heat-transfer roles", "Only the indoor fan needs to reverse", 0, "Refrigerant routing changes which coil absorbs and which rejects heat. Air movement alone cannot reverse the refrigeration cycle."),
    3, ("Heating role", "The indoor side receives heat from the hot refrigerant."),
    ("Cooling role", "Routing changes: the indoor side supplies heat to colder refrigerant. This is a mode comparison, not a valve-transition simulation."),
    "Qualitative reversible cycle. Defrost, auxiliary heat, real performance, refrigerants and weather limits vary; no efficiency or capacity numbers.")

THERMAL = (KETTLE, PRESSURE, ESPRESSO, WATER, HEATPUMP)
