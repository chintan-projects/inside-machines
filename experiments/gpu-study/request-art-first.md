# Author the artwork for a GPU learning figure

Return only JavaScript, no fences, no HTML document. This is a local manually
reviewed art spike. Our trusted shared player and pure scheduler supply all state.
Do NOT author a player, controls, timers, event listeners, physics or scheduler.
Expose exactly window.createGpuArt = function(Anatomy) { ... return {board, work}; }.
Use the actual supplied Anatomy kit k/G/T. No imports/network/assets/storage/eval.

board() returns {svg, labels, caption}, a beautiful 720×620 isometric graphics-board
illustration. labels is [{text,x,y}] in those viewBox coordinates; our HTML labels
remain 14px on a phone. SVG is its INNER markup (we own the outer svg.iso), with
filled materials, real four-tone shading, no wireframes. Use .iso styling from k.
Construct a green/blue PCB, a substantial center chip package with reflective die,
surrounding black memory packages, tiny real capacitors, mounting holes, gold edge
contacts, a short metal bracket and coherent copper/etched traces. The cooler is
omitted to expose the board; caption says so. Chip/memory/connector are generic
context, not exact vendor layout. At 1× it must read as one carefully made object;
at 4× detail belongs to components. Fit it large in the frame, not tiny amid labels.
No filler screws invented to hit a count. Anchored core labels: GPU chip, Memory,
Connection to computer. Material helpers MUST set --anatomy-paper/hi/top/shade-0…3
and SVG must carry .iso from host. Use only documented signatures. k.slabOf +
k.solidSvg for important parts, k.cylinder for mounting rings, k.planOutline etc.

work(pose) returns {svg,labels,caption} at 720×620, an enlarged LOGICAL working view.
Think an interactive science-book plate: eight numbered pixel jobs across a top
input strip, four substantial execution rows below, a result strip at the bottom.
This is explicitly a toy logical diagram, NOT a physical miniature factory or die.
Make the currently running arithmetic big and beautiful. Show what is waiting
and what is done by shape + words as well as colour. Stable A–H IDs connect input
to row to result. Work rows are labeled “Lane 1” … “Lane 4”. Disabled lanes should
be clearly unavailable when laneCount=1; available unused lanes are “Idle”, not busy.
Include a small recognizable version of the board as locator if it fits without
compromising the mechanism. Clear top-to-bottom dependencies; no fluid particles.

pose is immutable and ALREADY computed. Its contract:
{
  mode: 'independent'|'chain', laneCount:1|4, dataReady:boolean,
  round:number, totalRounds:number, progress:number /* 0..1 within current round */,
  jobs: Array<{id:string, input:number|null, output:number|null,
    status:'ready'|'waiting'|'running'|'done', lane:number|null,
    prerequisite:string|null}>,
  lanes: Array<{index:number, enabled:boolean, jobId:string|null}>
}
Never recompute the schedule, outputs, round counts, readiness or scenario outcome.
Use pose exactly. In the chain scenario inputs stay null until the predecessor's
result exists. Draw null as “needs A”, never fabricate a value. For running jobs
show e.g. “3 + 1” and progress from pose.progress; output numbers only once done.
Result strip completed values 1–8; blank/waiting results are distinct. For chains
show explicit prerequisite direction A→B→… (the arrow means needs previous answer).
For independent jobs every row does the SAME instruction on its own input; do not
invent different operators per lane. dataReady=false means no running/done jobs.
No CPU-vs-GPU comparison, GHz, power, memory size or real speedup readouts.

Legibility constraint: native 720×620 drawing displayed at374px wide; core labels
use host HTML tags so 14px phone is preserved. Ordinary SVG text needs ≥24viewBox
units (12.5px on phone); running equations ≥32, status ≥24. Avoid overlap, tiny
upper legends and too much text. Return short labels at uncluttered coordinates;
our host positions them as percent of720×620. Keep all content withinx16..704 and
y20..600. Standard labels fit x70..640, not directly on the edge.

The shared player supplies headline, actions, prediction and explanatory captions.
Artwork has no external font/assets, no random/autoplay, no assumptions about DOM
IDs. board/work are pure functions, deterministic for the same pose. Return only
the JavaScript registration. Aim for180–320 readable lines using small helpers.
