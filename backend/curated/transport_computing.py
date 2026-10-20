"""Physical motion and logical computation use different, explicitly labeled models."""

from .plans import Step as B
from .plans import SystemPlan as S
from .plans import check as Q
from .plans import source as R

CAR = S("car", "Car", "Transport", "Gasoline-car motion overview; electric vehicles use a different energy converter",
    "Fuel becomes shaft work; gearing delivers torque; tire-road contact moves and slows the car.",
    ("Engine piston", "Drivetrain", "Tire and road", "Brakes"), (
        B("Release fuel energy", "piston", 0, "In a spark-ignition engine, fuel and air are admitted and compressed, then ignited. Expanding combustion gases push a piston. The crankshaft turns that back-and-forth motion into rotation; exhaust leaves for another cycle.", "Fuel-air mixture and ignition", "Rotating shaft work", 0, "How Does an Internal Combustion Engine Work?"),
        B("Deliver torque to the wheels", "gear", 1, "The drivetrain connects engine rotation to the driven wheels. Gearing trades speed and torque; it does not create energy. Useful motion is only part of the fuel energy, with substantial energy also leaving as heat.", "Engine shaft rotation", "Torque at driven wheels", 0, "Crankshaft and powertrain gears"),
        B("Push against the road", "grip", 2, "A driven tire pushes backward against the road at its contact patch. The road's frictional force can push the car forward. Without useful grip, a turning wheel alone does not guarantee acceleration.", "Wheel torque and road contact", "Forward force on the vehicle", 1, "Static and kinetic friction at contacting surfaces"),
        B("Steer and slow the result", "brake", 3, "Steering changes tire direction and contact forces. Brakes oppose wheel rotation, converting motion energy into thermal energy. Traction still limits the forces the road can supply; this is a qualitative overview, not a driving simulation.", "Motion and control inputs", "Direction changes or energy is dissipated", 1, "Frictional forces; qualitative mechanical-energy inference"),
    ), (R("DOE: internal-combustion engine basics", "https://www.energy.gov/cmei/vehicles/articles/internal-combustion-engine-basics", "Four-stroke spark ignition, piston, crankshaft and gearing; not an electric drivetrain."),
        R("OpenStax: friction", "https://openstax.org/books/college-physics-2e/pages/5-1-friction", "Contact forces and static versus sliding friction; the vehicle example is a qualitative application.")),
    Q("Is a fast-spinning driven wheel enough to guarantee that the car accelerates?", "Yes, wheel speed is vehicle speed", "No, useful tire-road force is needed", 1, "The wheel must exchange force with the road. Spinning without suitable grip does not guarantee useful forward acceleration."),
    Q("Where does much of a car's motion energy go during ordinary friction braking?", "Into thermal energy", "It is destroyed", 0, "Friction brakes convert mechanical energy into thermal energy. Regenerative braking is a different additional energy pathway, outside this gasoline-car overview."),
    2, ("Useful contact force", "Tire-road interaction can provide the indicated forward force."),
    ("No-grip idealization", "The wheel can turn while the modeled forward contact force is absent. This is a limiting thought experiment, not a tire or road prediction."),
    "Gasoline powertrain plus traction/braking overview. No engine timing, tire coefficient, stopping distance, emissions calculation or vehicle-specific service detail.", ("automobile", "gasoline car", "petrol car"))

GPU = S("gpu", "GPU", "Technology", "Illustrative data-parallel computation, with CUDA as one documented example",
    "A program defines work; memory supplies inputs; parallel execution produces stored results.",
    ("Program", "Input memory", "Execution lanes", "Output memory"), (
        B("Describe many similar jobs", "compute", 0, "The CPU-side program submits work for the GPU. Each logical work item has an identity so it can select its own input and output. A drawn lane is not a literal chip core.", "Program and work-item identities", "A defined set of calculations", 0, "Thread hierarchy and unique thread identities"),
        B("Bring the data to the work", "compute", 1, "Execution needs operands from memory. Inputs are read, calculations transform them, and outputs are stored for later use. More arithmetic capacity cannot compute an input that has not arrived.", "Available input data", "Calculated and stored results", 1, "Memory hierarchy and kernel execution"),
        B("Use independence, respect dependencies", "compute", 2, "Independent items can make progress together within available resources. Dependent work must wait for its required result. Memory movement, synchronization and the problem's structure limit performance; a GPU is not always faster.", "Ready work and finite resources", "Concurrent progress where permitted", 0, "Synchronization and memory hazards"),
    ), (R("NVIDIA: writing SIMT kernels", "https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/writing-cuda-kernels.html", "Work-item identity, parallel execution and synchronization for dependencies. CUDA is not every GPU."),
        R("NVIDIA: programming model", "https://docs.nvidia.com/cuda/archive/13.2.2/cuda-programming-guide/01-introduction/programming-model.html", "Kernel launch, thread groups, memory and finite execution resources.")),
    Q("Does adding more execution lanes guarantee a proportional speedup?", "Yes, twice the lanes always halves the time", "No, data and dependencies can limit progress", 1, "Available arithmetic capacity is only one constraint. Work must be ready and supplied with data; coordination and transfers also matter."),
    Q("Can a calculation produce the right answer before a required input exists?", "Yes, spare lanes can invent it", "No, the dependency must be satisfied", 1, "A correct computation uses its required operands. Waiting is a consequence of the dependency, not evidence that the program should guess the missing value."),
    1, ("Inputs available", "The declared operations can consume their available operands."),
    ("Required input withheld", "Dependent work waits and its output is not fabricated. Other independent ready work can still proceed."),
    "Logical teaching diagram, not an actual GPU die, scheduler trace, benchmark or universal CUDA architecture. No core counts or performance numbers are claimed.", ("graphics card", "graphics processing unit"))

TRANSPORT_COMPUTING = (CAR, GPU)
