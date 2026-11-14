# Prefill/decode r3: learn at your own pace

A local interactive explanation of why a chosen text piece has to go back into the model, and what per-layer saved preparation avoids. The core is 392 words. Worked layer, key/value and output-scoring calculations are available through guided help.

This revision passes a fresh automated **self-paced product** check after one layer-help path. It does not pass the separate continuous-narration review. New speech and film delivery are held; the page does not present an obsolete movie as the new explanation. No human acceptance or live-app release is implied. The r2 experiment remains preserved alongside this directory.

From the repository root:

```sh
node experiments/prefill-decode-r2/r3/build.mjs
node --test experiments/prefill-decode-r2/r3/tests/invariants.mjs
node experiments/prefill-decode-r2/r3/review.mjs --port 8879
```

Open <http://127.0.0.1:8879/>. This serves only the local HTML and receipt. Opening `interactive/index.html` directly also works. Playback and help make no AI calls.

Try “I’m lost” on different steps. It opens the repair for that step. “Dive deeper” offers related paths; a named question routes to its prepared explanation. Unknown questions get an honest clarification. Each guided path returns to the same step and cache experiment. Restart clears questions and written attempts. This is prepared contextual help, not live AI chat.

## Continue the implementation

- `lesson/mechanism.js`: fixed untrained numerical toy. The math remains separate from drawing. Cached and rebuilt passes give identical scores and choices. Per-position traces expose preparation from layer inputs, complete layer outputs and output-scoring products.
- `lesson/teaching.json`: core, repairs, depth and assessment. `build.mjs` makes the inline page and Studio script from it.
- `lesson/recovery.js`: topic-independent help routing and return state, exercised with inference and refrigerator metadata. That fixture proves controller reuse, not refrigerator teaching quality.
- `interactive/src/`: visual and interaction adapters. The actual layer and word-score values come from the toy.
- `review/`: real evidence and remaining limits. Learner answers are in memory in the page; test transcripts and media stay local.
- `video/production/`: editable ManimGL adapter and draft plan, not a delivered r3 film. The canonical narration text matches the core but its once-heard presentation has unresolved findings.

The [portable repair guide](../../../plugins/inside-explain/skills/explain-visually/references/teaching-repairs.md) and plugin 1.1.1 preserve the workflow for Claude Code and Codex. New helper video projects enforce a script-bound fresh-reader record before the Studio wrapper reads a speech credential. `review/core-readiness.json` deliberately remains blocking here. A self-paced learning check cannot approve continuous narration.

## Evidence and costs

See [REVIEW.md](REVIEW.md). The final product reader explained all five causal/changed-case questions, using the functioning layer-help path for the local update and key/value jobs. Earlier source-only reviews repeatedly found overload, missing intermediate states and ambiguity. Their findings caused rewrites; their still-open narration findings remain visible.

Five unfamiliar human learners, a real-phone accessibility walk, independent human technical review and owner taste approval remain unmeasured. The app should not outsource known automated confusion to those reviewers.

Initial Claude Opus 5.5 authoring reported **$0.9042344 API-equivalent**, not an invoice. Codex edits and automated reader usage are unmeasured. **No new ElevenLabs speech was generated in r3.** The preserved $1 series speech-estimate budget does not cap subscription usage or all account spending. No live application, provider, storage or production schema was changed.
