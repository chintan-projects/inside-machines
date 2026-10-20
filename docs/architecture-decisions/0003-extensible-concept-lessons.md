# ADR 0003: Reuse the teaching engine across physical and computational concepts

Date: 2026-10-19. Status: Accepted architecture direction from the owner's request
to extend explanations to GPUs, LLMs and other concepts. New lessons remain subject
to the separate quality gates; this decision approves no content or deployment.
Extends ADR 0001's physical-object emphasis while retaining its teaching contract.

## Problem and decision

The learner wants to picture a causal relationship and predict a changed situation.
That job applies to a washing machine, a GPU and language-model generation. The
current shared state/scene contract can represent all three, but appliance-only
authoring instructions require a machine cutaway, fluid markers and mechanical
solids. Those instructions would make an abstract explanation misleading.

Keep one versioned lesson package and one teaching engine. Separate the following:

| Shared across concepts | Specific to a concept |
| --- | --- |
| Question, prediction, prerequisite beats, source claims, transfer rubric | Learner question, misconception, dependencies and evidence |
| Safe labeled shapes, poses, seeking/reset, static alternatives | Physical cutaway, execution lanes, token tiles or another truthful representation |
| Narration, captions, video, offline playback and private chat | Meaning of each encoding and supported physical/computational rules |
| Provider/task routes, budget ledger, checkpoints and immutable publication | Domain-specific authoring/review constraints and future trusted computed adapters |
| Artifact-bound technical/craft/learning/release gates | Independent reviewers and learner results for that exact concept/revision |

`backend.concept_guides` is a small immutable registry of trusted, versioned data:
general concept, physical mechanism, GPU computing and language model. Guidance is
selected by the server, recorded on new jobs and used by research, authoring,
revision and review. Unknown stored versions fail before paid work. It is not a
plugin loader or a new model gateway. Client text cannot provide code, credentials,
provider routes or custom renderer IDs. Guidance respects the requested subtopic;
it does not impose a fixed lesson sequence. Ambiguous mixed requests use the
general evidence-led guide. GPU cooling uses physical guidance, rather than being
forced into parallel-computing lanes.

All guide data participates in author-checkpoint policy identity, so an instruction
change cannot silently recover a paid draft written under an older teaching policy.
Research keeps its own evidence checkpoint. No paid generation was run for this
extension; model/visual quality for GPU and LLM remains unmeasured.

## Representation and truth

Anatomy's connected physical craft remains relevant when depicting hardware.
Information diagrams instead need explicit operands, dependency direction and
visible transformations. A token tile is a representation; it is not a physical
packet of fluid, a neuron, or a view of a model's private reasoning. Purposeful
detail must earn its place. Do not add fake components to meet part counts.

Grant's visual reasoning means showing which work can proceed together, or how
context changes a representation. Feynman's simplicity means establishing the job
before naming a warp, embedding or attention mechanism. Veritasium's contribution
is a prediction that exposes a misconception and a changed-situation transfer.
None of these names certifies teaching quality.

Current CE-1 supports bounded qualitative scenes. It does not execute arbitrary
models, GPU benchmarks, attention calculations or real model weights. A future
computed extension needs a trusted pure domain module, validated inputs, units or
explicit mathematical interpretation, invariants and shared output state. Introduce
new action/renderer semantics through an explicit version; do not reinterpret an
existing pose or claim an illustrative animation is a numerical simulation.
The current authoring envelope is 3–7 beats and at least eight purposeful context
parts including labels. Do not add filler for a concept outside that envelope;
use an explicit future contract extension when the concept requires another form.

## Compatibility and adding a concept

The public LessonSpec v1/v2, API version and stored hashes are unchanged. `parts`
can represent physical or logical working components; `graphics` illustrate their
operations. New job guide metadata does not rewrite published artifacts. GPU/GPU
plural/full-name and LLM/plural/full-name aliases normalize together, while memory,
training, inference, vendor and model qualifiers remain distinct cache identities.

To add a domain: fill the worksheet and claim ledger; declare the representation,
meaning of motion and one falsifiable learning hypothesis; add a trusted guide only
where the general guide is insufficient; add fixed evaluation cases and boundary
tests; build one complete lesson with shared media; perform independent technical,
real-device craft and beginner transfer reviews. Do not copy the player, pipeline,
provider, state, logging or budget services into domain folders.

The [GPU worksheet](../../design/lessons/gpu.md) and
[LLM worksheet](../../design/lessons/llm.md) are planned acceptance cases, not
published lessons. AC/washer/vacuum success cannot approve them. Broader topic
support does not change the current Vercel ownership/deployment hold.

## Evidence and limits

The initial source grounding is NVIDIA's CUDA Programming Model §§1.2.1–1.2.3,
*Attention Is All You Need* §§3.1–3.5, and the GPT-3 paper's abstract/§2. Their exact
scope and limitations are in the worksheets. NVIDIA-specific grouping is not a
universal GPU specification; an encoder-decoder Transformer paper is not proof
that every modern LLM uses the same architecture or dimensions.

Engineering checks establish trusted routing, alias reuse without new spend,
unknown-version failure and unchanged artifact readers. They do not establish
the explanatory quality of an as-yet unauthored GPU or LLM lesson.
