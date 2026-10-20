# AC benchmark: make the heat-transfer mechanism understandable

Spec version: 1.0, 2026-10-19. Iteration: CE-1 causal revision implemented; human acceptance pending.
Status: build specification; not implemented or approved.
Authority: [ADR 0001](../../docs/architecture-decisions/0001-concept-explanation.md)
and [concept explanation spec](../../docs/CONCEPT-EXPLANATION-SPEC.md).

## Goal and baseline

Person: an adult asking how an everyday AC works, without refrigeration vocabulary.
Question: **Why does an air conditioner need an outdoor unit?**

Outcome: explain how heat leaves a cooler room for warmer outdoors, why electricity
is needed, and why putting the complete unit inside a sealed room warms it overall.
Scope: generic split vapor-compression system in cooling mode. No exact appliance,
installation, refrigerant-specific values, diagnosis or repair claims.

Current lesson `air-conditioner-craft` is an immutable authored revision. The live
studio adds its own geometry/story, core labels and an enclosure experiment while
using the earlier MP4's audio. Compression and phase change are mostly described
in text. Current question feedback tests recognition. No beginner-learning result
or independent technical sign-off is recorded. See [the teardown](../visual-learning-teardown.md).

Hypothesis: seeing heat pickup, electrical work and heat rejection in a connected
model will let a beginner explain the outdoor unit and correctly predict the
sealed-room refrigerator case. A nicer cutaway alone would not test this hypothesis.

## Teaching choices

| Anchor | Application |
| --- | --- |
| Grant | Start with the two-units-in-one-room puzzle; motivate each new mechanism with the obstacle it solves. |
| Feynman | Bridge from heat moving between warmer/cooler objects to “make the refrigerant hotter so it can give heat to outdoors.” Introduce refrigerant, evaporator and condenser after their roles. |
| Veritasium | Ask for a cooler/warmer/unchanged prediction and optional reason before the result; revisit the same prediction after recombination. |
| Anatomy | Keep recognizable connected indoor/outdoor hardware; reveal a schematic internal process where the casing conceals the explanation. Labels remain anchored at phone size. |

The prerequisite chain is temperature difference → heat transfer → heat pickup by
boiling → electrical work/compression → outdoor condensation → pressure reduction
preparing the next pass → whole-system energy accounting. Exact pressure/temperature
values and the thermodynamic cycle plot are optional later depth.

## Mechanism and claim ledger

Core identities remain `evaporator`, `compressor`, `condenser`, `expansion` for
compatibility. Add stable semantic IDs for air streams, transfers and teaching beats
only through the versioned contract. Refrigerant stays in a sealed loop; room and
outdoor air are distinct streams. Actual processes run together during steady cooling.

| ID | Claim and locator | Assumptions / review status |
| --- | --- | --- |
| AC-C1 | A refrigerator/AC transfers heat from the cold region to the hot region using work. [OpenStax 4.3, Refrigerators](https://openstax.org/books/university-physics-volume-2/pages/4-3-refrigerators-and-heat-pumps) | Generic cycle; independent technical review pending. |
| AC-C2 | The four main roles are evaporation, compression, condensation and expansion. [Carrier, How do air conditioners work?, step-by-step cycle](https://www.carrier.com/residential/en/ca/products/air-conditioners/how-do-air-conditioners-work/) | Generic split system, schematic layout; review pending. |
| AC-C3 | At steady operation, heat rejected equals heat removed plus supplied work. [OpenStax 4.3, energy-flow diagram/equation](https://openstax.org/books/university-physics-volume-2/pages/4-3-refrigerators-and-heat-pumps) | Consistent boundary and negligible storage; include total electrical input or explicitly disclose omitted auxiliaries. Review pending. |
| AC-C4 | With both sides inside the same insulated room, the complete machine adds net heat equal to its electrical input. Inference from [OpenStax 4.3, Figure 4.6 and energy conservation following Eq. 4.3](https://openstax.org/books/university-physics-volume-2/pages/4-3-refrigerators-and-heat-pumps) | Our application of the energy balance to a common boundary; the page does not explicitly discuss the open-door case. Steady/over-time accounting, no heat exchange through the room boundary. Does not predict a temperature or rate. Review pending. |

Verify source support and add precise claim locators for pressure/phase changes
before implementing their insets. These references begin the ledger; they are not
technical sign-off. In particular, valve expansion is not piston expansion; never
use the compression inset in reverse as an explanation of the throttling valve.

## Planned storyboard

These are semantic beats, not a mandate to mutate current six stored stage indices.
Define their mapping to narration/media checkpoints when versioning the package.

| Beat | Labeled focus and prerequisite | Input → change → output / visible reason | Copy direction and evidence |
| --- | --- | --- | --- |
| AC-B1: predict and orient | Whole machine and room boundary; familiar heat flow | Offer cooler/warmer/unchanged/Show me before result. Show a familiar warmer object giving heat to a cooler one as an explicitly explanatory inset. Establish two air streams and one sealed refrigerant loop. | “Could this cool a sealed room with both units inside?” AC-C1/C4. Keep the final result concealed. |
| AC-B2: pick up heat | Indoor coil; warmer-to-cooler transfer | Room air gives heat to colder refrigerant through the coil. Show heat crossing the pipe wall, air remaining outside, refrigerant boiling inside. Output: cooler room air and low-pressure vapor. | “The same room air comes back cooler. Its heat enters the fluid in the pipes.” AC-C2, phase evidence to be completed. |
| AC-B3: overcome the obstacle | Compressor; heat must pass to warmer outdoors | Electrical work acts on vapor; a labeled schematic compression inset shows the physical change and higher pressure/temperature. Output vapor is hotter than outdoor air. Do not imply a documented compressor type or show only a glowing shell. | “To release heat outside, first make the fluid hotter than outside.” AC-C1/C2 plus reviewed compression evidence. |
| AC-B4: release heat | Outdoor coil; hotter fluid than surrounding air | Show heat crossing out of the sealed pipe into outdoor air, and vapor condensing. Keep room heat and added work identifiable as contributions to total rejected heat. Output: high-pressure liquid. | “Here the room's heat leaves, along with the energy supplied to run the machine.” AC-C2/C3. |
| AC-B5: prepare the next pass | Expansion device; the loop must return cold | A restriction produces pressure reduction and a cold liquid/vapor mixture in this refrigeration regime. Show a correctly reviewed phase change, with no piston or imaginary heat extraction at the valve. | “The pressure drops. Some liquid becomes gas, preparing the mixture to absorb room heat again.” Additional phase/throttling evidence required. |
| AC-B6: reunite and transfer | Whole running loop; all earlier relationships | Show all four processes together. Reveal the predicted enclosure outcome on request; switch the room boundary with the same machine and show where both heat transfers land. Offer new-situation task before its answer. | “Heat released = heat removed + electrical work.” AC-C3/C4. The continuous loop is not a four-phase on/off sequence. |

Every beat also needs a static input/change/output diagram and equivalent text.
One primary action owns attention. Retain recognizable full-machine context when
focusing an inset, and provide an explicit way back to the whole.

## Interaction and visual rules

- Opening prediction: optional choice/reason; skip reveals the same explanation.
  No grading, AI request or stored answer is necessary to advance.
- Enclosure experiment: outside versus both inside; qualitative reviewed scenarios,
  not a numerical temperature simulation. Reset restores the declared initial state.
- Keep refrigerant travel, air movement, heat transfer and electrical work separately
  traceable with labels and distinct direction/shape cues. Moving refrigerant markers
  do not imply that heat is conserved as a material particle.
- Pressure, phase and temperature are different properties. Qualitative low/high
  and liquid/vapor labels are enough for this iteration; do not invent gauges or
  show a linear temperature response to arbitrary animation speed.
- Compression/expansion insets demonstrate reviewed principles. Mark schematic
  internals explicitly; do not imply the illustrated device is the user's machine.
- At the whole-system checkpoint, account for all transferred heat and input work
  at the same boundary. Declare steady operation, omitted heat leaks and auxiliaries.

## Learning tasks and rubric

Baseline: “If both units run in a sealed, insulated room, does the room become
cooler, warmer, or stay the same? Why?” Capture optional initial reasoning privately.

Teach-back: “How can this machine move heat from a cooler room to warmer outdoors?”
Score 2 requires heat pickup indoors, electrical work making heat rejection possible,
and heat release outdoors. Merely naming four parts scores at most 1. Score 0 if
the explanation manufactures cold or sends the room's air outdoors through the pipes.

Transfer: “Leave an electric refrigerator's door open in a sealed, insulated room.
Over time, does it cool the room? Explain.” Score 2 requires that heat taken from
the room returns to that room plus electrical input, so the room warms overall.
Correct “warmer” without that reason scores 1; net cooling or disappearance of heat
scores 0. Both scores use the spec's 0/1/2 scale and do not require jargon.

Optional next-day variant: ask where the added energy goes when a standalone freezer
with its lid open runs in that room. Do not claim retention until it is tested.
Use five beginners initially lacking the target model, the spec's four-of-five gate,
and report baseline and missing observations. This is formative, not a comparison
proving superiority over other explanations.

## Implementation order and acceptance

| Requirement group | Planned evidence |
| --- | --- |
| CE-01–03, CE-06 | Primary question, prediction and prerequisite bridge in AC-B1; roles before jargon |
| CE-04–05, CE-07 | Labeled causal changes in AC-B2–B5, distinct heat/air/fluid/work cues, static equivalents |
| CE-08–10 | Shared scenario rules, allowed inputs/reset and invariant tests; no numerical simulation claim |
| CE-11, CE-13 | Simultaneous whole-system AC-B6, teach-back and refrigerator transfer rubric |
| CE-12, CE-15 | Completed source ledger and separate technical, craft, learner and owner review results |
| CE-14, CE-16–18 | Accessible/offline checks, immutable version migration, budget/privacy checks and shared-media checkpoint review |

1. Complete the claim ledger and technical treatment of compression/phase change.
2. Plan compatible teaching/action/state contracts and media checkpoints. Preserve
   the old revision, stage meaning, member progress and private chats.
3. Build the question-to-transfer path in the existing modular AC studio. Share
   scenario rules; do not introduce provider or physics rules inside UI components.
4. Align narration, captions, video and static output to the new storyboard. A new
   live visual with the old MP4 is still an explicitly incomplete parity gate.
5. Test meaningful state changes/reset/seeking, source boundaries, reduced-motion,
   keyboard, sound-off, offline/reconnect and actual phone readability.
6. Run technical, craft and beginner reviews independently, record the highest-impact
   failure, and iterate before widening the catalog or promoting draft generation.

No additional paid authoring/evaluation is dispatched by this document. Future calls
use the existing gateway, explicit task routes, bounded reservations and $50 total
app-AI ceiling. Playback and authored assessments do not need a model call.

| Gate | Current result |
| --- | --- |
| ADR/spec and acceptance tasks | Implemented; traced in docs/CONCEPT-IMPLEMENTATION.md |
| New causal scenes and shared artifact parity | Shared SVG/pose/storyboard implementation and new media; human semantic parity review pending |
| Engineering tests for new behavior | 107 backend tests, cross-language path sampling and real MP4 revision regression pass |
| Independent technical review | Pending; Danfoss printed pp.20/22 now support throttling and phase-change treatment |
| Real-phone owner craft/accessibility decision | Pending |
| Beginner teach-back and transfer | Unmeasured |
| Family release | Held; this plan does not approve it |


## CE-1 build evidence

`air-conditioner-ce-1` implements AC-B1–6 with a new immutable identity and media.
Grant's visual reasoning motivates the shrinking compression chamber and spatial
energy paths; Feynman's causal simplicity motivates heat-contact before refrigerant
terms; Veritasium's approach motivates the sealed-room prediction and open-fridge
transfer; Anatomy motivates the original physically connected cutaway. Labels and
motion follow the ADR's explicit project overrides. These are design choices, not
creator endorsement or evidence that learners understand them.

The claim ledger is now also executable data in `backend/ac_concept.py`. Source
inspection corrected an initially guessed Danfoss locator to printed p.20, sections
3.5–3.6, and p.22 cycle diagram. The valve inset is a restriction with a liquid/vapor
mixture downstream, not a reversed piston. Compression and heat rejection remain
distinct. A renderer fingerprint prevents later SVG changes silently reinterpreting
a saved revision. Independent technical, actual-phone and learning gates stay open.
