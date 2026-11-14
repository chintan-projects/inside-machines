# Claims and assumptions

| Claim | Evidence | Boundary |
| --- | --- | --- |
| A causal position reads self and earlier positions; appended future positions cannot change its earlier inputs/results. | [HF cache explanation, Attention matrices](https://huggingface.co/docs/transformers/main/cache_explanation); exact model mask and append/edit tests | A fixed causal model and unchanged earlier text/positions; no claim about arbitrary edits or bidirectional models. |
| Each layer derives its own keys and values from that layer's inputs; the current input's K/V joins allowed past K/V. | HF Attention matrices / cache update formulas; mechanism trace | This is source preparation, separate from the completed layer output and from chosen output tokens. |
| The last supplied position's output chooses the first new piece; the selected piece becomes the next input. | HF generation loop; visible chooser/input traces | Greedy two-candidate toy, not a real vocabulary or model-weight disclosure. |
| Reusing valid old K/V avoids rebuilding those entries, while new-query reading and local updating remain necessary. | HF cache explanation; exact kept/cleared trace equivalence | Preparation counts are not elapsed time or all arithmetic. |
| R6's positive-part sharing has the same causal argument structure but different numerical behavior from softmax. | Explicit own model definition; tests of its arithmetic and unchanged-prefix equivalence | **Teaching simplification.** This is not the standard formula in [Attention Is All You Need §3.2.1](https://arxiv.org/abs/1706.03762). No real-model quality/performance claim. |

All values are assigned, untrained, illustrative numbers from `lesson/mechanism.mjs`. No training occurred. The calculator omits vector geometry, positional encoding, normalization, biases and a real vocabulary. Its two layers have one scalar input per piece and a simple pointwise local update. Learned semantic meanings, training, hardware bottlenecks and factual certification are outside this model.

Source/code consistency, automated comprehension, visual/accessibility checks and human learning/taste are separate evidence. A passing source review is not independent technical or human acceptance. Older R2/R3/R4/R5 artifacts are preserved; R6 does not retroactively approve them.
