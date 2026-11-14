# R3 learning brief

Question: Why must the chosen text piece go back into an ordinary next-token model before the following choice, and what does caching earlier work save?

Audience: curious novice, inferred rather than measured. The complete experience supports self-paced exploration and optional concrete mathematical detail. Broad age suitability is not established.

Outcome: explain the next-slot dependency, separate chosen from processed, distinguish saved reading preparation from completed layer output, and predict rebuilding work when preparation is emptied.

Hypothesis: one stable example, explicit input/preparation/output paths and current-step recovery will let a fresh reader explain the dependency and transfer it to a different prompt length, using help when needed, without forcing projection algebra into the core.

Input → each position's next-slot task → repeated layers reading allowed past and updating working numbers → scores → choice outside layers → chosen piece back as new input → use valid earlier per-layer preparation → next choice.

The fixed untrained toy uses two layers, two coordinates, one head, ReLU and largest-score selection over five candidates. It is not trained for word meaning. The core counts positions processed through the whole model; it gives no timing or speed ratio. Earlier positions cannot read later ones. Editing earlier text does not have the append-only cache guarantee.

Core: The / sky / is → choose blue (unprocessed) → feed blue → process blue → choose and (unprocessed). First pass computes the prompt; the second processes blue. The cache-off comparison explicitly rewinds to before blue's pass.

Preparation comes from a layer's input; the completed working result feeds the next layer. Separate query, key, value, mixing, residual, local update and word-score products are computed in guided detail, not invented from labels.

Transfer before reveal: SIX supplied pieces, then one newly chosen piece. With preparation kept, process one; with it emptied, process seven. Both read the past and produce the same result for the same deterministic toy input. Rubric: 2 for the dependency and valid reuse/rebuild causes, 1 for one cause, 0 for neither or the answer-cache misconception. A separate blind product reader receives FIVE pieces (one versus six) and an earlier-edit counterfactual, without the rubric.

Recovery uses current concept and beat; ambiguous requests offer related choices. Preserve the exact return point and experiment. Do not invent an AI answer; local prepared help and host conversation have different capabilities. Attempts stay ephemeral.

Gate: unresolved automated inability/contradiction in the intended product learning path blocks human-review handoff. Once-heard movie review is a separate gate; success after self-paced help cannot silently approve the narration. No automatic acceptance after a fixed number of rounds.

One attempted design forced ~575 words of attention arithmetic into the core. It improved concrete coverage but added load. The final core is 392 words with complete guided detail. Product reader 17 resolved its remaining mathematical questions through the layer path. Continuous narration remains held.
