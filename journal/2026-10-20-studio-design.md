# D1: design the interface around the visual explanation

Owner direction: lock Claude + Anatomy for visual production and address the
interface's poor design. ADR 0005 records that direction without silently changing
deployed provider routes or claiming all existing work was authored by Claude.
The shared local GPU player is the first design consumer; the original vacuum
artifact and Vercel app remain unchanged.

Brief: `design/lessons/studio-interface.md`. CE-05/08/14/16/17/18. G1–G8,
mechanism rules, assessment answers and narration are unchanged. No factual or
independent learning acceptance is inferred from this presentation change.

## Three bounded render rounds

1. Replaced the cream/serif pill stack with the project's system typography,
   a compact identity/question, desktop path rail, large cool drawing stage,
   attached narration and adjacent tools. Observed: the repeated global/node
   questions still competed on phone.
2. Made the current question the single heading; gave chapters descriptive
   labels; used a native phone selector. Observed: the long final-node button
   compressed the selected chapter. Manual playback also needs a secondary
   pause/resume beside the full narrated tour.
3. Shortened the leaf action to Questions with an explicit accessible name;
   allowed transport wrapping; checked keyboard focus and 44px targets.
   Illustration assumptions remain expanded by default, because hiding the toy
   model's limits for a cleaner screen would undermine trust. Final affected
   renders and scope visibility were rechecked.

The layout uses no external fonts or decorative animation. Reusable controls
and tokens live in the shared studio, not GPU-specific UI branches. The native
selector uses the same selection/back/mute state as the desktop rail. Visited
prerequisites do not repeat an advisory paragraph; an unseen prerequisite is
still disclosed. Seeing a node does not imply learning or mastery.

## Observed evidence

Final HTML SHA:
`f87a9ae65c8a180bf60379ba0d5298b56fa3e73e7212ee4388ca2fa317313c55`.
S4 is archived privately with SHA
`0194186d7746ed696e3d706a5481d6c8a545a90f9b4f8acc898cf7ccc93aaffc`.
Art, original Claude response, Anatomy runtime and all narration manifests are
byte-identical to S4. The usage ledger is unchanged; new API cost is $0.

Private `studio-d1-browser-review.json` separates functional-base checks from the
final disclosure-only delta and binds final responsive evidence to the final
hash. Screenshots `studio-d1-{phone,tablet,desktop}-{core,matrix}.jpg` stay ignored.
375/768/1440 renders: no horizontal overflow, no core SVG text outside the view,
all visible controls/summaries at least 44px; matrix text minimum 14.58px at 375.
At fresh phone entry, the drawing begins at 368px. The long matrix question and
return/prerequisite context still make branch entry denser; do not infer ideal
small-screen hierarchy for every future topic from this one path.

Actual browser: decoded audio advances; Pause stops it; mute works. Manual
calculation stays silent with visible working controls. Typed natural depth opens
the next node; Back restores the exact paused 46.5027-second scene. Native chapter
selection does not autoplay. Leaf/missing-topic responses remain honest. A fresh
memory branch plays with network disabled and reduced-motion stills. Keyboard Tab
reaches the selector with a 3px focus outline. No console errors were observed.
Illustration limits are visibly expanded. Text contrast: blue/white 5.79:1;
muted/white 5.86:1, muted/stage 5.41:1. This is not a complete accessibility audit.

Ruff, strict mypy (79 files), 197 backend tests/87.77% coverage, frontend types,
lint, 10 tests/build, and studio types/lint/21 tests pass. Three external Postgres
cases skipped; no transactions changed. Linux packaging not rerun; deployment
packaging unchanged. No new live model-quality comparison, push or deployment.
This non-LessonSpec local HTML has no production publication/quality verdict.

## Judgment and next evidence

Agent rubric: utility 4/5, observed playback/experiment/depth jobs are clear;
usability 4/5, tested native controls and return work with visible state;
desirability 3/5, inferred more coherent composition but a conservative visual
identity and dense long-question branch need owner judgment; surprise 3/5,
inferred the existing causal experiments carry the experience rather than new
decoration. These are agent judgments, not owner or learner approval.

Prediction: concentrating attention on the visual and one playback action will
make first use less discouraging. Owner taste/actual-phone walkthrough,
independent technical review and five-beginner transfer evidence remain pending.
BUG-004 stays open. This completes the bounded local design implementation, not
the product quality goal or a family release.
