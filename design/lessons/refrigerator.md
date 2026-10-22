# Refrigerator R1 lesson record

Build specification and claim ledger:
[R1 brief](../../experiments/refrigerator-study/BRIEF.md).
Iteration 2026-10-20; local build requested by owner as a transfer to another concept.
Use the shared D1 design and teaching anchors, not a new player or model gateway.
Hypothesis, causal storyboard, R1–R7 claim sources, transfer rubrics and review plan
are in that brief. Implementation/evidence: [R1 journal](../../journal/2026-10-20-refrigerator.md).

## Implemented local candidate

Core: 104-second narrated heat-transport loop, with a labeled physical locator,
independent evaporator/compressor/condenser/capillary sections, then the whole
system. Optional paths: a 68-second energy-boundary explanation and a 62-second
pressure/boiling comparison. The shared D1 player, controls, audio/caption clock,
versioned path and question lookup are reused. Local saved lookup is not AI chat.

CE-01/02/03/06/13: one question/outcome, optional pre-watch prediction,
job-before-name narration and changed-situation transfer with hidden answers.
CE-04/05/07/11: own-context mechanisms with labels, heat/material encodings,
and an explicit simultaneous-operation reassembly.
CE-08/09/10: pure domain state; fixed-length slider crank, stopped comparison,
declared 3+1=4 energy example and assumed pressure cases. No appliance simulation.
CE-12/15: source locations and visible assumptions; human review remains separate.
CE-14/16/17/18: silent captions, cue stills, deterministic seeking, saved offline
audio and immutable source/hash chain. No MP4 export in this local slice;
actual-phone and screen-reader review are pending.

Engineering checks and three-width agent craft inspection passed for this
candidate; they do not establish factual certification, owner taste approval or
the 4/5 beginner hypothesis. No independent technical, actual-device or beginner
session has occurred. This non-LessonSpec HTML has no production quality verdict,
editorial approval or catalog publication. BUG-004 remains open; Vercel unchanged.

## R2 active worksheet · 2026-10-22

Status: planned reference refinement; no release or human acceptance.
Size: **Figure** — one connected cooling-loop reference with a detailed compressor
section, using the actual vendored Anatomy kit. The existing R1 core/energy/phase
sources and packed HTML remain historical and unchanged. New IDs are
`refrigerator-r2-core`, `refrigerator-r2-energy`, `refrigerator-r2-phase`.

Person and job: an initially unfamiliar curious learner, age 8–80, asking where
food's heat goes and why the refrigerator needs electricity. Observable outcome:
trace heat into the cold coil, work into the compressor, and heat out to the room;
then reason about a changed room boundary without calling heat “cold air.”

**One falsifiable hypothesis:** after the R2 core and optional energy branch,
at least four of five learners who lacked this understanding at baseline can
trace that energy path and explain why an open fridge does not cool the whole
closed kitchen, scoring 2 on both teach-back and transfer before reveal. The
intervention is a persistent physical loop with clearly different heat and
refrigerant paths, plus the same labeled compressor shown in a substantial
working section. No results have been collected.

### Diagnosis and boundaries

Observed in source: R1 already has genuine Anatomy cabinet geometry, a sealed
loop and three native shared-player adapters. Its physical whole view has no
visible electrical input or heat entering/leaving it; most causal motion occurs
in flatter SVG sections. The transition can make those sections feel unrelated
to the machine. The native R1 is substantially better than the later generic
hosted `refrigerator-studio-1` panel; they must not be called equivalent craft.
Inferred: the missing shared physical/energy identity is a larger learning
failure than another visual effect. Root's rendered review will check that
inference against actual scenes. The motivating drone is a craft reference for
recognizable connected hardware, not a measured quality comparison or a layout
to copy.

Teach the generic vapor-compression loop and one reciprocating compressor example.
Keep the existing truthful 3+1=4 illustrative balance and pressure/boiling branch.
Do not add repair instructions, refrigerant-specific temperatures, real pressure
readings, a claimed cycle frequency, a thermodynamic simulation or a universal
compressor design. No paid model call or new speech synthesis in this iteration.

### Teaching anchors and mechanism

| Anchor | R2 choice |
| --- | --- |
| Grant | The physical heat path stays visible through the whole view; the energy branch transforms the same removed/work/released quantities. |
| Feynman | Start with the job: carry heat out. Establish the colder fluid and electrical work before technical names. Captions state what the cutaway omits. |
| Veritasium | Optional open-door prediction; reveal by changing the room boundary; transfer asks about placing the warm coil outside the room. |
| Anatomy | Real kit solids, layered cabinet, fittings, motor/crank/piston, supported pipes and stable labels. Purposeful parts carry the causal change. |

Core components retain IDs `cold-coil`, `compressor`, `warm-coil`, `capillary`;
`cabinet` and `electrical-input` provide physical context. Material follows a
sealed loop. Heat crosses coil walls. Work enters the compressor. These jobs run
simultaneously under sustained operation; the storyboard only moves attention.
Shared R1 pure rules remain authoritative: fixed crank/rod length, mutually
exclusive illustrative valves, stopped pump comparison, energy conservation and
chosen pressure cases. Rendering must not reimplement their causal outcomes.

Purposeful Figure parts, grouped before geometry: four feet and mounts; base,
inner floor, back insulation, two side walls, top trim, two door seals, two hinge
bodies, two shelf rails and two shelves; food vessel/base/lid; cold coil runs,
suction coupling, suction return, compressor feet, shell/base, electrical
terminal/cable, motor housing, motor shaft/bearing, crank arm/pin, connecting
rod and bearings, piston/crown/seal, cylinder back and side walls, valve plate,
inlet/outlet and reeds; warm-coil bracket/runs/fittings, liquid line, capillary
inlet/bore/outlet and return. Insets may omit decorative parts that hide motion.
This is a parts plan, not an assertion that geometry has passed a kit audit.

### Claim ledger (R1 facts rechecked 2026-10-22)

| ID | Claim | Evidence and locator | Scope/limit | Independent review |
| --- | --- | --- | --- | --- |
| r1 | A sealed vapor-compression loop moves cabinet heat into its surroundings | [GE sealed-system operation](https://products.geappliances.com/appliance/gea-support-search-content?contentId=16911), steps 1–7 | Generic layout; cabinet air does not enter refrigerant tubing | Pending |
| r2 | Heat enters colder fluid through the evaporator wall; liquid evaporation takes in energy | [Danfoss basics](https://assets.danfoss.com/documents/latest/49699/AX000086437108en-000202.pdf), §§2.5–2.6 and §3.1 | Illustrative phase regions, not bubble kinetics; real evaporators can include vapor warming | Pending |
| r3 | Compressor work raises vapor pressure/temperature so hotter vapor can reject heat and condense | GE steps 1–3 | Reciprocating cutaway is one example; valve timing is qualitative, no pressure/performance simulation | Pending |
| r4 | Released heat equals removed heat plus supplied work | [OpenStax §15.5](https://openstax.org/books/college-physics-2e/pages/15-5-applications-of-thermodynamics-heat-pumps-and-refrigerators), opening Qh = Qc + W | Steady cycle; 3+1=4 units are illustrative, not measured performance | Pending |
| r5 | When both sides exchange heat with one room, the net added energy is work | Inference from r4 with the same-room boundary | Local cool draft possible; altered load, transients and thermostat control omitted | Pending |
| r6 | The capillary restricts flow between high/low sides; some liquid flashes as pressure falls | Danfoss §§3.5–3.6; GE steps 5–6 for the refrigerator capillary | Enlarged proportions, no real state calculation or heat input assigned to the restriction | Pending |
| r7 | Boiling depends on fluid/pressure; cold liquid can boil, while nonboiling liquid or vapor may still warm | Danfoss §§2.5–2.8 and §3.1 | Chosen temperature is at the lower-pressure boiling point and below the higher-pressure one; no transient/real readings | Pending |

These lowercase IDs match the R2 native artifact claim references. The R1 record
above retains its historical claim numbering.

### Causal storyboard and static equivalence

| Cue | Focus / prerequisite | Input → change → output and visible evidence | Claims / static alternative |
| --- | --- | --- | --- |
| 0–10 | Whole cabinet | Food/cabinet heat enters the cold coil; work enters motor; heat leaves warm coil. Sealed loop and permanent labels establish identity. | r1,r4; same labeled still |
| 10–22 | Cold-coil wall | Warmer cabinet air → heat through metal wall → energy in colder refrigerant. Own passage, ports and surroundings remain visible. | r2; labeled passage still |
| 22–34 | Liquid/vapor region | Liquid plus incoming heat → evaporation → vapor carries energy away. Phase marks are illustrative. | r2,r7; labeled liquid/vapor still |
| 34–49 | Compressor section | Vapor plus work → crank/rod/piston reduces chamber volume → higher-pressure/hotter vapor leaves. Valves never open together. | r3; intake/compression/discharge stills |
| 49–63 | Warm-coil wall | Hotter vapor → heat crosses metal into kitchen → refrigerant condenses. | r3,r4; heat-out/liquid-out still |
| 63–77 | Fixed capillary | High-side liquid → narrow fixed restriction → low-side mixture. | r6; own supported passage and two sides |
| 77–92 | Whole loop | Same components and directions reconnect; attention does not switch other parts off. | r1,r4; complete loop still |
| 92–104 | Cabinet and room | Insulation slows heat returning; warm side rejects removed heat plus work. | r1,r4; whole-system static explanation |

One meaningful comparison is retained: compressor running/stopped. Stopped fixes
the motor/crank/piston and illustrative valves, and shows that sustained pumping
stops; passive heat exchange immediately after stopping is explicitly omitted.
Optional depth remains the existing honest boundary and pressure comparisons,
not extra core detail or arbitrary AI generation.

### Assessment and transfer rubric

Before reveal ask the open-door prediction and a brief reason; skipping is allowed.
Teach-back: “Where does the food's heat go, and what does electricity contribute?”
Score 2 requires heat entering the colder coil, circulation driven by work and
heat rejection to the room; score 1 names parts/directions but misses work or a
necessary relationship; score 0 has heat disappear or cold be manufactured.
Changed situation: put the warm coil outside the kitchen while the cold side
receives kitchen heat. Score 2 explains cooling is possible in principle because
rejected heat and work cross out of the room boundary; score 1 guesses yes without
that cause; score 0 claims every heat pump necessarily warms its cooled space.
Use the R1 branch rubric for the vapor-only region. Five initially unfamiliar
learners, 4/5 score 2 on both tasks; retention remains unmeasured.

### Implementation and separate gates

R2 uses the shared `Lesson`/`Scene`/D1 player and versioned learning path. New
trusted modules live under `experiments/refrigerator-study/r2/`; R1 domain and
narration plans are imported where semantics are unchanged. The hosted bridge
must bind exact source, scene and artifact hashes using its new native contract;
this worksheet alone does not publish anything. Current automatic quality checks
must apply through that contract, without fake CE `Part`/`Change` geometry.

| Gate | CE IDs | Planned evidence | Current result |
| --- | --- | --- | --- |
| Engineering | 08/14/16–18 | Pure state invariants, trusted exports, deterministic frames, keyboard/sound-off/reduced-motion, old hashes unchanged | Pending |
| Technical | 04/07/09–12 | Named independent reviewer checks source claims, flow directions, valve timing and energy boundary | Pending |
| Craft/accessibility | 05/14/18 | Three bounded rendered reviews at 375/768/1440; real phone and screen reader separately | Root's browser review pending; actual device pending |
| Beginner learning | 01–03/06/13/15 | Five baseline-qualified learners scored with the rubric before answers | Unmeasured |
| Release | 15/16 | Owner decision tied to exact new graph/artifacts after other gates | Not approved |

Observed results and unresolved findings will be appended to the
[R2 journal](../../journal/2026-10-22-refrigerator.md). No learner text is collected
by this local build; answers stay ephemeral, and screenshots/artifacts stay ignored.

### R2 implementation evidence · 2026-10-22

The local native candidate now exists at
`experiments/refrigerator-study/r2/index.ts`. It exports the three actual
shared-player lessons, data-only v3 semantic definitions and the same depth path
with new revision IDs. It imports the unchanged R1 pure model and cue plans;
none of the R1 renderers, entry globals, generated response code or private
artwork files are loaded by this factory.

CE-04/05/07/11: the actual Anatomy solid/tube kit supplies a layered cabinet,
supported sealed loop, real inlet/outlet connections, electrical terminal/cable,
sectioned coil passages and an independently situated motor/crank/rod/piston
assembly. Persistent labels include all six core identities. Thin chevrons mean
material direction; broad arrows mean heat/work. The nearby wall is sectioned
to expose the actual cold coil instead of painting its tubing over an opaque
wall. The whole view reconnects the jobs that run together.

CE-08/09/10/18: chamber size, fixed rod and valves use existing model state;
the stopped comparison freezes pumping and explicitly omits residual heat
exchange. Phase marks identify fluid state, not particle inventories or bubble
kinetics. Energy/pressure branches retain their declared model and limits.
The new native contract carries actual cue IDs, claims, sources, input/output,
controls and assessments without fabricating CE `Part` geometry. Actual toolkit
paint values are flattened into explicit SVG styles so raster output and the
interactive scene use the same palette.

CE-12/14–18: 12 focused tests pass, including 54 default cue checkpoints and
36 cue stills covering every authored control choice through the Python SVG
materializer. Those checks verify each focus label in every case, a whole view
with every core label for each control choice, and a real geometric/transform
change in each causal cue. They also check route joins, unchanged rod rules,
actual scenario differences, cue identity, optional matching narration and
the historical R1 packed hash. Isolated strict TypeScript with `checkJs` passes.
The separate local build can verify/reuse all three existing matching computer
speech assets; it makes no model call or speech synthesis.

Observed in agent raster review: an opaque near wall initially hid the cold
coil; compressor title/status initially overlapped the housing; SVG text using
system fonts disappeared in the exporter's bundled-font mode; and the energy
view changed its reservoir label between valid cases. These failures were
repaired before the final source freeze. Updated physical fit reserves space
for title/status, a moving leader follows the piston, and the reservoir has a
stable “Cold side” label in both cases. Root owns the full application/browser
review and artifact-bound publication bridge.

These are engineering and agent-rendered observations. A complete Anatomy kit
collision/support/occlusion audit, independent technical sign-off, actual-device
accessibility, five-learner transfer results and owner release remain missing.
The R2 hypothesis is untested. The artwork is a held candidate, not proof that
the other library topics meet this craft bar.
