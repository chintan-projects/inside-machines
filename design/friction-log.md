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
