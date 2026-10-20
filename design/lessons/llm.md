# Language-model concept iteration worksheet

Status: planned lesson; shared-engine authoring support implemented locally for
review. No LLM teaching artifact, paid provider evaluation or release is claimed.
Follow ADRs 0001/0003 and CE-01–18. Candidate generic topic ID: `llm`.

## Identity, hypothesis and scope

Person: a curious adult asking how generated text emerges. Outcome: trace one
autoregressive generation step and distinguish changing context from changing
learned parameters. Hypothesis: after seeing a fixed-parameter model consume two
different contexts, at least four of five initially unfamiliar learners can explain
why candidate scores may change and why that does not demonstrate parameter updates.

The appliance-only prompt is an observed representation mismatch. This prepares a
bounded future lesson about decoder-only generation; training, retrieval, tools,
model-specific architecture and alternative model families require their own
evidence and question scope. Do not promise that all LLMs are decoder Transformers.
No actual weights, model probabilities, measured attention or private reasoning
are available in this lesson. Do not invent numerical values disguised as telemetry.

## Teaching anchors and claim ledger

- Grant: preserve token identity through representation/context changes; reconnect
  candidate scores, selection and the next generation step.
- Feynman: explain what the numbers and transformations do before naming embeddings,
  attention, feed-forward blocks or logits.
- Veritasium: predict whether a changed reply necessarily means the model's learned
  parameters changed; compare with an unseen context variation.
- Anatomy: purposeful detail and coherent connections where computation is shown;
  no invented plumbing, physical brain or decorative server cutaway.

| Claim | Evidence and locator | Scope / limitation | Technical review |
| --- | --- | --- | --- |
| Token representations are transformed using attention and feed-forward operations | [Attention Is All You Need](https://arxiv.org/html/1706.03762v7), §§3.1–3.3 | Foundational encoder-decoder example, not every LLM architecture | pending |
| Learned embeddings map tokens to vectors; output projection/softmax produces next-token probabilities | Same source, §3.4 | No real weights or numeric probabilities claimed | pending |
| Autoregressive generation conditions on earlier generated tokens | Same source, §3; decoder masking §3.1 | The overview chooses decoder-only scope; do not copy the paper's encoder path as universal | pending |
| Text context can change task behavior without gradient updates | [Language Models are Few-Shot Learners](https://arxiv.org/html/2005.14165v4), abstract and §2 | GPT-3 inference setting; not a claim that every hosted system never retrains | pending |

## Storyboard and representation plan

| Beat | Prerequisite / labeled focus | Input → change → output | Static equivalent |
| --- | --- | --- | --- |
| Pieces and representations | Familiar text / token input | Text pieces with positions → learned representation → numeric input | Token tiles and labeled illustrative vector slots |
| Use the context | Prior beat / context transformation | Available earlier context → attention and learned transformations → contextual representation | Explicit allowed connections and changed representation |
| Choose and repeat | Both beats / output selection | Contextual state → candidate scores and selection → append token, form next input | Whole generation loop with fixed-parameter scope |

Arrows mean information dependencies, never literal fluid travel. A token need not
equal a word. Any matrices/counts are clearly illustrative and qualitative. Future
computed toy attention must use actual declared math and invariant tests. The
counterfactual changes supplied context with parameters held fixed; scores may
change without guaranteeing a different selected token. Training is a distinct
process involving an objective/error signal and parameter updates.

## Transfer and rubric before implementation

Opening misconception: a different generated answer proves the model learned new
weights during the conversation. Transfer: add a new example to the prompt while
holding the model fixed; can candidate scores change, and what does that establish?
Score 0: asserts necessary weight update or guaranteed truth; 1: recognizes the
context effect without tracing it; 2: connects context to transformed state and
candidate scores, distinguishes selection from truth, and does not infer parameter
updates from a changed output. Optional next-day variant: remove the added context
and ask which claims of permanent learning remain unsupported.

## Build, review and evidence

Use the existing CE-1 declarative scene, pose clock, evidence ledger, assessments,
media and private chat. The language-model guide specializes research/authoring/
review; it is not another AI provider or a running LLM simulator. No schema field,
published ID/hash or old progress meaning changes in this architecture iteration.

Before release: build the actual lesson and render three bounded craft rounds;
check desktop/tablet/actual phone, labeled logical focus, before/after, keyboard,
sound-off, reduced motion, offline/reconnect and all media checkpoints. Obtain
independent technical review and five initially unfamiliar learner results against
the rubric; keep optional written answers ephemeral. All human gates and GPU/LLM
visual quality remain pending. No learning scores have been invented.

CE-01–03/12/13: planning evidence only. CE-04–11/14/18: shared capabilities exist,
new artifact/runtime evidence missing. CE-15–17: existing guards and private review
records reused. No paid call or deployment; Vercel migration hold remains. Next
consequential test: can the visual explain a changing contextual state without
suggesting that attention alone is the model or that the picture reveals its thoughts?
