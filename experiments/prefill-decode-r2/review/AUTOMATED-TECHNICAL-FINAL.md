# Automated technical review — final source snapshot

Date: 2026-11-13. Status: automated source and mathematical checks passed for the declared two-layer, two-dimensional, single-head, greedy toy. No remaining material defect was identified within this reviewed scope. This is not human technical approval, learner acceptance, or an owner craft review.

## Source identity

SHA256 of the files read and exercised:

| File | SHA256 |
| --- | --- |
| `lesson/mechanism.js` | `69f6efd70017f5a18079984ceb2980844d04c8f9ddd998d2299bc32133dfb14b` |
| `lesson/checkpoints.js` | `5a3fb5d8fe6273d7626b7a2bd5ddbc0ee1f62265d4e0e86d91572817593cca34` |
| `interactive/src/app.js` | `57666fb600c93929f44648962fdbad04b81d149c15165d8cc5bd64319f8fd960` |
| `lesson/story.js` | `6adc640ef20759373982de3442f4b9de1b7a45752f68a3625bec91cb11d29c4b` |

## Observed results

- Deterministic Node probes covered 4,696 request cases: every sequence of the eight embedding tokens of lengths 1–4, plus default and six-token prompts with 1–8 selections. Independent scalar equations agreed across 3,596,852 numeric comparisons; maximum absolute discrepancy was zero with the scalar operation order used in the final probe.
- Cache-on and full-recomputation runs were bit-identical for all intermediate inputs, Q/K/V, attention scores and weights, attention outputs, residual/FFN outputs, final vocabulary scores, and both layers' stored K/V. Additional trace observations were instrumented in memory; authored sources were not changed for the probes.
- Default picks remain `blue`, then `and`; all ten default vocabulary scores are bit-identical to the earlier reviewed version. With one selection, only prefill runs: the final trace is position 2 and `blue` is selected but unprocessed. The second pass processes position 3 (`blue`) and selects `and`.
- Six prompt tokens make 12 K/V pairs during prefill. To choose the second answer token, caching makes 2 new pairs and reuses 12; cache off rebuilds 14 and reuses none. Counts are pairs across two layers, not execution time.
- All eight masks, stable large finite scores, 30 invalid-input probes, and 192 positive-integer lane-count cases passed. An all-masked row explicitly returns `valid:false`, `reason:"no_allowed_positions"`, zero weights and `output:null`.
- The value-dimension fix at `mechanism.js:76` passed both one- and three-component value examples with a two-component query/key. Output dimension follows the values.
- `layer_example` and `decode_example` in `exportStates()` exactly equal the actual first-layer prefill and decode traces; `numeric_example` equals the actual first prompt K/V entry.
- The newly exposed feed-forward trace fields match independent calculations of both matrices, the hidden vector, ReLU activation, output delta and residual output. Their extraction preserves the existing arithmetic and default scores.
- Both cache settings preserve selected-versus-processed checkpoint states. The blocked edge is `{layer:1, from:1, to:2}`, a valid zero-based layer and forbidden future-position connection.
- A minimal DOM harness executed the actual scoped app functions: prefill and decode views consumed their respective traces; all-masked attention displayed its invalid-result explanation without formatting `null`; restoring the causal mask cleared both query inputs' `aria-invalid` flags and rendered a valid result.

## Narration and limits

The latest core narration was read for material technical falsehoods. None was identified within its ordinary causal autoregressive scope. Its displayed numeric examples, pair counts, greedy choices, cache invariance and selected-but-unprocessed statements agree with the computation. This does not claim that speculative or other specialized generation procedures obey a one-new-token-per-pass limit.

These observations establish behavior of the reviewed source snapshot and Node harness. They do not establish browser layout, actual-phone behavior, exported film fidelity, real-model numerical equivalence, GPU scheduling, latency, or learner comprehension. Those remain separate review activities. No paid services or credentials were used. The only file authored by this review is this report.
