# ADR 0002: checkpoint evidence before scene authoring

Status: implemented for a protected evaluation; runtime acceptance remains separate.
Date: 2026-10-19. Complements [ADR 0001](0001-concept-explanation.md).

## Problem and evidence

The first live CE-1 vacuum revision combined web research and a large typed visual
artifact in one call. It exceeded the existing 210-second provider deadline.
The job failed, published nothing and retained $0.65 for unknown billing. This is
not a measured zero-cost failure or a successful CE-1 generation benchmark.

## Decision

Separate the work into durable research → author → review → voice → video phases.
Research has its own registry task, small typed evidence schema and 2,500-token
limit. The existing OpenAI adapter retrieves primary-source evidence. Authoring
and review consume that checkpoint, perform no new search and cannot introduce
source URLs outside it. Source presence is not source entailment or expert approval.
Each phase retains its own existing paid-operation receipt, lease and checkpoint.

Research reserves $0.30, author/review $0.65 each and up to seven speech phases
$0.05 each: $1.95 fits the existing $2 admission reservation. Validate these bounds
and model-specific rates at startup. The $50 total ceiling is unchanged. There is
no automatic paid retry, provider fallback or invented completed output. A failed
attempt remains in the ledger and evaluation denominator. Unknown billing remains
retained until reconciled using provider evidence.

This extends application task routing; it does not change the shared gateway's
ModelBackend protocol or duplicate its services. All adapters are trusted startup
registrations. Another research route must declare retrieval support. A lesson
source ledger remains a draft until its separate human technical review.

## Migration and verification

New jobs carry `pipeline_version=evidence-first-1`. Old terminal job progress keeps
its combined research/build meaning. An already-paid pre-split author output is
resumed without a new research call. Interrupted unknown calls still fail closed.
Lesson spec/video identities, member history and the existing v1 reader remain
unchanged. No paid phase was redeployed while the first attempt was in flight.

Contract tests cover research routing/limits, malformed evidence stopping authoring,
source-boundary enforcement, paid-output migration and full real-MP4 publication.
Evaluation packets can export terminal failed jobs without prompts, private outputs
or fake artifacts. A new explicit production operation must demonstrate the split
path; engineering tests alone do not establish runtime reliability or teaching quality.
