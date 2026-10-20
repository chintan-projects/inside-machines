# GPU-S3: complete explanation, optional depth

Status: planned local iteration, 2026-10-19. Owner explicitly requests implementation.
Preserve GPU-S1/S2 and the original vacuum. This is a local study, not catalog release.

Person: a curious beginner, intended range 8–80, asking what a GPU does.
Job: trace a complete input-to-result story, then investigate the missing relationship.
Posture: concrete, calm, exploratory.
References: retain the Claude/Anatomy physical board as the hardware locator; use
Grant's stable objects and purposeful transformations to connect the logical views.
Avoid a component glossary or four interchangeable dashboard cards.

Observed gap: the owner finds both examples incomplete. GPU-S2 explains independent
jobs but leaves the program, data supply and result-to-image connection out. A
“deeper” button cannot compensate for an incomplete core answer.

Hypothesis: after core plus an optional branch, at least four of five initially
unfamiliar learners can trace instruction/input/calculation/result, and predict a
new dependency or data-supply case with a causal explanation (score 2).
Tenets: finish the causal spine before offering a detour; keep one example's
identities across views; each branch answers one question; depth is a choice, not
an age label; technical names follow their job. Preserve existing paper/ink tokens
and anchored labels. The new work is in explanation and transitions, not recoloring.

## Claim ledger and scope

| ID | Claim | Evidence / locator | Limit / review |
| --- | --- | --- | --- |
| G5 | A program launches GPU work with code and accessible input data | NVIDIA CUDA Programming Guide §1.2.1 | CUDA illustration; discrete-board example, not every memory architecture; human review pending |
| G6 | Memory availability and execution resources both matter | Same guide §§1.2.2–1.2.3 | Teaching rounds and four slots are not hardware clocks, layout or measured speed; pending |
| G7 | Each matrix output is a row/column dot product | Declared exact 2×2 arithmetic model | Mathematical result, not actual model weights; pending |
| G8 | Transformer attention/feed-forward layers use matrix operations | Attention Is All You Need §§3.2.1–3.3, equations 1/2 | Original Transformer example; not a complete GPT/LLM explanation; pending |

Sources checked 2026-10-19: https://docs.nvidia.com/cuda/cuda-programming-guide/01-introduction/programming-model.html
and https://arxiv.org/html/1706.03762v7 . Existing G1–G4 remain in the study brief.

## Storyboard and authoritative rules

Core: physical board → eight pixel values → program chooses add-one operation →
data in GPU memory → four illustrative ready calculations → results written back →
changed picture and return to the complete system. Keep A–H and 0–7 → 1–8 stable.
Eight levels are toy values, not calibrated luminance; no output clipping occurs.
Attention order is sequential; real transfers/calculations can overlap.

Insight: reuse the existing exact independent/chain scheduler and prediction.
Data branch: four available slots; deliver one or four inputs per ideal round,
compute each delivered value +1, show waiting versus working versus finished.
This explicitly simplified model delivers then computes in each round; no bandwidth
units, physical travel time, caches or real performance ratios are inferred.
Model branch: A=[[1,2],[3,4]], B=[[2,0],[1,2]], C=[[4,4],[10,8]]. Pair operands,
multiply, add, write one output; then reveal four independently computable outputs.
Change B[0][1] from 0 to 1: C becomes [[4,5],[10,11]]. Never animate a guessed result.

Grant: stable operand identities and visible transformations. Feynman: why each
step exists before naming it. Veritasium: predict what extra slots or a changed
weight can do; deliberate reveal. Anatomy: real hardware locator, explicitly logical
views for computations. Creator names are references, not acceptance criteria.

## Transfer and acceptance

Core transfer: with changed instructions, what must change before output can change?
Data transfer: eight ready slots but one input per round—what remains limiting?
Matrix transfer: changing the top-right entry of B affects which output column and
why? Score 2 identifies column 2 and row/column dependence; 1 predicts some change
without cause; 0 assumes every output changes or none does. Answers remain hidden
until requested. No learner text persists. Next-day retention remains unmeasured.

CE-01–13: complete spine, pure rules, evidence, prediction and transfer.
CE-14/18: narration/captions/stills consume each node's same timeline; shared sound
controls and offline playback. Branch switch pauses audio and returns to the saved
scene without autoplay. MP4 parity is outside this local slice and remains pending.
CE-15–17: exact revision hashes, separate gates, shared accounting, no paid calls.

Build a versioned JSON learning path, bounded validation and provider-neutral
planning prompt; a shared navigator owns selection/back/progress, and a shared
player owns playback. Domain rules/scene adapters remain topic-specific. Validate
another topic fixture to prove navigation is not GPU-coded. Do not pretend this
installs an automatic API generation or production publication route.

Run arithmetic/readiness/boundary, graph/admission, cross-language schema, navigation
and audio-interruption tests; required engineering checks; three bounded craft
rounds at 390/768/1280 widths, keyboard, reduced-motion and loaded offline checks.
No model calls are needed. Independent technical, owner actual-phone, beginner
learning and owner release decisions remain separate and pending.
