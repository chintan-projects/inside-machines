# Prefill/decode r3 iteration

Question and hypothesis are in the [brief](../../experiments/prefill-decode-r2/r3/BRIEF.md).
The user rejected handing unresolved automated confusion to humans. This iteration
replaces the long required explanation with a 392-word self-paced core and actual
contextual repair paths. The running example and deterministic toy remain stable.

| Concern | Implementation | CE trace |
| --- | --- | --- |
| Next-token dependency | Each prompt position targets one next slot; chosen blue is outside the layers and has no processed result. Feeding it back creates the next-slot task. | 01–04, 07, 11 |
| Layers | Read allowed positions, update working state, pass completed output onward. Optional layer detail shows actual mixing, both residuals and local reworking. | 03–06, 10, 12 |
| Scoring | One actual score per candidate; highest wins in the toy. Guided scoring exposes fixed directions and every product. | 03–04, 10–12 |
| Cache | Input-derived preparation stays beside its layer; completed outputs go onward. Replay clears preparation and selection before rebuilding; counts have explicit units. | 03–04, 07–12 |
| Recovery | Current beat resolves “I’m lost”; named questions select prepared paths; ambiguity offers related choices. Exact return and experiment survive; reset clears attempts. | 06, 09, 13–14 |
| Review integrity | Script digest, genuine fresh-reader record and no unresolved core loss before wrapper speech/delivery. Separate product and continuous-narration evidence. | 15–18 |

The product reader could explain the core dependency and transfer without help. It
used the functioning layer path to answer the deeper local-update/key-value
questions, then reported no remaining loss. This is the intended progressive
experience; it is not evidence that one short paragraph teaches all transformer
internals or that an unfamiliar human cohort has passed.

The narration-only reader still reports lost transitions and insufficient concrete
operations in the once-heard core. New audio and movie delivery remain held. The
product's positive result does not approve the movie. This reference is local and
excluded from deployment; no public registry, backend schema or provider route was
changed. Real-phone accessibility, independent human truth review, unfamiliar
learner checks and owner taste approval remain open.

See the [review](../../experiments/prefill-decode-r2/r3/REVIEW.md) and
[history](../../experiments/prefill-decode-r2/r3/review/REVIEW-HISTORY.md).
