# Refrigerator physical artwork for a shared learning player

Return ONLY JavaScript, no fences, no HTML. This is a manually inspected local
artwork study. Expose window.createRefrigeratorArt = function(Anatomy) { ... };
return {overview, evaporator, compressor}. Each is a pure function of pose and
returns {svg, labels, caption, alt}. svg is INNER markup for our svg.iso. Labels
are [{text,x,y}] in a 720×620 viewBox and rendered by our shared HTML overlay.
Use the supplied actual k/G/T toolkit, not an imitation. Important filled solids
must use k.slabOf/k.solidSvg or documented lathe/tube builders. Match signatures.
No player, timers, controls, DOM, network, imports, physics, storage or random.

Our trusted domain supplies pose:
{focus:'whole'|'inside'|'compressor'|'outside'|'restrictor',
 running:boolean, progress:number /*0..1 visual phase*/,
 piston:number /*0..1, 0=large chamber, 1=small chamber*/,
 intakeOpen:boolean, outletOpen:boolean}
Do not infer pressure, refrigerant phase or energy quantities from pixels.
The SAME cycle continues during every focus; focus selects attention, not which
part runs. If not running, no moving flow cues. No cold-gas clouds outside pipes.

overview(pose): a beautiful generic domestic refrigerator with a front/side
section removed to reveal a substantial insulated cabinet, cavity, two shelves,
a few recognizable food vessels and an open door/door seal as a cutaway aid.
This door is opened for illustration, not the energy experiment's physical state.
Use an elegant warm-white steel shell, layered insulation, glass shelf edges,
small feet, hinge detail. Show an internal cold coil on the rear cavity wall,
an EXPOSED rear condenser coil on a visible offset side/rear service plane and a
substantial dark compressor on a base with mounts, ports and copper lines.
Expose the refrigeration loop for learning: vapor line from internal coil to
compressor inlet; hot vapor outlet to OUTSIDE coil; liquid line from outside coil
to a NARROW capillary, then returning to internal coil. Label the capillary.
Hide/cut a wall honestly to expose connections, never route a pipe through solid
parts. A schematic service layout is allowed but say so. Coils must read as
continuous fitted tubing, not floating circles. No transparent solid wireframes.
Keep physical painter order, filled materials and coherent short shadows.
Core anchored labels: Cold coil, Compressor, Warm coil, Narrow tube.
Labels must sit at uncluttered anchors x90..630,y35..575 with short leader/dot
to the actual part. At phone width labels are 14px, so distribute without overlap.
Leave the appliance large in the frame. Do NOT squeeze four labels above it.

evaporator(pose): an independently composed enlarged SECTION of the cold coil
WITH a visible tube wall and adjacent cabinet air/liner. Show cool liquid entering
one end, a visibly mixed liquid/vapor region and vapor leaving toward compressor.
Broad heat arrows point from the surrounding cabinet air THROUGH the wall into
the refrigerant. Refrigerant arrows stay INSIDE its passage. Distinguish heat by
wide wavy arrows and refrigerant by thin solid direction arrows, not color alone.
Core labels: Cabinet air, Tube wall, Liquid + vapor, Vapor to compressor.
This is an illustrative phase-change section, not literal bubble simulation.
Use physical volume/metal thickness and context, not isolated liquid dots.

compressor(pose): an independently composed large section of one reciprocating
compressor EXAMPLE. Show cylinder, piston supported by rod/crank, motor section
and housing outline/base; inlet passage on one side, outlet on the other. A small
closed gas volume above the piston shrinks as pose.piston increases. Piston never
passes through head/valves. Render valves open only from pose flags; intake vapor
and discharge vapor use separate paths. Label Low-pressure vapor, Piston,
High-pressure vapor, Motor. Short pipe stubs terminate on actual ports.
Show a mechanical reason for compression, not an illuminated outside shell.
Caption MUST say this is one compressor design; real refrigerators vary.
Use pose only for geometry/attention. Do not invent ideal-gas readings.

All views: 720×620, stable deterministic coordinates, content in x16..704,y20..600.
Use k.fitProjection with ALL extremes then k.iso for label anchors; don't add
undocumented projections. Material groups set --anatomy-paper/hi/top/shade-0..3.
Use tones for metal/volume; cool blue and copper/orange identify appropriate coils,
never arbitrary AI glow. Fine detail must belong to actual parts: seam, fitting,
hinge, shelf edge, mounting grommet. A few purposeful details beat a part quota.
No tiny instructional SVG text: labels are HTML; any important SVG text≥28 units.
State/meaning must be conveyed by label, geometry and direction as well as color.
No source URLs in generated code. Short truthful caption/alt for each view.
Aim for 250–380 readable lines; reuse helpers. Our shared D1 player owns all UI,
narration, explanation, assessments, optional depth and return to whole.
