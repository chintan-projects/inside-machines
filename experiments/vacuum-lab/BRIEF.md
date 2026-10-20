# Vacuum visual production comparison

Status: local experiment; no production publication or quality acceptance.

Person: a curious person aged roughly 8–80 who wants a satisfying answer, not a course.
Job: understand why moving air can pick up dirt, then compare four ways of showing it.
Posture: calm, tactile, plainspoken.
References: Anatomy’s connected, shaded physical parts; Manim’s use of a changing picture as an argument.
Avoid: the existing small schematic surrounded by controls and terminology. Enlarging its container alone does not improve the explanation.

## One question and one hypothesis

“What actually picks up the dirt?” After a roughly 45-second explanation, a beginner can
connect powered fan → moving air → dirt transport → separation, and predict why an
airtight blocked inlet stops continuous pickup despite a turning fan. The hypothesis
fails if a learner merely names the parts or attributes pickup to motor noise alone.

Compare actual Anatomy, Manim Community, Motion Canvas and Remotion output authored
by the same OpenAI Codex interactive coding session. The repeated Motion Canvas in
the request is interpreted as Remotion for the fourth candidate. No external model
API dispatch, token accounting comparison or autonomous-generation claim is implied.
Human-directed coding, documentation reading and repairs are part of this spike.

## Tenets

- Finish the useful answer in under a minute; put extra physics behind an invitation.
- Show three working jobs before adding component vocabulary.
- Keep the object recognizable, but let a simpler picture win if it explains more.
- Ask once, demonstrate once, let the learner leave satisfied.
- Prefer a readable static picture to motion the learner cannot follow.

## Visual system

- Inspection paper `#fbfcfe`: a neutral ground for drawings, not a decorative theme.
- Graphite `#172432`: high-contrast labels and fine physical edges.
- Air `#4267d5`: a semantic path and direction, never a pressure measurement.
- Dirt `#78513b`: distinct solid specks, not another species of air marker.
- Hairline `#dce2e9`: divide controls without enclosing every paragraph in a card.
- System sans, 18px body, short line lengths: familiar letterforms, zero font download.
- Broad figure, compact header, four wrapping selectors: the explanation owns the screen.
- No autoplay, no ambient motion, no required prediction. Motion begins on Play.

## Claim ledger and limits

| ID | Claim | Evidence and locator | Scope / review |
| --- | --- | --- | --- |
| V1 | A powered fan moves air; lower pressure inside permits surrounding air to enter | Dyson vacuum FAQ, “How do vacuums work?” https://www.dyson.com/vacuum-cleaners.asp | Generic mechanism; independent technical review pending |
| V2 | Moving air carries loose dirt through a connected inlet path | Same FAQ, low-pressure intake and dirt collection description | Qualitative; not every adhered particle is picked up |
| V3 | A porous bag separates some dirt while permitting air through its material | Dyson “It started with a cyclone”, https://www.dyson.com/discover/innovation/behind-the-invention/filtration-at-dyson | Bagged cleaner only; no complete-filtration or HEPA claim |
| V4 | An ideally airtight blocked inlet prevents sustained incoming throughflow although the fan may turn | Inference from V1/V2 and mass continuity | Idealized steady condition; leaks, bypasses and real appliance protection omitted |
| V5 | Current and magnetic forces can produce torque that turns a motor shaft | OpenStax Physics 20.2, “Electric Motors, Generators, and Transformers”, first two paragraphs; https://openstax.org/books/physics/pages/20-2-motors-generators-and-transformers | Optional prerequisite; generic electromagnetic motor principle, not a specific motor design; independent review pending |

Existing manufacturer evidence was reused from the CE-5 record. Never run a real
cleaner with an obstructed inlet for this experiment. The control changes a drawing.
Rotations and markers are slowed illustrative encodings, not measured motion or flow.

## Storyboard / CE trace

Teaching anchors: Grant's visual reasoning motivates the independent working closeups;
Feynman's job-first language keeps the initial answer short and puts prerequisite physics
behind an invitation; Veritasium's prediction/misconception approach motivates the sealed
inlet and kinked-hose transfer; Anatomy supplies connected, shaded physical construction.
These are our design choices, not creator endorsements. No kit geometry audit is claimed.

| Beat | Input / working focus / output | Visible argument | CE |
| --- | --- | --- | --- |
| Fan | Electricity / motor and fan / moving air | Connected shaft turns; air continues toward outlet | 03–07 |
| Inlet | Room air and loose dirt / nozzle and hose / transported dirt | Air and dirt enter the same connected path | 04–07 |
| Bag | Dirt-bearing air / porous bag / retained dirt and continuing air | Air crosses bag material; retained dirt does not reach the fan | 04–07 |
| Together | Same operating machine / all three jobs / continuous pickup | One complete path; chapter sequence is attention, not startup order | 08, 11, 18 |

Prediction (skippable): with an airtight blocked inlet and a turning fan, can fresh
dirt keep entering? Demonstration uses the same state for every renderer. Transfer:
the bag is clear, but the hose is kinked shut; does a running motor ensure pickup?
Rubric: 0 = yes/no without a correct mechanism; 1 = less air/no pickup but no cause;
2 = the path is blocked, so there is no sustained throughflow to carry fresh dirt.

One shared storyboard and typed/pure qualitative state feed trusted local adapters.
This is authored code executed locally, not a newly enabled production code-generation
capability. Old lesson artifacts, published revisions and private history are untouched.
Static checkpoints and text remain available without playback. A single self-contained
HTML embeds real rendered media. Browser feedback remains local and is exported only
on request. CE-12/15 technical and learner gates remain pending.

## Review and release

Compare matched narration, duration, claims and conditions. Record actual tool versions,
prompt/source hashes, renders and limitations. Perform three critique rounds at 390,
768 and 1280 pixels, inspect encoded frames, test seek/switch/block/reset, keyboard,
sound-off, reduced motion, missing storage and offline file loading.

Engineering, source inspection and agent craft review are separate from independent
technical review, a real-phone owner walk and five beginner teach-back/transfer results.
This local comparison does not release a new family lesson. Owner preference and
beginner evidence are needed before selecting a production default.
