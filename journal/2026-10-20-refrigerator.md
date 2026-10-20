# Refrigerator R1: transfer the learning framework to a physical loop

Owner asks for a refrigerator or car explanation using the selected principles.
Chose refrigerator: one bounded mechanism tests shared-framework transfer and
connects observable cold food/warm exterior to a complete heat-transport story.
This is a local candidate using Claude + actual Anatomy, not a production release.

Worksheet, falsifiable 4/5 beginner hypothesis, R1–R7 claim ledger and transfer
rubrics: `experiments/refrigerator-study/BRIEF.md`. Review record:
`design/lessons/refrigerator.md`. Applied product-sense and design-quality guidance,
the shared D1 design brief, ADRs 0001/3/4/5 and CE-01–18. Creator principles are
explicit design choices, not claims of endorsement or measured learning benefit.

## Teaching and source decisions

Core 104 seconds: heat enters a cold coil through its wall; liquid evaporates;
compressor adds work; hot coil rejects heat and condenses vapor; capillary returns
the low-pressure mixture; reassemble the simultaneous loop. Cold/warm coils,
compressor and narrow tube keep stable labels. Each working section includes its
own surroundings and input/output. Chapter focus never switches the other parts
off. Stopped comparison fixes the crank/rod/piston and closes the illustrative
valves; it expressly omits residual transient heat transfer.

Optional 68-second energy branch makes 3+1=4 visible, then changes the boundary
to one room: 4−3=1 added. Values are declared illustrative energy units, not an
appliance's measured efficiency, temperature or rate. Real door opening changes
loads; closed-cabinet passive heat leaks are not modeled. Optional 62-second phase
branch compares assumed conditions for the same fluid: chosen temperature at the
lower-pressure boiling point, below the higher-pressure one. Higher pressure
does not imply zero heat absorption. The earlier draft wording “between” boiling
points was corrected before this build; no pressure-change transient is claimed.

GE's sealed-system steps 1–7 support the circuit. OpenStax §15.5 supports the
energy balance; same-room net work is our inference. Danfoss §2.6/2.7/2.8 and the
circuit/capillary sections support phase/pressure and vapor warming. Sources and
locators are linked within every node. This is source grounding by the authoring
agent, not independent technical review or a product-specific service diagram.

Prediction is optional before playback, with an initially hidden answer and
Show me escape. Transfer asks about failed heat rejection, heat rejection outside
the kitchen, and a vapor-only tube region. Answers are hidden until deliberate
reveal. Assessment state is ephemeral; no learner answers are sent or logged.
Core labels, physical surroundings, separated heat/material encodings, optional
depth and question lookup use shared components rather than a refrigerator UI fork.

## Paid work and provenance

The existing trusted CLI/gateway/registry/config/logger/Store accounts for both
requests. No new provider service, fallback, retry policy or transaction change.

| Operation | Outcome | Input / output tokens | Configured-rate charge |
| --- | --- | --- | --- |
| fridge-art-1 | Failed closed: max_tokens, known billing | 19663 / 16000 | $0.199326 |
| fridge-art-2 | Distinct narrower locator request completed | 18949 / 4904 | $0.086938 |

Actual returned model identity: `claude-sonnet-5-5`. Total $0.286264; trial account
$4.568218 of the unchanged $5 cap, reserved $0, no uncertainty. These are token-rate
ledger amounts, not an audited invoice. The first incomplete response remains
failed; it was not presented as a successful artifact. After inspecting that
receipt, the second request reduced three views to one physical locator. No paid
work follows it. Narration uses local Samantha/FFmpeg with $0 API cost.

Original response remains private. Explicit reproducible repairs qualify a kit
helper, correct projection bounds and capillary connectivity, anchor labels on
actual parts, separate phone labels and add directed refrigerant chevrons. Codex
authored the independent mechanism sections and energy/phase scenes. Do not
attribute all visuals or narration to Claude. The shared packer binds the exact
response, repair chain, actual Anatomy runtime, scripts, audio and path hashes.
The final brief includes later reviewed assumptions and is not the original
dispatched prompt; rerunning a mismatched paid operation is intentionally refused.

## Three bounded craft rounds

1. Physical/section views: phone review found Compressor and Narrow tube labels
   overlapping. Corrected their positions with anchored leaders. The new consumer
   also exposed GPU-only interface copy; shared wording is now topic-neutral.
2. Energy/phase views: arrows crossed energy numerals and the phase heat arrow
   ended at the tube wall. Moved numbers/arrow ends apart and extended heat into
   the fluid. Added the non-blocking pre-watch prediction and neutral phase intro.
3. Final verification: 375px whole/compressor/phase, 768px warm coil/capillary,
   1440px open-door energy view. No horizontal overflow, SVG text outside the
   actual transformed scene, HTML label collisions or visible controls below 44px
   in these samples. Smallest section text is 14.58px at 375px. An initial geometry
   check ignored the moving piston label's parent transform and produced a false
   clipping signal; corrected to actual client rectangles and checked the render.

Private `fridge-r1-browser-review.json` and `fridge-r1-final-*.jpg` record observed
results. Source/bounds inspection and sampled renders do not prove a complete
all-frame audit. Phone/tablet dimensions are Chrome emulation, not physical devices.

Observed browser journeys: prediction hidden/reveal; pressure comparison retains
heat transfer; decoded audio advances, mute, pause and seek; manual scenarios stop
fixed narration; typed ordinary depth opens energy and pauses old audio; Back
restores the exact paused 0.431422-second core state; stopped compressor remains
stationary when seeking; open-door state shows the same domain 3/1/4/net1 values;
unsupported car query reports missing saved coverage. Fresh branch playback works
with network disabled and reduced-motion stills. Media ends at 68 seconds paused;
Reset restores zero/automatic controls. Keyboard focus has a solid 3px outline.
No warning/error console entries observed. Offline/media preferences and temporary
viewport override were restored; final tab is fresh, paused at core time zero.
These checks do not prove physical speaker output, natural voice quality or a full
screen-reader/WCAG audit.

Final refrigerator HTML SHA:
`baa8eb1955889a696755c693331bdc82ef9ab0ad552f7d78400212dd810c7a4e`.
The existing GPU D1 hash remains
`f87a9ae65c8a180bf60379ba0d5298b56fa3e73e7212ee4388ca2fa317313c55`;
vacuum remains
`2df631dc2c5164bf191fb304dd77f82849d529ccb54783ee647a9f187a11ddba`.

## Verification and judgment

Ruff, strict mypy (79 files), 199 backend tests/87.79% coverage; frontend strict
types/lint/10 tests/build; studio types/lint/25 tests pass. New tests check the
real slider-crank fixed rod length, valve/chamber direction, stopped pose, energy
conservation, pressure comparison limits, cue seeking and trusted prompt isolation.
Three external Postgres cases skipped; no transaction change. Linux deployment
packaging not rerun; no deployment packaging change. No push or Vercel deployment.

Agent rubric: utility 4/5, inferred the complete circuit and two branches address
the question; usability 4/5, observed labeled scenes and native controls work;
desirability 3/5, conservative D1 composition and computer voice need owner taste
judgment; surprise 4/5, inferred the door-open boundary and cold-boiling comparison
can correct common intuitions. Scores are agent judgment, not user/learner approval.

Engineering and sampled agent craft are observed. Independent technical truth,
owner actual-phone taste/accessibility and five-beginner causal transfer remain
unmeasured. No editorial model review was run. This non-LessonSpec HTML is outside
the production `backend.quality` publication pipeline and has no structural,
editorial or human publication verdict. Adopting it in production still requires
trusted declarative translation, all current source/quality gates, checkpoint
alignment for exported media and immutable revisions. BUG-004 remains open.
This implements a local second-domain candidate, not the broader product quality
goal, automatic arbitrary-topic generation, car lesson or family release.
