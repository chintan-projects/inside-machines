# Vacuum production-system study

Owner request: compare several OpenAI + visual-tool approaches on one vacuum
example before selecting a system. Keep the curiosity answer short, with optional
depth for a broad intended age range. The existing product has not demonstrated
that learning bar; BUG-004 remains open.

Built for local review: `experiments/vacuum-lab/`, with generated output and evidence
under ignored `.vercel/vacuum-lab/`. One self-contained HTML embeds actual Anatomy
kit/resvg, Manim Community, Motion Canvas Scene2D/Stage and Remotion renderMedia
films. Each has the same 44-second narration, claims and chapter timing plus a
12-second ideally sealed-inlet experiment. Sources and authoring briefs are visible
in the page. The duplicate Motion Canvas request was interpreted as Remotion.

This is OpenAI Codex interactive authoring, with human direction, implementation
choices, research and repairs. No separate application model API calls were made.
Exact API model identity/token receipts are unavailable and are marked null rather
than invented. Render time excludes authoring and is not cost per accepted lesson.
Comparing these authored approaches does not isolate an engine's intrinsic quality.
The existing app, provider routes, budgets, public artifacts and private history
were not changed. No Vercel deployment or production publication was performed.

## Observed engineering and agent review

- All eight MP4s decode with audio, 960×720 frames and matching 44/12-second durations.
  Packaging checks story/source hashes and receipt-bound bytes, and rejects active
  exports. Same-adapter locks prevent overlapping local render writes.
- Four common-model tests pass: blocking versus continuing fan, chapter continuity,
  deterministic seek/invalid time, connected-path placement. Actual encoded title
  checks at 12/23/34 seconds pass for Manim, Motion Canvas and Remotion.
- The initial Manim treatment was too similar to a whole-machine schematic. It
  was changed to independently built working insets for the fan, nozzle and bag,
  followed by the whole. A visible title mismatch at an exact chapter seek exposed
  an off-by-one render clock; corrected and guarded using decoded MP4 frames.
- Three agent critique rounds used 390/768/1280 widths and reviewed hierarchy,
  typography, working mechanism, controls/state and responsive/accessibility behavior.
  Main fixes: controls moved above the picture; enlarged Anatomy labels/framing;
  tablet uses the full diagram width; removed duplicated experiment explanation.
  No horizontal overflow in the checked viewports; initial Play is visible on phone.
- Browser walkthrough: matched chapter switching preserves time; block/restore works;
  static steps, enlarged view, Escape, tab Home navigation and range arrow seek work.
  Reduced-motion initialization uses stills. Loaded-page comparison and explicit
  playback work with network disabled. Temporary network/media/viewport overrides
  were restored. Feedback is page-local; it is not a human learning result.
- Direct `file:` navigation could not be tested because browser automation permits
  HTTP/HTTPS only. The self-contained artifact was reviewed through a loopback server.
  Fresh direct-file opening and real iOS/Android device behavior remain unobserved.
- Existing app verification: 166 Python tests pass, three Postgres integration tests
  skipped (database transactions unchanged), backend/main coverage 87.26%; Ruff,
  strict mypy (74 app/test files), TypeScript, ESLint, ten JS tests and build pass.
  Experimental TS also passes strict checking/lint; both experimental Python files
  pass Ruff and strict mypy with the actual Manim environment where applicable.
  Linux deployment packaging was not rerun because no deployment change was made.

Agent rubric, not acceptance: utility 4/5 (matched comparisons work; learning is
unmeasured); usability 4/5 (main controls are reachable, native-phone evidence
pending); desirability 3/5 (physical and abstract treatments differ; owner's taste
is unmeasured); surprise 3/5 (the blocked-inlet observation may change a misconception,
an inference until tested with beginners).

## Decision and next falsifiable prediction

Owner selection pending. Provisional agent interpretation: Manim's large causal
views make the relationship easier to inspect; Anatomy makes the physical assembly
more tangible. This is an inference about authored examples, not a learner outcome
or a universal model/engine ranking. Motion Canvas and Remotion implementations
do not establish those tools' maximum craft potential.

Next hypothesis: beginners can explain why a kinked-shut hose prevents continuous
pickup despite a running motor after seeing the preferred example, before revealing
the transfer answer. Use the brief's predefined rubric with five initially unfamiliar
learners. Independent technical review, owner actual-phone craft approval and
beginner results are still missing. A second concept is needed before selecting a
universal production default; no family release or global goal completion is claimed.
