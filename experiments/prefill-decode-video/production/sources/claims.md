# Source ledger and scope

Conventional dense, full-attention, causal decoder-only transformer inference.
Already-resident model weights; illustrative token splits, scores, three layers
and timings. No measured GPU/model run, training, speculative decoding or MoE
performance claim. Re-read the primary sources before changing the lesson.

| ID | Claim | Primary source and location | Limit |
| --- | --- | --- | --- |
| C1 | Known prompt positions can be processed together within a layer; causal attention permits the current position and earlier ones. | [NVIDIA Inference Optimization](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization/), Understanding LLM inference; [HF How caching works](https://huggingface.co/docs/transformers/main/cache_explanation), Attention matrices. | Layers still depend on earlier layers; no future-token leakage. |
| C2 | The last prompt position's scores produce the first sampled output token. | NVIDIA prefill paragraph; HF DynamicCache generation loop. | The selected word is a toy outcome, not measured model output. |
| C3 | A sampled output becomes the next input in ordinary autoregressive decoding. | NVIDIA decode paragraph; HF generation loop. | One request; no speculation. |
| C4 | Saved per-layer K/V is reused, and current K/V is added when that token is processed. Attention still consumes allowed past and current K/V. | HF Attention matrices and Cache class. | Cache is not answer text, stored answers or model weights. |
| C5 | Work shape and memory/compute balance differ between phases and depend on workload. | NVIDIA Understanding LLM inference and Batching; [Co-Designing Attention](https://developer.nvidia.com/blog/co-designing-ai-model-attention-for-fast-interactive-long-context-inference/), phase comparison and prefix-cache note. | Qualitative tendency; hardware, context, batching and model design matter. |
| C6 | More sampled tokens require more sequential iterations in the stated scope; exact time ratio does not follow. | C2–C5 and counting arithmetic. | Count every pick, including the end marker: N picks use one prefill plus N−1 decode steps. |

For reproducing the original reading, Hugging Face's Markdown is available in its
official Transformers repository at `docs/source/en/cache_explanation.md`.
NVIDIA's complete articles are linked, rather than copied into this repository.
This ledger records factual scope, not independent scientific certification.
