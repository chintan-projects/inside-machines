# CE-1 implementation and evidence

The implementation follows [ADR 0001](architecture-decisions/0001-concept-explanation.md).
This is an implementation record, not the owner's lesson acceptance. BUG-004 remains open.

| Requirement | Implemented path | Evidence / limitation |
| --- | --- | --- |
| CE-01–03 | Three filled lesson records, goal/misconception, prerequisite beat dependencies, optional pre-result prediction; AC starts with touching warmer/cooler blocks | Typed authoring contract and deterministic reveal. Beginner prerequisite comprehension remains unmeasured. |
| CE-04–07 | Safe declarative causal insets; compression reduces chamber volume, phase changes cross a tube wall, restriction changes the downstream mixture; anchored core labels | Structural checks reject color-only changes, absent labels and sampled clipping. They cannot certify physics or label placement. |
| CE-08–10 | Shared CE beat clock, piecewise poses and qualitative scenario outcomes consumed by React and server SVG/video | Cross-language pump-path regression and boundary tests; no invented temperature, pressure or efficiency readings. |
| CE-11 | Whole-system final beat, explicit simultaneous/sequential/controlled operation, normal/counterfactual scenarios | AC energy balance, washer tumble/spin, cooker confinement. Each family remains a separate draft. |
| CE-12 | Claim ledger with actual URL/section/page, generic/inference scope, limits and per-beat evidence UI | Danfoss printed pp.20/22 inspected for throttling; Whirlpool parts sections 1/2/4 checked. Independent technical review is pending. |
| CE-13 | New-situation transfer before reveal, optional unsent reasoning and teach-back, predefined reasoning rubric | Recognition and written reasoning are separate. No model grades or stores private answers. Learning gain remains unmeasured. |
| CE-14 | Static before/after, readable text alternative, keyboard component buttons, reduced-motion snapshots, explicit offline save | Automated checks do not establish actual-device accessibility. Browser and real-phone evidence are distinct. |
| CE-15 | Owner workbench/API, artifact-bound append-only engineering/technical/craft/learning/release records | Technical pass requires independent human attestation; craft requires real phone; learning requires five initially nonexpert learners and ≥80% causal + transfer score 2. The app cannot authenticate reviewer expertise. No human passes have been fabricated. |
| CE-16 | v1 reader/digest preserved; v2 author boundary; immutable new IDs/spec/video hashes and trusted renderer fingerprint; owner revision command | Atomic Postgres regression and full real-MP4 revision test preserve the parent's private history. Stale AC renderer data falls back to its preserved video/text. |
| CE-17 | Playback/assessments/scenarios use no paid call; counts opt-in, no answer text; new drafts/chat use the existing gateway and atomic budget ledger | Duplicate revision clicks share one reservation; failed paid attempt requires an explicit new operation. $50 total app-AI ceiling retained. |
| CE-18 | One versioned storyboard/pose contract drives insets, computer narration, captions, video and static checkpoints | Exact raster dimensions regression prevents shortened/corrupt video. Trusted AC SVGs are shared with both renderers. Human semantic parity review remains required. |

## Modules and operation

- `backend/teaching_contracts.py`, `teaching_state.py`, `teaching_quality.py`: typed data, pure sampling and publication floor.
- `backend/teaching_svg.py`, `renderer_assets.py`, `web/teaching/`: bounded rendering and learning experience. No generated executable code.
- `backend/concept_publication.py`: deterministic local narration/render, verified private upload and immutable atomic import. No paid model calls.
- `backend/learning_reviews.py`, `teaching_routes.py`: owner review gates and consented coarse events.
- Existing pipeline: CE-1 author/review schemas and three structural gates; owner revision uses the same budget, queue, checkpoints and receipts.
- `backend/evaluation.py` and `evals/`: fixed cases, artifact/usage packets and explicit human ratings. Unmeasured fields remain unmeasured; no OpenAI/Claude/open-model equivalence claim.

## Verification in this iteration

Observed: Ruff, strict mypy, 141 backend tests including three disposable Postgres tests,
86.68% backend coverage; TypeScript, ESLint, ten JavaScript tests and production build pass.
The provider in pipeline tests is synthetic; transactions, media encoding and artifacts are real.
Linux packaging, browser, hosted runtime and paid generation observations are recorded below
when completed. Their earlier-revision evidence does not automatically transfer here.

Pending: independent technical review, actual-phone craft/accessibility walkthrough,
five-beginner causal/transfer test, optional next-day retention and owner's release decision.
The product remains a protected review alpha. These are missing observations, not capabilities
that software can truthfully mark passed on its own.

### Observed local/runtime checks

- Three original authored media files validate against their exact source spec and
  SHA-256: AC 100.51 s / 804 frames; washer 60.15 s / 481; cooker 57.43 s / 459.
  The sub-frame video/audio differences are bounded by the 8 fps frame interval.
- Chrome desktop, 768 tablet and 375/320 phone widths inspected. Narrow layout is
  contained; component focus, meaningful compression, whole-room counterfactual,
  transfer reveal, enlarged diagram and Escape/focus restoration exercised.
- Narration starts at the current causal checkpoint. Reduced motion produces static
  before/after poses. Explicit save survives full offline reload and narration plays
  from a local Blob at readyState 4. Offline sign-out stays signed out on reconnect.
- Owner release submission is disabled without the four required evidence gates.
  No human review or learner result was entered during agent verification.
- Linux packaging verifier passes with both API/queue functions, real queue trigger,
  shared services, font, both trusted SVGs, Linux resvg/ffmpeg and versioned shell;
  private local inputs are excluded. CLI packets export/compare without paid calls,
  retaining unmeasured human judgments rather than inventing a provider ranking.

See the friction log for findings and fixes. These are observed implementation
checks, not independent scientific review, actual-device approval or learning gain.


### CE-1 generation latency finding

The first combined research/author call timed out at 210 seconds. It published
nothing and retained $0.65 of unknown billing; that failure is included in a private
evaluation packet. [ADR 0002](architecture-decisions/0002-checkpointed-evidence.md)
separates the small evidence retrieval and larger scene authoring into explicit,
checkpointed task routes. Source boundaries, invalid research, budget limits,
legacy paid-output migration and failure export are tested. New split-path runtime
evaluation remains required before claiming generation is reliable. The previous
successful v1 cost benchmark does not establish CE-1 generation success.

The split path completed evidence and authoring but full-copy review hit the output
limit. New jobs review the entire artifact using a concise SHA-bound verdict; a
rejection or wrong hash cannot publish. Explicit same-owner recovery can reuse a
validated authored checkpoint after a known billed review failure, without paying
again for evidence/drawing or mutating the failed operation. Runtime acceptance
of the revised review protocol remains pending. Search-tool accounting now excludes
known page-open/find actions and labels omitted action data as an estimate.

Catalog lookup follows immutable supersession chains, so older aliases resolve to
the latest artifact even if a revised author omits them. A regression checks two
revisions, zero new paid work and a corrupt-chain error instead of regeneration.

New declarative context parts cannot carry legacy motion; all causal motion uses
the shared teaching graph. Phone component focus reuses the bounded scene viewport
and includes its anchored label; the washer pump focus was inspected at 375 pixels.
Empty pose fills now resolve against the original graphic colour in both languages,
so a new colour does not appear before the causal change. Existing three authored
artifacts have no one-sided colour endpoints; their stored media meaning is unchanged.

Compact author transport (`backend/author_transport.py`) expands into the unchanged
full lesson and pose schemas. Hash-preserving round trips and full real-MP4 pipeline
tests cover the new protocol; old paid-output migration keeps its original reader.
Confirmed output-limit failures remain in private evaluation packets and the ledger.
No automatic paid retry or reduction in the quality floor is introduced.


### Completed generated runtime case

A fresh explicit typed patch repaired an exact rejected source, passed fresh
full-artifact editorial review, completed three narration calls and produced a
51.03-second captioned video. Hosted playback, prediction, causal controls,
counterfactual, transfer reveal, keyboard enlarge/Escape and 375-pixel containment
were exercised. Repeated lookup reused the new revision with no new job or spend;
old media/spec, private chats and ledger hashes are unchanged. See LIVE-BENCHMARK.md
for costs including failed/reused prerequisites. BUG-006 is fixed for the missing
benchmark, not a claim of broad generation reliability. BUG-004 stays open.

A separate ownership audit found the deployed source scope uses the work-email
account despite a personal workspace name. Correct Gmail-account migration of
project, Neon and Blob is pending; BUG-007 records the issue. Further deployment
is held. No human technical, actual-phone, beginner or owner gate is inferred.
