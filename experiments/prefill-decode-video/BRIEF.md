# Prefill versus decode — preserved example brief

Question: why can a language model process a known prompt together, but usually
generate its answer one new token at a time?

Audience: a technically curious adult beginner who knows the model runs on a GPU,
without assuming linear algebra. This is an inferred starting level, not observed
audience knowledge or a promise that one pace suits every age.

Outcome: trace the prompt into the first output token and the next two decode
steps; predict what changes with a longer output. Hypothesis: making each output
become the next input will let an uncoached viewer distinguish sampled tokens from
processed tokens and explain the sequential dependency.

The toy prompt is “The sky is”, with illustrative token splitting, IDs and scores.
Use a conventional dense causal decoder-only transformer with full attention and
KV caching. Three drawn layers are schematic. No training or actual model/GPU
benchmark ran. Weights are resident in GPU memory, not copied over PCIe per token.

The core causal spine is known prompt → causally masked processing through layers
→ last-position scores → first sampled token → feed that token back → current
Q/K/V attends allowed past and current K/V → append processed-token state → next
scores and token. Rejoin the entire request before discussing performance.

An initial optional prediction asks why a parallel GPU does not emit the entire
answer at once. The transfer asks what necessarily changes for 10 versus 100
sampled tokens at fixed prompt/model. Count every pick including an end marker:
N picks comprise one from prefill and N−1 decode steps. More sequential steps and
larger retained state follow; an exact total-time ratio does not.

Rubric: 0 = cache enables the entire answer at once or claims exactly 10× time;
1 = says “more steps” without explaining the next input or retained state;
2 = traces each new token as the next input and explains why exact time requires
workload information. Proposed 4/5 formative success gate was not tested.

Grant's visual reasoning makes the dependency visible; Feynman's plain causal
language precedes names; Veritasium's prediction/transfer exposes a misconception.
Anatomy's stable labeled component identity informs craft, while logical data
flow replaces a fictional physical appliance. This example uses ManimGL, not
Anatomy geometry, and none of these creators endorses the product.

Narration is local macOS Samantha with a zero speech-API budget. The planned
3–5-minute scope grew to 5:48 after review-driven clarification. Actual technical,
engineering, craft and learning evidence remain separate in the README and review
history. No human acceptance or live publication is implied.
