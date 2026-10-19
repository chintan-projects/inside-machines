# ADR 0001: Build explanations around a testable mental model

Date: 2026-10-19  
Status: Accepted teaching and architecture direction; implementation is partial.  
Decision owner: Chintan. The owner agreed to the teaching interpretation and asked
that it govern subsequent implementation and iteration. This accepts the direction,
not the current lesson's scientific correctness, craft or release readiness.

## Context

Inside must help a curious beginner explain why a machine works and predict a
related situation. The owner rejected the AC presentation twice: first for missing
labels and confusing stages, then for ordinary craft and insufficient intuition.
Adding information and improving the drawing did not establish understanding.

The current AC studio has an authored isometric cutaway, six chapters, persistent
core labels, narration and a same-room experiment. Much of the mechanism remains
in text; the compressor interior is not demonstrated. The experiment selects
qualitative outcomes. Its drawing and the stored MP4 diverge. Other machines use
the older renderer. Existing structural validation and model review cannot certify
scientific accuracy, explanatory craft or learning.

## Decision

Treat a lesson as a designed path from a question to an independently usable mental
model. Use this teaching progression, adapting its length to the concept:

**Question → prediction → observation → causal explanation → whole system → transfer.**

Break complexity into dependencies a beginner can follow. Each chunk establishes
one relationship needed by a later chunk. Reassemble those relationships explicitly.
The sequence describes attention, not necessarily the machine's operating order.

The following influences have distinct jobs. The requirements in this ADR and its
spec are our product synthesis, not a framework endorsed by these creators.

| Influence | Decision for Inside | Review question |
| --- | --- | --- |
| Grant Sanderson / 3Blue1Brown | Begin with a concrete problem; build visual intuition before abstraction. Every movement and the accompanying words express the same relationship. | What does this visual let a beginner understand that the words alone did not? |
| Richard Feynman | Use plain, mechanistic explanations; expose missing prerequisite ideas and declare the limits of the simplified model. Introduce a technical name after establishing its job. | Can the learner explain the cause in ordinary language, including where the model stops applying? |
| Derek Muller / Veritasium | Elicit a prediction, address a plausible misconception through evidence, and let the result motivate the explanation. Permit skipping the prediction. | What belief could this observation change, and what reasoning demonstrates the change? |
| Anatomy | Make the recognizable physical object carry the explanation: purposeful parts, real connections, volume, readable depth and motion/readouts derived from the model. | Can the learner locate the working part and follow what physically happens? |

### Priority when principles conflict

1. Factual truth and honest scope.
2. Causal legibility and accessibility at the actual viewing size.
3. Interaction and narrative that build and test understanding.
4. Mechanical craft and polish that support those goals.

Preserve Anatomy's purposeful detail and physical coherence. Reveal subordinate
detail through focus or inspection when it obscures the causal mechanism. Part
count alone is never a learning metric. This project explicitly requires anchored
core labels, semantic flow cues and user-initiated motion; these override the
upstream skill's minimal-label and idle-tour preferences. Geometry audit claims
require the actual applicable audit; our custom SVG does not inherit kit proofs.

## Architecture direction

Separate these responsibilities behind a versioned lesson package:

| Module | Owns | Must not own |
| --- | --- | --- |
| Mechanism model | Components and connections, material/energy transfers, supported scenarios, state transitions, invariants, claims and assumptions | Provider protocols or UI layout |
| Teaching storyboard | Question, prerequisite order, misconception, prediction, focal mechanism, plain-language explanation and transfer rubric | An independent copy of the physical rules |
| Trusted renderer adapters | Geometry, visual encoding, camera/focus and accessible interaction for a supported mechanism family | Arbitrary executable model output or invented physics |
| Playback and artifact adapters | Chapter/state synchronization, narration, captions, static alternative, interactive and video output | Separate causal outcomes for different media |
| Evaluation record | Lesson/revision/spec identifiers, factual review, observed friction, teach-back and transfer results, release decision | Public reuse of private chat or learner answers |

The same authoritative mechanism and storyboard must drive all supported media.
Pixel-identical output is unnecessary; consistent claims, states, chapter meaning
and outcomes are required. Existing API and lesson versions remain compatible.
Introduce new typed fields through an explicit migration, not by silently changing
the meaning of saved stages or personal progress. Keep provider adapters, shared
services, atomic budgets and immutable publication behavior intact.

A declarative, reviewed qualitative scenario is valid when labeled. A numerical
simulation requires supported parameters, units, equations, limits and invariant
tests. Appearance and animated dots do not establish either accuracy or simulation.

## Execution and acceptance

The normative [concept explanation spec](../CONCEPT-EXPLANATION-SPEC.md) translates
this decision into requirements and evidence. Start each iteration from the
[lesson worksheet](../templates/lesson-iteration.md). The first filled specification
is the [AC benchmark](../../design/lessons/air-conditioner.md).

Work in bounded iterations:

1. State one learner outcome and a falsifiable learning hypothesis.
2. Establish facts, model limits, dependencies and the assessment rubric.
3. Storyboard the causal changes and static equivalents before geometry or prompts.
4. Implement one complete question-to-transfer path with shared state.
5. Run engineering, factual, visual/accessibility and beginner-learning reviews as
   separate checks. Record missing evidence explicitly.
6. Fix the highest-impact failure, repeat the affected checks and record the owner's
   decision. Preserve the previous revision and its private history.

Existing `backend.quality` checks continue before review, after review and before
publication. They are the automated floor. New semantic requirements start as
explicit human review criteria until their typed contracts/checks are implemented.
Do not represent this documentation change as an updated authoring prompt or gate.

Before family release, require technical review of the mechanism, an owner walk on
a real phone, and the beginner evaluation in the spec. A rejection produces the next
bounded hypothesis; it does not justify another self-awarded quality score.

## Adoption sequence

1. **Document the contract:** this ADR, spec, worksheet and AC acceptance scenarios.
2. **Build the AC vertical slice:** causal scenes, prediction, recombination and
   transfer; bring narration/video/static output into semantic agreement.
3. **Validate it:** technical review, device/craft review and beginner learning;
   iterate before calling it the approved benchmark.
4. **Prove reuse:** apply the contract to a second, different mechanism, using the
   washer as the candidate. Share genuine primitives without forcing one storyboard.
5. **Extend generation:** version the data/prompt contracts, validate safe outputs,
   evaluate authoring/review providers on identical cases, and label unsupported or
   unapproved output as draft. Never expand paid calls implicitly.

The order limits premature infrastructure work. Existing hosted drafts remain
drafts; acceptance of this ADR does not upgrade them or open family access.

## Alternatives and consequences

| Alternative | Decision |
| --- | --- |
| Continue polishing independent chapter drawings | Insufficient: does not ensure a causal explanation or cross-media agreement. |
| Ask a frontier model to imitate a creator's style | Insufficient: no reproducible teaching contract, scientific assurance or provider-independent evaluation. |
| Build a universal simulator before one lesson works | Deferred: broad physics and geometry would hide the current learning problem behind infrastructure. |
| Author every lesson as unrelated bespoke code | Useful for a spike, unsuitable as the catalog contract; shared mechanisms and assessment structure must be extracted after validation. |

This decision increases storyboard and review effort and may slow catalog growth.
It favors reviewed reusable explanations, useful offline playback and measured
understanding. Video parity and safe schema migration are real implementation work.
It does not require Manim, a particular model provider, photorealism or native apps.

Keep this decision stable once implementation begins. Record a successor ADR for
changes to its core direction. Revise lesson specs and iteration records as evidence
arrives; include the version and reason in each result.

## Sources and relationship to existing guides

- [Grant Sanderson's teaching guidance](https://www.3blue1brown.com/about/), FAQ
  “I'd like to start making math videos online”: concrete examples, purposeful
  motion and coordinated words/visuals. Primary guidance, not a learning trial.
- [Feynman, Atoms in Motion](https://www.feynmanlectures.caltech.edu/I_01.html),
  especially sections 1–2 and 1–3: a physical picture used to explain familiar
  phenomena, with explicit schematic limitations. Our teaching interpretation;
  no attribution of an internet “Feynman technique” checklist.
- [Muller, Bewes, Sharma and Reimann, Saying the wrong thing](https://onlinelibrary.wiley.com/doi/10.1111/j.1365-2729.2007.00248.x):
  misconception/refutation and dialogue treatments improved learning relative to
  exposition in a study of 364 first-year physics students. This motivates our
  hypothesis; it does not establish effectiveness for household-machine lessons.
- [Pinned Anatomy skill](../../vendor/anatomy/SKILL.md): physical coherence and craft;
  source remains unmodified with its license. Our label/motion overrides are above.
- [Product brief](../../BRIEF.md), [design direction](../../DESIGN.md) and
  [quality bar](../QUALITY-BAR.md) retain their roles. The spec governs concept
  explanation; the quality bar also governs reliability and release evidence.
