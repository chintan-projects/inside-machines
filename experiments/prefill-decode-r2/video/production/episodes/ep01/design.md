# ep01 design

- Opening question: the viewer has watched "blue… and…" stream in; a GPU is parallel, so why one at a time?
- Aha: "blue" is picked but not processed. The next scores come from position 4, which cannot exist yet. Known
  tokens go together; picked tokens go one per trip.
- Central image: the board (positions × two layers), input chips below, picked chip waiting above.
- Takeaway aspects. Applies: ordinary causal decoder, one request, greedy toy rule. Mistaken for: a display effect,
  or the cache storing answers. Limits: no speed claims; batching and hardware in interactive depth only.
- Promise: hook_guess is settled in fp_settle.
- Terms taught before use: token/position (kp_tokens), layer (kp_layers), causal mask (kp_lookback), attention and
  feed-forward network (kp_two_jobs), decoding rule (fp_pick), key/value (fb_kv), query (fb_query), KV cache (kv_name).
- Misconceptions: gpu_should_parallelize_answer → hook_guess + fp_settle + cl_reframe; picked_means_processed →
  fp_not_processed + kv_last; cache_stores_answers → kv_not + cl_transfer_reveal.
- Transfer: cache off before "blue" goes in (cl_transfer_ask, 3 s pause, cl_transfer_reveal). Interactive keeps the
  answer hidden behind its own button and scores 0/1/2.
- Self-check: concrete hook in 5 s; guess beat; every link its own beat; conclusion beats paused; close is a reframe.
  Short-version skeleton (no roadmap or strange preview: not applicable to the short version).
