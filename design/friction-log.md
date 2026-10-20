# Inside design friction log

October 19, 2026. Agent assessment of the existing local prototype, based on saved desktop/390-pixel screenshots and source behavior. Real-device and assistive-technology walks remain for the product owner. These observations do not claim human user feelings or completed usability research.

Person: an adult with a concrete question about a machine. Journeys: enter a lesson, watch/inspect, ask about an owned machine, return offline, and ask a new question.

| Journey | Observation and consequence | Evidence | Severity | Next-release status |
| --- | --- | --- | --- | --- |
| Enter a lesson | Introductory content takes much of the phone's first viewport before the machine appears | Seen: [phone screenshot](../shots/mobile.png) | High | PRD requires direct links to begin with the mechanism |
| Explore cause and effect | The timeline changes time, but there is no causal parameter control; the learner cannot yet test why slow and fast rotation differ | Inferred from app controls and model | High | Add one reviewed variable in S0 |
| Inspect the machine | The complete cabinet is visible, but meaningful parts are small at phone size | Seen: [phone screenshot](../shots/mobile.png) | High | Prioritize the active subsystem and test zoom/part-panel behavior |
| Understand an owned machine | The specific-machine form records context but cannot verify or apply it | Seen: [intake screenshot](../shots/specific-machine.png); inferred functional limit | High | Keep explicit status; implement evidence handling only in S1 |
| Ask another question | Unsupported topics correctly explain the local scope, but the prototype cannot supply a new answer | Inferred from source; browser check passed for message | Medium | Route authored questions in S0 and test bounded fresh answers in S1 |
| Return offline | Browser offline reload passed; a fresh iOS installation and native download behavior were not tested | Browser check from prior implementation | Medium | Real-device cold-launch and interrupted-download tests required |
| Read measurements | Illustrative values are identified, but the scene can still appear more exact than the teaching model supports | Seen: [mechanism](../shots/mechanism-closeup.png); inferred interpretation risk | Medium | Per-claim source/assumption mapping in PRD |

## Rubric for the current prototype

- **Utility:** It demonstrates a cycle but cannot yet test the user's main causal question with a meaningful variable or fresh answer. **3/5**, inferred from scope and controls.
- **Usability:** Playback and stages are available, but phone entry delays the object and small parts demand effort. **3/5**, seen in screenshots; real-device behavior unscored.
- **Desirability:** The page is coherent, but the familiar editorial styling competes with a practical learning tool and repeated content cards add little to the mechanism. **3/5**, visual judgment.
- **Surprisingly great:** Coordinated movement/readouts are promising, but a memorable learning outcome has not been observed with users. **2/5**, inferred.

## Human release walk

Before an S0 release, walk entry, Watch/Explore, a curated question, progress restoration, offline launch, reduced motion, and VoiceOver on the target phone. Record screenshot, observation/feeling, severity, and resolution for each issue. Resolve blockers/highs and rescore utility/usability to at least 4 before a release decision. This is a future product-quality gate, not a request to approve the PRD.

Owner decision: pending real-device walk. Prediction: exposing the relevant mechanism and its control immediately will matter more than expanding the catalog from three to ten lessons.

## Connected family-alpha review

The observations above concern the earlier visual lab. The following review covers the new React app and live local API, observed through Chrome tooling at normal desktop width, 768×1024 and 375×844.

| Journey | Observation | Severity | Resolution |
| --- | --- | --- | --- |
| Enter a lesson | Seen: desktop playback controls originally fell below the first viewport | High | Fixed with a viewport-bounded scene; phone controls now fit near y=645 |
| Ask why | Seen: the washer speed experiment changes contact prediction and its diagram at 45 versus 90 rpm | Positive | Keep its idealizations and physics reference beside the experiment |
| Find a saved lesson | Inferred: downloads originally lacked a visible library filter | Medium | Added Saved filter; full offline reload and downloaded video were observed working |
| Return later | Seen: Tumble and its 8.75-second timeline position survive reload | Positive | Progress is user-scoped and cleared at sign-out |
| Keyboard entry | Inferred: a hash-based skip link could change the lesson route | High | Fixed by focusing main content without navigation |
| Account isolation | Seen: offline sign-out remains signed out after reconnect; cache audit showed zero API entries and zero saved lessons after switching member | Positive | Also guard progress persistence during component teardown |
| Inspect small parts | Seen: complete machine remains legible on phone, but individual fittings are small | Medium | Large part selector provides equivalent descriptions; evaluate zoom with real users |
| Request a new machine | Seen: disabled generation saves demand and explains its status | Release dependency | Needs actual provider/budget configuration and a live end-to-end test |

Agent assessment: authored learning has a clear main task and usable controls (**utility 4/5 for existing lessons**, seen/inferred); core browser journeys are coherent (**usability 4/5 in tested Chrome**, seen). The visual language is consistent but schematic detail needs real-phone judgment (**desirability 3/5**, judgment). The causal experiment adds a useful learning moment; whether it is memorable is untested (**surprisingly great 3/5**, inferred).

These scores do not approve a release. Human device/accessibility review, live generation and the product owner's release decision remain pending.

## Live generated lesson — October 19

Seen: a 35-part vacuum cutaway, five stages and narrated video were created on
Vercel; authenticated video delivery and two-member reuse passed. First generation
took 6m16s, so the existing multi-minute waiting copy is necessary. Seen in Chrome:
the default selected shape was a decorative backdrop. Changed the initial focus
to a part referenced by the opening stage; saved user selections still restore.
The generated lesson remains schematic and needs human device review before family
release. Hosted entry is still protected by Vercel Authentication.

Seen on the hosted personal Vercel URL: download, network-offline full reload and
actual 66.02-second downloaded video playback/captions passed. The network override
was restored. Desktop review screenshot: `shots/live-vacuum-review.jpg` (ignored).
This browser verification does not replace the person's phone walkthrough or release decision.

## Human review — October 19, 15:05

Release not approved. The owner reports that the AC schematic lacks visible labels
for named components and that its four stages do not build understanding. Seen in
the supplied screenshots: only Indoor/Outdoor labels; component discovery relies on
a long dropdown that mixes casings with functional parts. Video narration names an
unidentified compressor, and captions cover the lower circuit. This is a high
severity learning-quality failure, tracked as BUG-004. Infrastructure/live cost
checks do not establish explanation quality. Revise one AC lesson as the benchmark
before expanding the catalog or requesting another release decision.

## AC craft revision — agent observations, awaiting owner decision

| Round | Finding | Resolution and evidence |
| --- | --- | --- |
| 1 | Seen in supplied screenshots: unlabeled parts, dropdown-only discovery, captions over circuit | Four anchored labels persist in scene/video; four visible component controls; transcript outside picture. |
| 2 | Seen during revised browser review: stage text failed to follow native video seeking | Video time and chapter buttons now synchronize focus, input/output and transcript. Actual 92-second MP4 inspected. |
| 3 | Seen at 375/320 widths: smaller secondary fittings need inspection support; desktop video initially exceeded available height | Component enlargement includes its label; whole-machine reset; bounded desktop video framing; no horizontal document overflow. |

Utility: 4/5 agent judgment for the revised AC, supported by component/chapter
interaction. Usability: 4/5 in tested Chrome, with physical-device/accessibility
review outstanding. Desirability: 3/5; purposeful cutaway and typography improved,
but this remains schematic. Surprisingly great: 3/5 inferred for misconception
feedback and linked visual explanation; no user learning result measured.

These are agent critiques, not release approval. Screenshots in ignored
`shots/ac-craft-phone.jpg` and the final hosted review capture support the owner
walkthrough. Other catalog lessons remain drafts. BUG-004 stays open until the
person accepts the revised teaching experience.

## Second human rejection and action-led studio

The owner again rejected the visual quality and supplied the microwave example.
The prior agent ratings did not establish an acceptable craft bar. This revision
changes both teaching structure and the physical drawing.

| Review round | Seen finding | Resolution |
| --- | --- | --- |
| 1: hierarchy and object | Large empty space and page chrome pushed the new figure's next action below the viewport. A detached fastener lacked a supporting frame. | Compact lesson chrome, bounded drawing, single next action; front frame supports the mounting details. |
| 2: type and phone use | Phone overview text needed larger labels. Selecting a lower step could leave the changed explanation above the user's viewport. | Larger overview labels; automatic component focus; explicit whole-system control; phone step selection reveals the new instruction. |
| 3: interaction and access | At tablet width the enclosure controls shrank to several short lines. Scene controls could cover a secondary label. Muted text contrast was too low. | Full-width enclosure choices; controls above desktop artwork and outside phone artwork; darker text. Keyboard inspection and reduced-motion behavior checked. |

Five aspects reviewed: hierarchy, typography/contrast, mechanical drawing,
interaction/state feedback, and responsive/accessibility behavior. Seen: the
selected compressor chapter paused/seeks narration at 32.54 seconds; subsequent
playback advanced to the heat-release chapter. Seen: inside/outside choices update
the same enclosure and change the energy outcome. No numerical performance is
invented. Seen: 320/375/768 widths have no document overflow; the smallest
whole-system labels measure 14.5 CSS pixels. Motion preference override was restored.

Agent rubric, subject to the owner's judgment: the concrete heat-tracing job now
has one dominant action (utility 4/5); tested navigation and recovery are coherent,
with physical-device review missing (usability 4/5). Purposeful hardware, restrained
controls and direct labels show more care (desirability 4/5, subjective). The
sealed-room counterexample provides a causal payoff (surprise 4/5, inferred until
someone learns from it). These ratings are proposals, not human approval.

Review captures: `shots/ac-studio-phone.jpg` and the protected hosted studio
capture. Other catalog lessons remain outside this visual revision. See
`design/visual-learning-teardown.md` for scope and limitations.

## CE-1 implementation — observed engineering and teaching risks

- Real encoded regression exposed a frame byte-count mismatch: the rasterizer kept
  aspect ratio rather than exact requested dimensions. A padded exact-size canvas
  fixes the MP4 timing/corruption issue; real encoding and dimension tests pass.
- A water marker took a diagonal shortcut around a pipe bend. Shared piecewise poses
  now carry it through the actual pump center; JS/Python parity is tested.
- Color or rotating a symmetric housing does not explain an internal action. The
  compressor changes chamber volume; the washer has a visible impeller; the cooker
  uses a labeled conceptual control contact/power state. Independent truth review
  must still assess whether these simplifications teach the right mechanism.
- Source URLs alone hid weak locators. Printed Danfoss expansion/cycle pages were
  inspected; washer inner/outer tub and pump claims now cite relevant manufacturer
  sections. Circular-path and room-energy applications are marked as inferences.

These observations do not close the human rejection. CE-1 render-review rounds,
actual-phone and beginner learning evidence must be recorded separately below.

### CE-1 render review rounds (agent observations)

Live generated vacuum draft inspection: the machine locator was recognizable, but
the independently rendered causal panels contained tiny unlabeled overlays with no
physical surroundings. This is an observed CE-04/05/07 failure, not a human-approved
artifact. The draft was never published. Authoring now explicitly requires a
self-contained large labeled mechanism in each inset; the structural floor rejects
unlabeled detail panels, and review checks the physical context and scale. This
finding invalidates reuse of that authored draft under the current quality gate;
its validated evidence may be reused by a fresh explicit operation. No source
reference or failed receipt is edited into success.

| Round | Consequential finding | Change and observed check |
| --- | --- | --- |
| 1 — hierarchy and interaction | At 375 width, the causal action fell below a tall component/inset stack | Current action remains visible within the teaching workspace while scrolling; actual compression changes the chamber and qualitative state. Desktop question/prediction and restrained step rail inspected. |
| 2 — phone containment and state | The consent label's anonymous flex text overflowed to 434 pixels; narrow media controls needed deterministic handoff | Wrapped a shrinking text span; document width now equals 320. Selected narration starts at the current checkpoint; reduced motion snaps to static end state. Counterfactual changes scene and explanation; transfer stays hidden before reveal. |
| 3 — tablet legibility and inspection | At 768 width, two small figures made inset labels too small | Stack context/inset at tablet width; add a bounded enlarged diagram with keyboard pan, native focus trap, Escape dismissal and return focus. Distinct washer pump and cooker control/scenario paths inspected. |

All five design aspects were considered: hierarchy, type/contrast, physical mechanism
craft, interaction/state, responsive/accessibility. Observed AC save → full offline
reload → Blob narration playback (100.51 seconds, readyState 4); place restored;
offline sign-out then reconnect returns to entry. Sound-off text and component
keyboard alternatives remain available. Temporary offline/reduced-motion overrides
were restored. Browser simulations are not an actual-phone or screen-reader pass.
No human or beginner quality score is inferred. A new human rejection starts a new
bounded iteration focused on the most consequential observed failure.

A fresh vacuum drawing added large self-contained physical surroundings but two
long labels crossed the canvas. The quality gate rejected both before paid review
or media. One label also used padding spaces and a truncated phrase. The next
author request explicitly limits on-scene labels to short concepts and bounded
placement. No clipping threshold or minimum type size is relaxed.

Compact-input iteration: unused paint channels and zero-box polygon metadata
caused format failures; the compiler now handles these explicitly while keeping
all public-domain constraints. The compiled draft still drew a closed duct end
while claiming an open outlet. This is a separate observed CE-04/07 physical
legibility failure, not solved by format validation. Explicit open-passage examples
now govern authoring; policy-bound recovery cannot reuse the older drawing.

The SHA-bound editorial check rejected the next structurally valid scene for
CE-04/05/07/18 failures: pickup markers began inside the inlet, moving-symbol
identities/ports were unlabeled, and enlarged filtration/bypass motion lacked
narrative explanation. This rejection is useful observed evidence; it is not
a technical certification. The next explicit iteration includes the critique
and matching-evidence scene, with new authoring and fresh review required.


19 October, generated vacuum follow-through: the first typed source-bound patch
cleared airflow collision but introduced/revealed label collisions; agent-rendered
seated and bypass views reproduced them. Fresh review withheld publication. The
next explicit patch separated labels and completed review, speech and a 51.03s
MP4. Hosted prediction/causal chunks/scenario/transfer/enlarge/Escape and 375px
containment exercised; native video readyState4, one caption track, time advancing.
Second lookup reused the new revision without new job/spend. Exact parent/history/
old-ledger hashes unchanged. These are agent engineering observations, not human
technical/craft/learning/release approvals. Account audit separately found wrong
owner identity despite personal-named scope; migration is pending, BUG-007 open.


19 October, computing extension (local): observed code forced every topic into a
real-machine cutaway and disallowed the logical diagrams a GPU/LLM explanation
requires. Extracted trusted representation/research/review guides; shared CE state,
claims, assessments and media remain unchanged. Local intake copy reviewed at
1512/768/375 widths with no page overflow; generic/specific-model choices remain
legible, and unsupported exact-model requests return honest generic guidance.
Existing AC seek and component controls still work with neutral system/change
labels. Utility/usability are observed for this copy change; visual craft is
otherwise unchanged, and no new surprising teaching moment is claimed. This is
one focused copy/compatibility pass, not the three craft rounds for a new lesson.
GPU/LLM representations and human learning remain unbuilt/unmeasured. No deployment.

## 2026-10-19 — vacuum phone owner rejection

Observed, high severity (CE-04/05/14): owner's iPhone screenshot puts a tiny whole
machine and several component controls above the actual causal mechanism. Ambiguous
fan label and crude housing undermine trust. Earlier desktop emulation missed this
first-screen failure. Next iteration: detail first, rebuilt physical close-ups,
secondary locator. Actual-phone approval and beginner learning remain pending.

### Vacuum iteration: three agent critique rounds (owner acceptance pending)

1. **390 / 768 / 1280, seen:** hierarchy put the working detail first and moved the
   locator into disclosure. Labels became readable, but primitive surfaces still
   looked generic. Added trusted curved/shaded housings, couplings, fins, screws,
   shaft and bag texture. Found oversized arrows crossing the floor opening;
   corrected marker size and passage alignment. Typography/focus/targets inspected.
2. **390 / 768 / 1280, seen:** keyframe markers converged into one symbol. Staggered
   the paths and added non-merging/hose-boundary regressions. The same safe poses
   drive web and export. Replaced a repeated clogged-bag question with transfer to
   a different blocked component: the hose. No horizontal overflow observed.
3. **390 / 768 / 1280, seen:** comparison controls below the explanation hid the
   changed diagram while selecting a condition. Moved the condition directly
   above the scene and made a choice explicitly replay its modeled change. The
   outcome sits below the drawing. Fixed narrated base/comparison mismatch,
   returned the video to the whole system, and corrected a clipped reassembly line
   using actual bundled-font bounds. Phone navigation text and reset target enlarged.

Final local observations: labeled working detail and action fit the phone viewport;
condition and consequence share a screen; 768/1280 content width equals viewport.
Keyboard slider and Escape from native detail dialog work. Reduced motion reveals
final states on request. Explicitly saved lesson reloads offline and the bag
comparison still works. Browser overrides restored. Decoded 24 fps MP4 frames show
matching artwork and the full-system return. These are agent/emulation observations,
not actual-device, VoiceOver, independent technical or beginner-learning approval.

Agent rubric (judgment, not release approval): the causal job is prominent — utility
4/5; navigation/action/condition are explicit — usability 4/5; original physical
sections carry consistent material/detail choices — desirability 4/5; the blocked
path comparison is useful, but learner delight is unobserved — surprise 3/5 inferred.
The owner's verdict and five-beginner transfer evidence remain missing. BUG-004 open.

## Vacuum production comparison · local authored study · 2026-10-19

Evidence: ignored `.vercel/vacuum-lab/review-desktop.jpg`, `review-phone.jpg` and
encoded media; [record](../journal/2026-10-19-vacuum-production-study.md).

Agent observations across 390/768/1280 widths, not an actual-device owner walk:

- High: the initial Play control appeared below a tall image. Moved controls above
  it; Play is now visible on the checked initial phone viewport.
- High: the first Manim treatment repeated a small whole-machine schematic. Rebuilt
  its fan/nozzle/bag as independent, larger causal views before reassembly.
- High: exact chapter seek could show a preceding Manim shot for one frame. Fixed
  the clock; decoded title checks now cover 12/23/34-second boundaries.
- Medium: small Anatomy labels and framing reduced phone legibility. Enlarged both;
  preserved the real kit output, readable core labels and the connected air path.
- Medium: tablet split layout narrowed the picture. Tablet now uses the full width.
- Medium: experiment copy and narration repeated the same explanation. Replaced the
  experiment duplicate with an observation cue; narration is an optional disclosure.
- Observed: matched-time switching, block/restore, static frames, Escape, keyboard
  tabs/range, reduced-motion initialization and loaded-page offline playback work.
- Inferred: Manim's closeups are clearer causally and Anatomy's physical construction
  more tangible. No beginner preference, transfer result or owner approval is implied.

Direct-file opening could not be automated because browser policy permits HTTP/HTTPS
only. Loopback HTTP review succeeded. Real phone, VoiceOver, fresh file opening,
independent technical review and five-beginner learning remain unmeasured. BUG-004 open.
