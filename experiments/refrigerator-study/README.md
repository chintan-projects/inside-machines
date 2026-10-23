# Refrigerator R1 local study

Read [BRIEF.md](BRIEF.md) for the question, claim ledger, teaching choices,
assumptions and transfer rubric. Evidence and remaining gates are in the
[R1 journal](../../journal/2026-10-20-refrigerator.md).

This is the second real topic using the shared D1 studio and `learning-path-1`.
It supplies refrigerator rules and artwork without forking the player, navigator,
model gateway, state manager, configuration, logger or accounting. `model.ts` owns
qualitative outcomes, slider-crank geometry and illustrative energy accounting;
`scenes.ts` renders that state. `lessons.ts` binds interactions to the same state.
The three scripts in `narration.ts` also drive captions and reduced-motion stills.

Claude authored the physical cabinet/sealed-loop locator with the actual vendored
Anatomy toolkit. Codex supplied inspected integration repairs, independent working
sections and the energy/phase diagrams. Do not describe all views as unmodified
Claude output. The inlet/outlet/piston example is one reciprocating design, not a
claim about every refrigerator compressor.

## Build existing private artifacts

```sh
node experiments/refrigerator-study/finish.mjs
node experiments/refrigerator-study/narrate.mjs
node experiments/visual-studio/build.mjs refrigerator
.venv/bin/python -m http.server 8068 --bind 127.0.0.1 --directory .vercel/visual-studio/public
```

Open `http://127.0.0.1:8068/refrigerator/#core`. Narration synthesis needs the same
Node/macOS Samantha/FFmpeg tools as the GPU study. Pass a trusted plan ID to
`narrate.mjs` to revoice only that plan. Playback is one self-contained HTML file,
with embedded audio and no model call, external font, storage or learner telemetry.
The current local preview is not a hosted Vercel release or MP4 export.

Original response, repaired JS, repair hashes, audio manifests, usage ledger,
HTML and browser evidence remain ignored under `.vercel`. `finish.mjs` fails if
an exact repair anchor changes; the shared build checks receipt completion,
response/repair hashes, narration hashes and both Python/TS path schemas. Packing
is defense in depth for inspected local code, not an arbitrary-code sandbox.

`fridge-art-1` failed closed at 16000 output tokens, with known usage and a $0.199326
configured-rate charge. A separately narrowed `fridge-art-2` completed at $0.086938.
Total $0.286264; cumulative trial $4.568218 of $5, no reserved/uncertain amount.
These are token-rate accounting amounts, not an independently verified invoice.
Neither operation is retried or reset. The final brief contains later reviewed
assumption refinements; it is not byte-identical to the dispatched prompt. Do not
rerun a paid operation to rebuild; use the preserved response and its receipt.

```sh
node_modules/.bin/tsc -p experiments/visual-studio/tsconfig.json
node_modules/.bin/eslint --config experiments/visual-studio/eslint.config.mjs experiments/visual-studio experiments/gpu-study experiments/refrigerator-study experiments/shared
node --test experiments/gpu-study/*.test.mjs experiments/refrigerator-study/*.test.mjs experiments/visual-studio/*.test.mjs experiments/shared/*.test.mjs
```

This local HTML does not pass through the production LessonSpec publication
pipeline. Independent technical review, owner actual-phone design judgment,
screen-reader inspection and initially unfamiliar beginner transfer evidence
remain pending. Engineering checks do not accept those gates or release a lesson.
