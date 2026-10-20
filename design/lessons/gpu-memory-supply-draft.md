# GPU memory supply · scoped follow-up production trial

## Identity and goal

- Generic qualitative insight attached to `gpu-studio-1`; no measured device claim.
- Iteration GPU-MEM-S1, CE-1/v2, planned for review. Root artifacts stay immutable.
- Learner: curious beginner who followed the core's input → calculation → stored result.
- Question: why can additional execution capacity remain unused while inputs are missing?
- Observable outcome: explain a waiting dependency and predict a changed input-supply situation.
- Hypothesis: four of five initially unfamiliar learners score2 on causal reasoning
  and transfer before hints after this experience. This is unmeasured.
- Gap: the complete core establishes data-parallel work but not this limiting relationship.
- Scope: a logical dependency diagram, not chip layout, instruction timing, a profiler,
  GPU purchasing guidance or an explanation of every performance bottleneck.
- CE-01–09,11–18 apply. CE-10 permits a qualitative model without invented measurements.

## Teaching anchors

| Anchor | Choice |
| --- | --- |
| Grant | Keep one task and its input visible; animate a dependency becoming satisfied. |
| Feynman | Explain the job before terminology; distinguish waiting time from transfer capacity. |
| Veritasium | Predict whether extra lanes alone guarantee more finished work, then inspect why. |
| Anatomy | Use coherent labeled logical components and connections; do not invent a physical cutaway. |

## Mechanism and claim ledger

Use labeled input store, input path, waiting/ready work and execution lanes. Results
return to a labeled output store. Motion means data dependency/transfer, not a clock
or a benchmark. Core input/calculation/result identities remain recognizable.

| Claim | Evidence and location | Scope / review |
| --- | --- | --- |
| GMS-01: An operation needs its required operands before it can execute. | Dependency reasoning; [NVIDIA CUDA13.0 guide §11.2](https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-best-practices-guide/index.html#hiding-register-dependencies). | General inference from dependency examples; independent review pending. |
| GMS-02: Other ready work can use resources while dependent work waits. | Same guide §11.2, active-thread discussion. | CUDA example; no universal scheduling guarantee. |
| GMS-03: Reading inputs and storing results both create memory traffic. | [Same guide §9.2.2](https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-best-practices-guide/index.html#effective-bandwidth-calculation). | No workload-specific bandwidth or timing claim. |

Source sections were opened during planning. The research checkpoint also records
scope limits; neither retrieved text nor automated review is technical certification.
Latency and bandwidth must stay distinct. Caches and other ready work prevent the
false claim that every off-chip wait leaves an entire GPU idle. No percentages,
cycles, throughput or speedup readouts are authorized by this qualitative trial.

## Prediction and causal storyboard

Prediction before reveal: does adding execution capacity always finish this same
input-dependent task sooner? Let the learner skip without guessing.

| Beat | Focus | Visible input → action → output | Static equivalent |
| --- | --- | --- | --- |
| ready-input | Input path and task | Labeled input reaches its dependent operation; the operation becomes ready. | The same identities connected by labeled dependency arrows. |
| waiting-task | Waiting operation | Withhold its input; preserve the unsatisfied dependency rather than invent a slower clock. | Explicit waiting label and missing-input explanation. |
| reconnect | Available work and output | Compare independent ready work, then reconnect the result to the core's output. | Whole dependency map with simultaneous work distinguished from attention order. |

Each working view must have its own labeled surroundings and components, input,
output, causal change and source-linked claim. The full-system locator is separate.
The table is a proposed storyboard, not evidence that generated art implements it.

| Interaction | Allowed state | Required consequence | Limit |
| --- | --- | --- | --- |
| Input availability | Available / withheld; reset to available | Scene and explanation agree about readiness. | Qualitative counterfactual, not measured rate. |
| Ready independent work | Only if supported by the authored scope | Compare a separate ready task without erasing the original dependency. | Never imply all latency can always be hidden. |

## Assessment before disclosure

- Teach-back: point to what the waiting operation needs and explain the cause.
- Transfer: would adding more dependent work itself supply the missing input?
- Score0: names parts or repeats “GPUs are fast.” Score1: identifies waiting but
  cannot connect the changed condition. Score2: traces the dependency and predicts
  the new situation with a correct reason and an honest scope limit.
- Gate: five initially unfamiliar learners, at least four scoring2 on both tasks.
  Baselines, responses and next-day retention are not measured yet.

## Build, verification and release

Use the shared owner depth endpoint, frozen parent context, research checkpoint,
Claude authoring, original domain/quality validation, SHA-bound editorial verdict,
OpenAI speech, trusted renderer and shared D1 player. Complete core first; attach
only an actual compatible leaf. Never use this plan to fabricate a successful job.

The owner authorized a$50 app ceiling; each explicit job reserves$2. Failed work
and unknown billing stay recorded. This trial does not permit automatic paid retry.
Private operator artifacts and any learner responses remain ignored and anonymized.
Check seek/scenario/caption/narration/static parity, labels at375/768/1440, keyboard,
reduced motion, offline hash verification and return context for the exact revision.

| Gate | Method and CE trace | Current result |
| --- | --- | --- |
| Engineering | API/provider/budget/path/media checks; CE-08,14–18 | Shared regressions pass; full generated artifact pending. |
| Technical | Independent claim/scope/invariant review; CE-03,06,10–12 | Pending. |
| Craft/accessibility | Real-phone readability and owner walkthrough; CE-04,05,07,14,18 | Pending. |
| Beginner learning | Predefined teach-back/transfer rubric; CE-01,02,09,13,15 | Pending; no invented scores. |
| Release | Owner approval for exact spec/video/bundle hashes; CE-15,16 | Held. |

The first nested-schema attempt failed at provider admission. The next complete
stream hit its10k output limit. Neither yielded a publishable artifact. The new
20k bound preserves the same phase reservation and teaching requirements. Results,
actual artifact identities and observed versus inferred findings belong in
[journal](../../journal/2026-10-20-curated-integration.md); this plan is not acceptance.
