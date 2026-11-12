# ep01 design: Why does AI write one token at a time?

Presenter Theo, mechanism playbook, **short version** (≤6 min). Toy request throughout: prompt "The sky is" →
blue → and → clear → "." → end. All splits, scores and step counts in the picture are illustrative.

## Opening question

Naive: "If the GPU does thousands of calculations at once, why not write the whole answer in one go?" (pause 2.5 s,
open question). Restated after the decode scene: "What must exist before step two can start?" → the previous token.

## Aha

The gold "blue" chip that came out of the top of the grid physically travels back to the bottom as the next input.
Until it has made that trip, there is nothing for step two to process. The sequential dependency is a data
dependency you can watch, not a hardware limitation.

## Central image (spine object)

One grid: columns = token positions, rows = 3 schematic layers (actual layer counts vary). Input chips below, sampled chips
above. A cell turns teal (saved key + value) when its token has been processed at that layer. Invariant: a cell is
teal only if its token is an input that has passed that layer. "blue" sits above the grid with a dashed empty column
until it is fed back.

## Takeaway card

- Name: "The next-input chain".
- Standard picture: gold chip going from the top of column n to the bottom of column n+1.
- One sentence: "The prompt goes through together because it is known; the answer goes one token at a time because
  each token is the next step's input."
- When to take it out: whenever someone asks why output speed differs from prompt processing, or what a longer answer
  costs.
- What it is not: not "the GPU can only do one thing at a time" (prefill shows it can do many positions at once); not
  "the cache stores answers".
- Where it fails: speculative decoding / multi-token schemes and non-transformer designs change the picture (scoped
  out); many independent requests can be batched into one step.

## Takeaway aspects

- Applies to: ordinary autoregressive decoding of a decoder-only causal transformer with KV caching.
- Mistaken for: a hardware limitation; a cache of answers; "parallel means seeing the future".
- Limits: memory-vs-compute is a tendency (long context, batching, architecture, hardware, prefix caching shift it).

## Promises and where they are kept

- "Follow one request all the way and check your guess" (hook/promise) → kept in decode `hook_payoff` and in the
  full-request timeline.
- "Toy, illustrative" (hook/illustrative) → every numeric label on screen says illustrative; transfer avoids 10×.

## Terms (where taught, how)

| Term | Level | Beat | How |
|---|---|---|---|
| token | refresh | prompt/tokens | sentence splits into three chips |
| attention | teach | prompt/look_back | arcs from a cell back to earlier cells, then named |
| causal mask | teach (label) | prompt/no_future | red cross on forward arc; label "causal mask" on screen only |
| key, value | teach | first_token/key_value | one cell split into K and V halves with plain labels |
| KV cache | teach | first_token/saved | named after all nine cells are teal |
| prefill | teach | first_token/prefill_name | brace over the prompt columns after the pass is seen |
| query | teach | decode/query | "what it's looking for", small Q tag on the new cell |
| decode | teach | decode/decode_name | after the first full loop is seen |
| memory-bound | teach (label) | work_shape/decode_waiting | "limited by memory reads"; the term "memory-bound" only on screen |

## Misconceptions

- whole_answer_at_once: said in the hook (the prediction), granted ("the GPU really is parallel" — shown in prefill),
  fails at decode `dependency` (step two has no input until step one finishes), new version `dependency_conclusion`;
  `hook_payoff` says which part was right (parallel hardware) and where it went wrong (the chain).
- parallel_sees_future: prompt/no_future and parallel_conclusion ("together across known positions, never ahead").
- cache_stores_answers: first_token/cache_misread as a marked "Intuition" claim, struck in cache_truth.
- ten_times_tokens_ten_times_time: transfer question; answer separates "more sequential steps" (must) from "exact time"
  (cannot infer).

## Transfer check (case not in the video)

A user pastes a 50-page document and asks for a one-word answer. With only the video's pictures: prefill is a very
wide block (many known positions, processed together), decode is one or zero steps after the first token. So most of
the work is in prefill, and making the answer longer would add sequential steps while the prompt work stays the same.
The video's names (prefill, decode step, next-input chain, saved keys and values) should suffice. This is a planned transfer check reasoned by the author, not an observed viewer result; the dominant phase there is a tendency (a one-word answer may still be several tokens, and exact timing depends on the workload).

Second quick transfer inside the video: 10 vs 100 output tokens (9 vs 99 decode steps after prefill).

## Self-check

- Mechanism must-haves: every link on screen (known → together → look back → layers in order → last position scores
  → first token → saved K/V → sampled ≠ processed → feed back → query/match/append → next token → dependency).
- Guess beats: 2 (opening, transfer). Each is a question the viewer would ask.
- First 5 seconds: a streaming answer, not a title.
- Close: reframe, not a list.
- Honesty: toy/illustrative label; tendencies-not-laws beat; scope line naming speculative decoding.
- Short skeleton: no roadmap/strange preview (not applicable to the short version).
