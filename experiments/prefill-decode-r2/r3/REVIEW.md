# R3 review: keep the evidence separate

The product gate passes for the **self-paced local experience with available guided help**. The continuous-narration gate remains open and blocks new speech. Human quality acceptance remains open. This is not a live release.

## Observed learning evidence

Fresh agent `prefill_r3_product_reader_17` received actual browser-extracted core and optional help, without prior reviews, code, hints or answer rubric. It could choose only help it needed. It used the layer path, explaining that the core alone did not explain the position-local adjustment sufficiently for that deeper question. It then correctly explained all five questions and reported no remaining inability or contradiction.

It explained chosen blue versus processed blue, why is's result cannot fill blue's next slot, per-layer preparation versus finished output, key/value jobs, one new position versus six rebuilt positions for FIVE supplied pieces, continued reading of the past, and why editing an earlier piece invalidates blanket cache reuse. The parent scored teach-back/transfer 2/2 against the brief. This is automated evidence, not five human participants.

Earlier implemented-page reader 07 found two real adapter bugs: an IS example was labelled BLUE, and layer 2 displayed blue's input instead of is's matching output. Both were corrected. Reader 09 then answered all five questions without remaining confusion, using the then-long numerical path. The core was subsequently shortened; its later acceptance is reader 17's scoped evidence.

## Narration remains held

Source-only reviewers 02, 04, 05, 06, 08, 10, 11, 12, 13, 14 and 16 repeatedly identified lost transitions when hearing the script once. Changes addressed prerequisite order, list creation, query versus matching list, current-position reading, working output versus cached preparation, per-layer validity, replay continuity and count units. A long arithmetic-first draft still overloaded the core; a compact core with on-demand detail worked better as an interactive product.

Latest source reader 16 still flags missing concrete operations and overloaded spoken transitions. Its open findings are in `review/core-readiness.json` and Studio's review record. The wrapper was exercised: narration stops before credential access. No source finding was marked passed merely because many rounds ran. The video tab is absent until a matching delivery exists; the r2 film is not presented as r3.

## Engineering and truth

The unchanged toy calculations now expose immutable per-position layer inputs, prepared key/value snapshots, completed outputs, attention intermediates and candidate-scoring products. Cache kept/rebuilt equality is checked over forty changed prompts and four choices; layer add-backs and shares are checked. The controller is exercised with inference and refrigerator metadata. Domain reuse does not transfer learning approval.

Required repository checks pass: Ruff, strict mypy, 390 backend tests (10 external Postgres tests skipped), frontend types/lint, 59 JavaScript tests and production build. Local reference invariants and readiness/packaging checks pass. No database transaction was changed.

Browser testing uses actual Chrome at 390/768/1440, including all core states, specific diagnostic feedback, both layer walks, cache and word scoring, literal “I’m lost” and “dive deeper,” unknown-question clarification, exact return, clearing/rebuilding, reset and reduced motion. Browser fixtures do not count as learners. A real phone, independent human truth review and owner craft verdict remain unmeasured.

## Cost and release

Claude Opus 5.5 initial authoring reported $0.9042344 API-equivalent through the personal subscription session. That is not a verified bill. Codex edits and automated review usage are unmeasured. R3 made no ElevenLabs speech call; narration remains held under its separate $1 speech-estimate cap. Playback makes no AI calls.

The previous r2 source and film remain intact. This reference source stays excluded from Vercel packaging. Personal Gmail ownership, app scope and active Neon/Blob ownership were reverified; the live deployment and missing Git automation link remain unchanged. The public source commit does not assert a live deployment or a completed human quality gate.
