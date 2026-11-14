# Follow one choice into the next

A local, editable explanation of why a chosen text piece still needs processing and what a separate key/value cache at each layer saves. The running example is **The / sky / is → blue → and**.

The delivered local movie is **29:17**, with eight scene links, English captions and a complete transcript. It is a detailed worked-model study rather than a short introduction. The exact narration passed a fresh reader with zero findings and a separate uncoached five-case transfer test. Human learning and taste acceptance remain unmeasured.

This revision uses an explicit **structural teaching calculator**, with one number per piece and two layers. Its sharing rule is `(1 + max(0, query × key)) / total_parts`. Actual transformers use softmax and many trained values. The calculator demonstrates dependencies and reuse; its numbers are not literal GPT internals, learned meanings or speed measurements. See [claims](CLAIMS.md) and [the learning brief](BRIEF.md).

## Run the interactive reference

From the repository root, with Node installed:

```sh
node experiments/prefill-decode-r2/r6/build.mjs
node experiments/prefill-decode-r2/r6/tests/mechanism.mjs
node experiments/prefill-decode-r2/r6/review.mjs --port 8879
```

Open <http://127.0.0.1:8879/>. Change a word, layer or retained preparation; all dependent numbers recompute locally. The complete transcript works without audio. Playback and interaction make no AI calls. Follow-up chat lives in the Claude Code or Codex session, not in an embedded chatbot.

The public source package excludes movies, speech files, generated HTML/scripts, private prompts, sessions and account credentials. The watch tab appears only after a local Studio delivery whose script bytes match the current source. A prior movie cannot silently stand in for this revision.

## Reproduce the movie

The evaluated runtime is Explainer Studio **1.3.0**, ManimGL **1.7.2**, with ffmpeg and its scene kit. The production sources are editable; installing those tools is a separate prerequisite. Read the repository's Explain Visually skill and the installed Studio guide.

```sh
explainer-studio doctor --json
node plugins/inside-explain/skills/explain-visually/scripts/project.mjs studio script validate ep01 --series experiments/prefill-decode-r2/r6/video
node plugins/inside-explain/skills/explain-visually/scripts/project.mjs studio narrate ep01 --series experiments/prefill-decode-r2/r6/video
node plugins/inside-explain/skills/explain-visually/scripts/project.mjs studio preview ep01 --series experiments/prefill-decode-r2/r6/video
node plugins/inside-explain/skills/explain-visually/scripts/project.mjs studio render ep01 --series experiments/prefill-decode-r2/r6/video
node plugins/inside-explain/skills/explain-visually/scripts/project.mjs studio notes check ep01 --series experiments/prefill-decode-r2/r6/video
node plugins/inside-explain/skills/explain-visually/scripts/project.mjs studio deliver ep01 --series experiments/prefill-decode-r2/r6/video
node experiments/prefill-decode-r2/r6/review.mjs --port 8879
```

Inspect the actual preview and render screenshots before delivery. The owner selected ElevenLabs Sarah / `eleven_v4`; the wrapper reads the existing macOS Keychain credential only after checking the script-bound teaching gate. This series caps Studio's speech estimate at $2. That estimate is not a verified invoice or a cap on every account's spending. There is no provider fallback or silent paid retry.

A script change invalidates [core-readiness.json](review/core-readiness.json). Obtain a fresh reader and changed-situation test for the changed core before speech or handoff. Three rounds, a correct headline, or passing code tests do not resolve a lost reader.

## Continue the work

- [Mechanism](lesson/mechanism.mjs): pure causal calculations, cache behavior and exact traces.
- [Numerical narration compiler](lesson/narrate.mjs): words derive from the same trace as the figures.
- [Storyboard manifest](lesson/narration.json): ordered scenes and stable semantic beat IDs.
- [Panels](lesson/panels.mjs): maps computed checkpoints to labeled operations and source rows.
- [Renderer](video/production/shared/series.py): uses the actual ManimGL scene kit.
- [Cards](video/production/episodes/ep01/notes.yaml): standalone explanation, predictions and frame links.
- [Review record](REVIEW.md): exact evidence, cost distinctions and remaining human checks.

The replay that clears preparation starts with **text and fixed rules only**, without retained earlier working results. A policy retaining other intermediate states would be a different comparison. Debug traces in this source are inspection records; they are not used as runtime cache inputs.

Earlier R2/R3 examples remain unchanged. R4/R5 local drafts remain held. Automated comprehension, numerical invariants, source consistency, rendered craft, accessibility and human learning are separate checks. This local reference does not release a catalog lesson or change the live app.
