# Family alpha implementation

## Active teaching iteration

The next work follows [ADR 0001](architecture-decisions/0001-concept-explanation.md),
the [concept explanation spec](CONCEPT-EXPLANATION-SPEC.md) and the filled
[AC benchmark](../design/lessons/air-conditioner.md). They make Grant, Feynman,
Veritasium and Anatomy part of the build and review contract. Start from the
[lesson worksheet](templates/lesson-iteration.md), implement one complete causal
path, align media, and review engineering, factual truth, craft and learning
separately. Validate AC, then prove reuse with a different mechanism before widening
generation. Existing budgets, privacy and immutable publication rules remain required.

The documents are implemented guidance; the new causal scenes, versioned teaching
contracts and semantic media parity remain planned. Hosted draft publication does
not constitute family-release or benchmark acceptance. Dated implementation notes
below retain historical evidence and limitations.

## Family-alpha scope

The active goal supersedes the fixed-catalog staging in the initial PRD. Deliver a growing shared library, with lookup before generation, both interactive and narrated video output, feedback, private contextual chat, alpha analytics, deployment on Vercel, and an installable PWA. Native clients reuse the API and lesson contract later; building App Store binaries is not the current delivery target.

## Completion evidence

| Requirement | Evidence required |
| --- | --- |
| Family access | Invite/login flow, HttpOnly session isolation, cross-user tests |
| Catalog lookup and aliases | Same mechanism reused across equivalent requests; ambiguity handled |
| Missing-machine creation | Live provider creates a new validated machine lesson, not a canned substitute |
| Shared reuse | A second session requests that machine with no further generation charge |
| Concurrency | Simultaneous requests attach to one job; durable job lease and budget reservation |
| Interactive explanation | Recognizable mechanism, stage timeline, useful controls, source/assumption display |
| Narrated video | Playable video artifact with audible narration, stored and reused |
| Feedback | Persisted thumbs and optional reason, independently stored from review status |
| Clarifying chat | Context-grounded answers; private session ownership; persisted history |
| Usage research | Owner-only demand, reuse, feedback, failures, tokens and dollar ledger |
| Cost control | Configured ceiling, pre-dispatch reservations, bounded attempts, failure settlement |
| PWA | Manifest/icons, cached lesson assets, offline viewing, online-only jobs clearly indicated |
| Vercel | Durable DB/assets, working production URL, deployment smoke tests |
| Mobile path | Versioned lesson/API contract and documented native reuse boundaries |

## Architecture

Use the ancestor workspace's Python FastAPI and React/TypeScript/Vite pattern. Vendor an unmodified snapshot of mandatory shared config, logging, model-gateway, and checkpoint services for portable deployment. Hosted model access plugs into the gateway's existing backend factory rather than changing the shared gateway. Domain data lives in Postgres in production and SQLite locally; shared StateManager provides local operational checkpoints, not a substitute for durable production data.

Generate a bounded declarative scene and lesson schema rather than executable model-produced code. Render interactive and video views from the same scene/animation data. Video encoding runs with a bounded ffmpeg process. Store job phases and results durably so retries continue from a completed phase. Do not run expensive work in an untracked request that reports success before artifacts exist.

Production credentials, a $50 app-AI ceiling and Neon are now configured on the personal Vercel project. Live private-video delivery and chat passed; full generation, generated-artifact reuse and fresh contextual follow-up passed. See LIVE-BENCHMARK.md; human/device release review remains. No mock output may be represented as a completed live generation benchmark.

## Implemented backend evidence — October 19

`backend/app.py` exposes versioned session, catalog, request/job progress, feedback, private chat,
caption/video delivery and owner-report APIs. Authentication stores hashed opaque session tokens,
throttles failed invite attempts and checks same-origin browser mutations. Owner reporting excludes
private conversation text. Model-specific intake explicitly reports its current general-mechanism
scope instead of inventing appliance details.

`backend/pipeline.py` persists separate author, editorial review, per-stage speech and video phases.
A completed paid output is saved atomically with its receipt before advancing, so a worker restart
can reuse it. A crashed request with unknown billing is not automatically paid for again. Interrupted
allowances remain visible in the ledger for reconciliation. Publishing requires both validated
lesson data and its completed narrated MP4. Failed automated editorial checks prevent publication.

Automated tests exercise real SQLite contention, rollback, session revocation, cross-member chat
isolation, idempotent requests/replies, budget settlement, private feedback, HTTP protections,
video byte ranges, provider request/usage parsing, checkpoint recovery and real ffmpeg encoding.
Provider output and audio in these tests are synthetic. These tests do not prove production queue,
Postgres, private Blob delivery or live model availability; those need integration evidence.

The React interface and three authored narrated lessons are now connected locally. Browser checks
prove explicit offline downloads, offline video/captions, account switching and playback-position
restoration. See [verification](VERIFICATION.md) for evidence and its limits. The Linux packaging
check proves that both Python functions, the real queue trigger, shared services, Linux encoder
and versioned CDN shell are included without local credentials or test data.

An actual private Blob write/read/cleanup also passed. Production deployment, deployed private-video
delivery, queue operation and a live provider cost benchmark remain required. Original prototype
screenshots only prove the older visual experiment. A human review of
the family-alpha UI and target-phone behavior is still pending.
