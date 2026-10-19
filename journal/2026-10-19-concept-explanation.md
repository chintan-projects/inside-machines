# Concept explanation contract adopted

Owner decision: agreed to building causal mental models with Grant Sanderson's
visual reasoning, Feynman's simplicity and Veritasium's misconception work, alongside
the existing Anatomy craft foundation. Requested a durable ADR/spec and structured
iteration. This accepts the teaching direction, not a lesson or family release.

Response: [ADR 0001](../docs/architecture-decisions/0001-concept-explanation.md),
[concept explanation spec](../docs/CONCEPT-EXPLANATION-SPEC.md), a reusable
[worksheet](../docs/templates/lesson-iteration.md) and a filled
[AC benchmark plan](../design/lessons/air-conditioner.md). Linked from engineering,
product, design, build and release guides. Runtime code and deployed behavior are
unchanged by this documentation revision.

Prediction: a storyboard specifying the prerequisite, input, causal change, output,
visible evidence and transfer rubric will expose teaching gaps before geometry and
prompt work. The next AC iteration tests that prediction through beginner
teach-back and a refrigerator transfer task, with technical/craft reviews separate.

Learning results remain unmeasured. Current video/interactive parity, independent
technical review and real-phone owner review remain incomplete. The next iteration
must record observed failures and change the most consequential one; this document
does not close BUG-004 or promote other catalog drafts.

Documentation verification: local links and CE-01–18 identifiers checked; file and
progress limits pass. Existing required checks pass: Ruff, strict mypy/TypeScript,
frontend lint, seven JS tests and 84 backend tests at 85.03% coverage. Two disposable
Postgres tests skipped; no transaction or runtime code changed. No frontend build,
deployment packaging, device or learning test was needed/performed for these docs.
