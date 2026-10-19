# Learning quality is a release requirement

The October 19 AC screenshots failed human review (BUG-004). Working APIs and a
cheap generation cost did not make the explanation useful. Family release remains
held. This document supersedes earlier visual self-assessments.

## Benchmark and scope

`air-conditioner-craft` is a separately versioned, authored teaching benchmark.
It has four permanently labeled working components, six causal chapters, a
connected cutaway, selective enlargement, state changes, and a narrated video.
The final chapter reunites the continuously operating cycle after the individual
component explanations. Three misconception questions provide corrective feedback.
They do not constitute a validated learning assessment.

Old AC content stays at its original URL with its private conversations. Discovery
points to the new revision after selective import. Existing washer, pressure-cooker
and generated vacuum lessons are visibly marked learning drafts when they fail
the new structural checks. They have not been brought to this craft bar.

## Release checks

| Dimension | Required evidence |
| --- | --- |
| Identify | A beginner can locate every narrated core component without a dropdown; labels remain readable on phone and video. |
| Understand | Explain what enters, what changes, why it changes, and what leaves. Reassemble the full system; do not imply a continuous system switches on one component at a time. |
| Craft | Connected, purposeful hardware; visible flow direction; heat, airflow and working fluid distinguishable without color alone. No cropped labels or captions covering components. |
| Truth | Claims tied to relevant sources, declared generic assumptions, no invented operating readings, no claim of expert verification. |
| Interaction | Part selection, chapters, scrubbing, native video seeking, descriptions and transcript agree. Keyboard alternatives and adequate control sizes. |
| Reliability | Private range video, artifact integrity, immutable published versions, offline reload and logout isolation. Failed generation cannot publish or silently consume more paid phases. |
| Human decision | Owner walkthrough on real phone, beginner teach-back and technical review before declaring the benchmark approved. |

`backend.quality` enforces a floor: at least three component-linked labels,
minimum authoring text size, conservative bounds/nonoverlap, explicit input/output,
a labeled focus used in every chapter, and evidence indices. Schema validation
checks references and safe drawing primitives. Gates run before paid review,
after review and before publication. Owner diagnostics expose bounded findings.
These checks cannot establish scientific correctness, source entailment, label
anchoring quality or learning efficacy. Model review is not independent human review.

## Source-to-claim record

| Claim | Reference |
| --- | --- |
| Separate air streams, sealed refrigerant circuit, evaporation/condensation | [Carrier cycle explanation](https://www.carrier.com/residential/en/ca/products/air-conditioners/how-do-air-conditioners-work/) |
| Four core components and their functions | [Carrier equipment explanation](https://www.carrier.com/residential/en/ca/products/air-conditioners/air-conditioning-equipment/) |
| Outdoor heat equals removed room heat plus supplied work | [OpenStax heat pumps](https://openstax.org/books/university-physics-volume-2/pages/4-3-refrigerators-and-heat-pumps) |

This is a generic split system in cooling mode. It omits controls, humidity removal,
superheat/subcooling and refrigerant-specific details. Colors and motion are
qualitative. No operating temperatures, pressures or flow rates are claimed.
The compressor shell is shown; its internal pump is not animated. The voice uses
local computer speech, disclosed in the UI. Shared lesson data drives both the
SVG interaction and the Pillow-rendered MP4; the renderers are not pixel-identical.

## Verification record — October 19 revision

- Strict Python/TypeScript checks, lint, production frontend build and five JS tests pass.
- 86 backend tests pass with 85.91% coverage, including disposable real Postgres
  concurrency/rollback and revision publication preserving private history.
- Linux API and queue bundle verification passes, including bundled font and encoder.
- Chrome: component choice selects the matching causal chapter; video chapter
  seeking updates the transcript and state cards. Actual MP4 is 92 seconds with
  one optional caption track. The default transcript is outside the drawing.
- Desktop and 375/320 CSS-pixel layouts inspected. Document width equals viewport;
  visible component buttons replace dropdown-only discovery. Temporary viewport
  overrides restored. Main labels measure 14.4 CSS pixels at 375 width and 12.1
  at 320 width. These are browser simulations, not physical-device tests.
- Revised lesson downloaded, reloaded fully offline and played as a local Blob
  video with captions. Font present in the shell cache; no API responses cached.
  Network override restored. Misconception feedback changes after wrong/correct
  choices; no model call is made for these authored questions.

No new paid model calls were used for the authored revision. The earlier live
vacuum cost benchmark remains valid for that specific run, not this revised
quality contract. General generation under the tighter gate and provider quality
comparisons still require live evaluation. No claim of Anatomy-equivalent craft
or family-release approval is made.
