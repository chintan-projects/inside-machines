# Washer CE-1 iteration

Authority: [ADR 0001](../../docs/architecture-decisions/0001-concept-explanation.md),
spec CE-01–18. Revision: `washing-machine-ce-1`. Status: implementation for review.
Person: a curious adult. Question: why wash slowly and spin quickly?
Hypothesis: contrasting lift/drop with fabric following the drum, then tracing water
through holes and pump, lets a beginner explain why spin removes water but does not
replace tumbling. Outcome/transfer: predict poor tumbling if clothes stay at the wall.

Grant: concrete speed contrast before force terminology. Feynman: explain each
physical job before naming it. Veritasium: predict whether faster always cleans
better. Anatomy: keep real drum, motor and pump identifiable; the mechanism inset
does the explanatory work. Model: qualitative front-load washer, no speed threshold,
fabric dynamics, exact drive layout or moisture-removal calculation.

Claim ledger: manufacturer wash/drain/spin sequence and generic part roles; circular
motion reasoning is an explicitly limited inference. Precise locators and source
indices live in the immutable teaching data. Core labels: drum, motor, drain pump.
Prerequisites: lift/drop → perforated drum → collected water and pump → speed's job.
All claims, source support and simplifications await independent technical review.

Storyboard: lift then drop fabric; pass water through drum holes; pump collected
water away; reunite the cycle and compare slow tumbling with fast spin. Graphics
show schematic motion, not measured operating states. Context cutaway is static.
Each beat has a sound-off/static explanation and the same exported vector scene.

Prediction: faster must always clean better. Transfer: if fabric follows the drum
without falling, does that give the same tumbling action? Score 2 requires both
loss of lift/drop and the different water-removal job; right direction alone is 1,
target misconception is 0. The five-beginner spec gate remains unmeasured.

Review: engineering checks, media checkpoints, desktop/tablet/phone, keyboard,
reduced motion, offline/reconnect, technical review and human learning are separate.
No human or family release approval is implied. Highest-priority risk is depicting
spinning in standing water; the orientation cutaway omits the old water/clothes
markers, while the insets explain phase-specific behavior. No paid inference is
needed for authored playback/assessment. Private answers stay on screen only.
