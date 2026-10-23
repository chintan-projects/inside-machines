# ADR 0004: complete core explanations with optional question-driven depth

Date: 2026-10-19. Status: implementation direction authorized by the owner.
Extends ADRs 0001/0003; approves no content release.

A short principle demo is insufficient for a whole-system question. Establish the
input, operation, internal causal relationships and useful output before offering
depth. Each deeper node answers a concrete question, introduces its prerequisites,
uses a useful interaction and returns to the larger system. Creator references
inform craft; explanatory completeness and observed learning govern acceptance.

Introduce a separate `learning-path-1` JSON envelope, leaving published LessonSpec
v1/v2 and old artifacts unchanged. Nodes contain stable lesson references,
questions/outcomes, prerequisite references, next-node edges and reviewed query
aliases. Core, insight and model are roles, not age or ability labels. Prerequisites
are recommendations; learners may inspect any available node. Validate unique IDs,
trusted lesson refs, reachability, earlier prerequisites and acyclic forward edges.
Back navigation belongs to the session, not circular edges in authored data.

The local navigator and player are shared. Topic-specific pure rules and trusted
scene adapters stay separate. Preserve node state/answers in ephemeral mounted
players, pause before switching, retain a return stack, and resume deliberately.
Local question lookup searches only existing node aliases; unsupported questions
must say the branch is absent. It is not an AI chat or a fabricated generated result.

The provider-neutral planner composes trusted concept guidance, completed evidence,
registered target lesson IDs and this same JSON schema. It neither calls a model
nor adds another gateway. A future paid dispatch must use existing reservations,
checkpoint identity, routing and SHA-bound review; replay/branch navigation remain
free. No new production generation endpoint is enabled by this local implementation.
The existing single-lesson prompts also require a complete causal spine at their
declared scope, and recovery fingerprints change with those instructions.

GPU-S3 is the first local consumer; a second-topic fixture checks structural reuse.
That fixture proves no domain teaching quality. Production adoption still needs
artifact resolution, graph-level review, native/API integration and release gates.
