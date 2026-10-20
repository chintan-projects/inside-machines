# GPU concept iteration worksheet

Status: production catalog lesson planned; local standalone GPU-S1 implemented
for review on 2026-10-19. The original planning iteration below is retained as
history; see the new local-study record at the end. No narrated catalog release
or controlled provider evaluation is claimed.
Follow ADRs 0001/0003 and CE-01–18. Candidate generic topic ID: `gpu`.

## Identity, hypothesis and scope

Person: a curious adult asking why a GPU can help with some work. Outcome: explain
independent work versus a dependency chain and predict whether adding execution
lanes can help. Hypothesis: after comparing equal independent jobs with jobs that
depend on previous results, at least four of five initially unfamiliar learners
can explain the difference and solve an unshown dependency example without hints.

The existing appliance author prompt forces cutaways and fluid paths. This is an
observed code-level mismatch; beginner learning remains unmeasured. This iteration
prepares architecture and a future lesson, not a speed benchmark or vendor-specific
performance model. Exclude full shader pipelines, silicon fabrication and hardware
purchasing advice. Memory availability is a qualitative limit, not an exact timing
formula. GPU cooling or a specific model needs different scope/evidence.

## Teaching anchors and claim ledger

- Grant: keep task identities visible as independent jobs occupy several lanes;
  compare with a chain in which the next job needs the previous result.
- Feynman: establish “can these jobs proceed without each other's answers?” before
  naming threads, execution groups or parallelism.
- Veritasium: predict whether twice as many lanes must make every job twice as fast.
- Anatomy: connect the logical model to sourced chip/memory hardware when useful;
  do not invent a physical conveyor as literal GPU internals.

| Claim | Evidence and locator | Scope / limitation | Technical review |
| --- | --- | --- | --- |
| GPU work can involve many concurrently executing threads | [CUDA Programming Model](https://docs.nvidia.com/cuda/archive/13.1.1/cuda-programming-guide/01-introduction/programming-model.html), §1.2.1 | NVIDIA programming model; not every thread starts simultaneously | pending |
| Work grouping and available execution resources matter | Same source, §1.2.2.1 | CUDA-specific blocks/SMs; illustrative lane counts are not a die layout | pending |
| Memory organization and data availability affect execution | Same source, §1.2.3 | Qualitative limitation; no invented latency or throughput | pending |
| Added resources alone cannot remove a data dependency | Inference from the declared toy dependency graph | Graph prerequisite rule, not a measured GPU speed claim | pending |

## Storyboard and representation plan

| Beat | Prerequisite / labeled focus | Input → change → output | Static equivalent |
| --- | --- | --- | --- |
| Work items | Familiar independent arithmetic jobs / work queue | Several independent jobs → assign to available lanes → multiple results progress | Before/after task locations with stable task IDs |
| Dependencies | Prior beat / result dependency | Linked jobs → wait for the required earlier result → next job can proceed | Explicit completed prerequisites and waiting successor |
| Put it together | Both beats / execution and memory | Available work/data → constrained execution → results, with waiting where needed | Whole dependency graph, completed jobs and stated limits |

Motion means illustrative task progress, not clock cycles or physical travel.
Arrows mean data dependencies. The same qualitative state must drive labels,
narration, captions, static views and video. Baseline/counterfactual compares
independent versus chained work or data available versus unavailable. Reset restores
the same graph; no arbitrary speed multiplier or invented benchmark readout.

## Transfer and rubric before implementation

Initial misconception: more GPU lanes guarantee proportional speedup.
Transfer: each step of a new calculation needs the answer from the previous step;
what can adding lanes alone change? Required reasoning: identify the prerequisite
chain, explain why blocked work cannot proceed, and avoid concluding GPUs are
universally faster or slower. Score 0: retains guaranteed speedup; 1: predicts
limited benefit without the cause; 2: explains the dependency constraint and states
that other workload/memory conditions can also matter. Optional next-day variant:
independent jobs whose input data is not yet available.

## Build, review and evidence

Use existing declarative CE-1 parts/poses/claims/assessments and the GPU guide. No
new public schema, media implementation or provider is needed for this qualitative
scope. A measured scheduler/throughput model would need a separately reviewed
computed contract. Preserve all old revisions/private histories.

Before release: author one actual lesson; compare supported states across outputs;
inspect desktop/tablet/actual phone, label focus/enlarge, keyboard, reduced motion,
sound-off and offline/reconnect. Perform the three bounded craft review rounds.
Technical, actual-phone craft, five-beginner learning and owner release gates are
all pending. Written reasoning remains optional/ephemeral; only explicitly
consented anonymous scores may enter the existing review workbench.

CE-01–03/12/13: planning evidence only. CE-04–11/14/18: reusable contracts available,
new GPU artifact/runtime evidence missing. CE-15–17: existing privacy/review/budget
controls reused; no new human pass or paid evaluation. Current Vercel migration
hold remains. Next consequential test: does a real GPU scene show dependencies
clearly without making its illustrative lanes look like measured hardware?

## Local GPU-S1: a second crafted concept

The owner chose GPU after positive craft feedback on the local vacuum trial.
[The study brief](../../experiments/gpu-study/BRIEF.md) fills the new worksheet,
claim ledger, falsifiable hypothesis and transfer rubric. The pure toy scheduler
has eight equal add-one jobs with independent or chained inputs, one/four lanes,
and an input hold. Arithmetic/readiness/rounds are computed; there are no invented
GPU core counts, clocks or benchmark claims. Nine gray levels illustrate toy
brightness, not calibrated luminance. Sources were checked in the current NVIDIA
programming guide §§1.2.1–1.2.3; its CUDA scope remains explicit.

The shared local studio owns playback/seek/reset, controls, anchored HTML labels,
optional assessments, source disclosure, responsive viewports and restricted
single-HTML packaging. GPU owns its rules, storyboard and reviewed drawing adapter.
Claude Sonnet authored base board/logical art; Codex authored the scheduler/player,
teaching data and disclosed art repairs. This is one reviewed local code-authoring
spike, not executable model output accepted by the production lesson runtime.
The earlier vacuum HTML is unchanged and has not been ported into this new shell.

CE-01–13/15–17 have planning/domain/browser evidence for GPU-S1. CE-14 has desktop
viewport, keyboard, reduced-motion and loaded-offline evidence, not real-device
or VoiceOver acceptance. CE-18 remains incomplete: there is no narrated MP4 for
this trial. No `backend.quality`/publication result is claimed for a non-LessonSpec
artifact. Engineering tests, source inspection and craft feedback do not certify
GPU hardware accuracy or learning. Exact results and limitations live in the
[journal](../../journal/2026-10-19-gpu-study.md).

## Local GPU-S2: missing sound correction

Owner reported missing audio. GPU-S1 was silent; the omission was in the artifact,
not a diagnosed device problem. The brief adds a bounded CE-08/11/14/18 iteration
before writing the script. One eight-cue plan now drives embedded local computer
speech, captions and reviewed reduced-motion stills. The media clock drives the
tour; changing any experiment stops the voice before its fixed script can disagree
with the scenario. Watch/listen, pause/resume, seek, replay, reset and mute are
explicit. Browser playback, loaded-offline use, failure UI and interruption are
observed; audio content is non-silent and hash-bound. Actual phone/speaker and
beginner learning checks remain pending. This supplies narrated HTML, not MP4
parity or production publication. Preserve GPU-S1's silent artifact and evidence.
