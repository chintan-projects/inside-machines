---
version: alpha
name: Inside
description: Everyday machine mechanisms for adults with a concrete question
colors:
  ground: "#F7F8FA"
  surface: "#FFFFFF"
  ink: "#17232D"
  muted: "#52616D"
  accent: "#006D7C"
typography:
  display: { fontFamily: "SF Pro Display, system-ui", fontWeight: 600, letterSpacing: "-0.02em" }
  body: { fontFamily: "SF Pro Text, system-ui", fontSize: "17px", lineHeight: 1.5 }
  mono: { fontFamily: "SF Mono, ui-monospace" }
spacing:
  base: 4px
rounded:
  input: 8px
  card: 8px
  surface: 12px
---

# Inside design direction

## Concept explanation contract

[ADR 0001](docs/architecture-decisions/0001-concept-explanation.md) and the
[concept explanation spec](docs/CONCEPT-EXPLANATION-SPEC.md) govern the teaching
experience. Keep these four anchors visible in every lesson worksheet:

- Grant: concrete questions, visual intuition and purposeful synchronized motion.
- Feynman: plain causal mechanisms, prerequisite bridges and honest model limits.
- Veritasium: a prediction, a plausible misconception and an explanatory payoff.
- Anatomy: a recognizable object with purposeful physical detail and model-linked behavior.

Prioritize truth, causal legibility/accessibility, teaching interaction, then polish.
Retain core labels and opt-in motion under the project's Anatomy overrides. Review
the whole system after isolated mechanisms. Use
[the worksheet](docs/templates/lesson-iteration.md) and the
[AC build spec](design/lessons/air-conditioner.md); engineering passes do not establish
human craft approval or learner understanding.

## Existing visual direction

The React family-alpha interface now uses these tokens; the original visual lab remains separate. Posture: calm, precise, hands-on. Person: an adult with a machine question. Job: connect an action to its consequence. References: Ciechanowski's adjacent controls and Tinybop's manipulable mechanisms. Direct lesson entry begins with the mechanism and its controls.

## Ranked tenets

1. Show the mechanism before personal setup.
2. Simplify peripheral detail for a legible causal part.
3. Preserve authored learning without runtime AI.
4. Annotate evidence without implying exact geometry.
5. Make new paid work explicit; allow free repeat playback.

## Color and typography

Use a neutral instrument-panel ground so machine materials and highlighted flows carry meaning. This replaces the prototype's cream/serif presentation as a default direction. Teal identifies the primary action and selection. Water, heat, and electricity may use separate semantic colors only with labels and non-color cues. Do not use action color to imply verified evidence. Check actual contrast in implementation.

System type supports native legibility and larger-text behavior. Use compact headings rather than a tall marketing title. Body starts at 17 points on iOS; helper text remains readable. Tabular numbers use the mono token only for measurements. Scene labels become a readable part panel when space is constrained.

## Layout and shapes

The object and a useful control occupy the first lesson viewport. Stage controls remain within reach without covering the relevant part. Text and evidence follow in progressive detail. Use 44-point minimum touch targets. Border and tone distinguish structure; one soft shadow is reserved for transient overlays. Radius follows role, not a universal pill style.

## Controls and motion

Every control has ready, focus, active, disabled, waiting, and error behavior. Focus is visible; selected states include text or shape changes. Sliders expose value, units, range, and a reset. Changes explain the consequence and do not silently alter factual parameters.

UI transitions use 150–250 ms opacity/transform effects only where orientation benefits. Mechanism animation follows the model with labeled time/speed scaling. Reduced motion uses still stages; full playback is opt-in. The signature interaction is changing one causal variable and seeing the same state update in the mechanism and explanation.

## Quality checks

Do show the actual object, preserve useful static explanations, and place assumptions beside affected claims. Do not put a paywall before the first causal answer, scatter decorative motion, or turn parts into identical promotional cards. Review phone, tablet, and desktop layouts, then walk the core journeys on real hardware. Utility and usability must pass before decorative polish.

## Action-led AC studio

- Teach one change at a time; move component detail behind an explicit inspection.
- Keep the real object large enough to recognize before reading the explanation.
- Use a physical counterexample to earn the abstract energy-balance explanation.
- Mechanical detail belongs to fins, housings, mounts and tubing; UI chrome recedes.
- Keep labels; fewer surrounding panels must not make identification harder.

The studio uses a chalk drawing ground (#F3F2EE) to separate the physical object
from the app's white controls; dark graphite (#29383D) gives fine outlines weight.
Teal (#286E75) is reserved for the active action/cold side, copper (#BC7954) for
actual tubing, and orange (#D47444) for escaping heat. These colors encode roles,
paired with names, arrowheads and dashed heat paths. Inter remains the shared
legible drawing font. A compact 30px question replaces the large lesson title;
step titles are 15px; body copy stays 16–17px. Desktop figure proportions are
roughly 4:3; mobile uses a separate stacked arrangement with its next action close.

Genericness check: a neutral dashboard with a larger SVG would repeat the rejected
solution. The distinctive move is the room experiment changing the same physical
scene and its energy outcome, with a six-action story supplying the orientation.

### 2026-10-19 vacuum rejection: a focused workbench

The owner's phone screenshot rejected the small box-like locator and oversized
control stack. The causal detail now comes first, with one adjacent action and a
secondary expandable whole-system locator. The last step opens the whole-system
locator to reconnect the parts. This shared structure applies to other domains.

White (#FFFFFF) keeps attention on the object. A cool inspection surface (#F6F9FC)
distinguishes the cut face from the page. Graphite (#202D3B) carries explanation;
blue (#2676DF) marks directional airflow and brown (#C5823C) marks retained dirt,
with arrow versus particle shape so color is never the only signal. Blue controls
(#225BDF) identify the single next action. This replaces the rejected cream/sage
stack; changing color alone is not the craft improvement.

Trusted, original section artwork supplies curved shells, recesses, material
shading, couplings, fins, screws and texture on real surfaces. The lesson still
owns the same safe poses, paths, labels and qualitative outcomes. The asset set is
SHA-bound to the new revision; historical drawings/videos retain their identity.
The generic player does not gain vacuum-specific interaction rules.
