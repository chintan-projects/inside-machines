# Prefill/decode r2 — lesson iteration

Status: implemented for local review; acceptance pending. CE-1 iteration 2, computational dependency family, generic ordinary causal decoder. This is a separate reference from the earlier `prefill-decode-video` experiment, with no mutation of published lessons, stored progress or private conversations.

The learner is a curious adult who has watched AI text stream but cannot trace a request. The question is why known prompt positions can be processed together while answer choices depend on processing the previous choice. After the lesson, the learner should trace “The sky is → blue → and”, distinguish selected from processed, and predict what cache removal changes.

Hypothesis: preserving one token/state across input, processing and selection will let an unfamiliar viewer explain the dependency and transfer it to a six-token request whose cache is disabled. This remains a hypothesis until tested with real learners. The previous 55-second voice sample did not cover the full explanation; model audience reads and narrow renders exposed confusion and layout failures.

| Teaching anchor | Concrete choice |
| --- | --- |
| Grant: purposeful visual reasoning | The selected gold token remains outside the processing grid until fed back; actual computed values and explicit dependency paths replace decorative hardware. |
| Feynman: plain mechanism and limits | One two-layer toy, hand-chosen rules, fixed two selections; optional full arithmetic. No measurements, real-model score claims, GPU core counts or creator endorsement. |
| Veritasium: prediction and transfer | Optional prediction about parallel answers; worked cache-off observation; a different six-token assessment before its answer is revealed. |
| Anatomy: truthful representation | Follow the skill's computational exception: show data, operations and dependencies, rather than inventing a physical appliance cutaway for an algorithm. |

The [brief](../../experiments/prefill-decode-r2/BRIEF.md), [claim ledger](../../experiments/prefill-decode-r2/CLAIMS.md) and [canonical story](../../experiments/prefill-decode-r2/lesson/story.js) define prerequisites, claims, assumptions, stable beats, visual cues and static narration. Information flows from known representations through attention/feed-forward layers to vocabulary scores and a selection. Known positions are parallel within the current layer; a later layer waits for the preceding layer's outputs; the next answer selection waits for the selected input to be processed.

The pure mechanism supports cache on/off and exact attention arithmetic. The optional calculator permits finite query values in [-10,10] and an explicit allow-list; an all-masked row has no valid attention output. Batching counts independent logical positions, not hardware or time. One K/V pair means one position's key and value in one layer. Invariants cover cache/recomputation equivalence, selected-versus-processed state, causal masking, invalid input and multi-dimensional value outputs. Encodings use labels/shapes as well as color; motion traces dependencies, and reduced motion retains complete states.

The interactive and ManimGL adapters share generated checkpoints, score values and canonical narration. Actual render timelines drive chapter seeking. Static transcript and captions remain available without sound. Local intent lookup opens prepared depth; unrestricted follow-up conversation remains in the host Claude/Codex session. No provider, player API, public registry or backend schema migration is introduced by this local example.

Prediction: can parallel hardware choose two dependent new answer pieces together? Choices are optional, the causal answer appears at the first selection. Teach-back asks why known prompt work differs from the answer loop. The separate transfer request has **six** prompt tokens; disabling caching before its second choice rebuilds six old positions plus one new position in both layers: fourteen pairs rather than two. The same exact computation and selection rule retain the same result. Score 2 for both recomputation and unchanged deterministic result, 1 for one, 0 for the answer-cache/GPU-sequential misconception or neither. Counts are supplementary, not the sole learning criterion.

Baseline understanding must be recorded; five learners must lack the target causal understanding initially. Proposed gate: four of five score 2 on teach-back and transfer before hints. Next-day transfer/retention is unmeasured. Optional written answers stay in memory; explicit downloads hold anonymous self-scores only. Browser QA fixtures do not count as participants.

| Gate | CE IDs | Evidence | Status |
| --- | --- | --- | --- |
| Engineering | 08–10, 14, 16–18 | 19 mechanism/content checks; browser journeys and real media checks in the reference receipt; required repository checks. | Recorded separately from learning. |
| Technical | 03–04, 07, 10–12 | Primary source ledger; independent automated scalar-equation checks. | Independent human technical review pending. |
| Craft/accessibility | 05–07, 14 | 390/768/1440 renders, keyboard/reduced-motion, explicit sound state and return from depth. | Actual phone and owner verdict pending. |
| Beginner learning | 01–04, 06, 11, 13 | Genuine fresh automated reads retain confusion; every reader stated the main takeaway. | Five unfamiliar learners pending; no human scores invented. |
| Release | 15–18 | Revision-bound local receipt, public editable source only. | No live app update or lesson activation. |

The [friction record](../../experiments/prefill-decode-r2/review/FRICTION.md) distinguishes observed corrections from inferred learning. The highest remaining risk is the transition from completed prompt processing to separate K/V intermediate state; optional arithmetic may not repair that for a first-time viewer. Human teach-back must establish whether the core gives a sufficient causal model. The owner has not made a release decision. Refrigerator reuse follows acceptance of this reference, without transferring its evidence automatically.

The [iteration journal](../../journal/2026-11-13-prefill-reference.md) records execution, plan departures, observed failures, cost scope and the outstanding human decision.
