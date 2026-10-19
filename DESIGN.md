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
