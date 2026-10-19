# Action-led learning: October 19 redesign

The owner rejected the labeled AC revision as ordinary and supplied
[Visual Learning's microwave](https://visual-learning.app/microwave). Adding labels
had addressed an identification failure without resolving the learning experience.

## What was observed

In Chrome, the reference opens on a recognizable, detailed cutaway. Its manual
steps place chocolate, heat it and reveal a measurement. The instruction stays
beside the machine, and available actions establish what to do next. The stated
turntable experiment supplies a reason to care about the mechanism. Its strongest
move is a concrete action followed by a visible consequence. This is our analysis,
not a claim about the creator's intent or measured learning outcomes.

Our previous screen presented a schematic, chapter tabs, playback, two state
cards, explanatory paragraphs, component choices and a prediction together. A
beginner had to decide where to look and assemble the causal story independently.
It made the information available but did not guide attention sufficiently.

## The new AC experience

One question leads: where does the room's heat go? A short ordered story introduces
the two sides, heat pickup, compression, heat rejection and expansion, then asks
what happens if both units share a sealed room. The experiment changes the same
scene's enclosure, heat paths and outcome. It represents an idealized enclosure
change, not an installation animation or a numerical temperature simulation.

The drawing is original isometric SVG with purposeful fins, coils, mounts,
compressor housing, fan guard, electrical compartment and connected tubing.
Component labels remain visible; selecting one opens its corresponding explanation.
Phone steps focus the relevant component, with a whole-system alternative.

Text, direction cues and the outcome remain usable with reduced motion. The
existing narration follows the live SVG chapters. It is deliberately opt-in.
Sources, detailed states, comprehension questions, feedback and private chat sit
after the primary experience. No new paid model calls are needed for this revision.

## Engineering and scope

- The AC renderer is an authored adapter in `web/ac`, selected for the existing
  AC lesson. It does not execute model-generated code. Other machines retain
  their existing renderer and draft status.
- Geometry, reusable drawing primitives, story, interaction, outcome and styles
  are separate modules. Standard and AC lessons share discussion, download and
  media storage handling. Timeline rules are shared independently of rendering.
- The stored lesson, private conversations and immutable MP4 have not been
  rewritten. The new live visual uses that media's audio track. A standalone MP4
  exported through the existing API still contains the earlier schematic; the
  server renderer has not gained this new isometric geometry.
- Supporting similarly crafted arbitrary machines requires additional renderer
  families or a richer safe geometry contract, followed by visual evaluation.
  This example does not establish automatic high-quality 3D generation.

## Proposed learning test

Give five beginners the AC link without coaching. After at most two minutes, ask
whether room air travels outdoors, where heat is released, and what happens with
both units in the same sealed room. Ask them to point to the compressor and say
why it is needed. A proposed acceptance threshold is four people correctly
explaining both the air separation and the sealed-room prediction. This result
has not been measured. Interface checks are not learning-efficacy evidence.

## Verification scope

Desktop, 768px tablet, 375px phone and 320px phone inspected in Chrome. Main labels
measured 13.3px on the tablet and 14.5px in the smallest overview; focused phone
components are larger. Keyboard component inspection, chapter/narration agreement,
loading/cancellation handling and zero active diagram animations under reduced
motion were checked. Real iOS/Safari and a human walkthrough remain outstanding.

Strict TypeScript, frontend lint, production build and seven JS regression
tests pass, including a regression for stale canceled-media events. Backend remains unchanged: 84 tests pass with 85.03% coverage; the two
disposable-Postgres tests were skipped in this revision, having passed previously.
No transaction code changed. These checks do not certify the design's taste.
