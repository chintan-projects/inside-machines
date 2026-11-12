# Local explanation workflow verification

Observed on 2026-11-11 for Inside Explain 1.0.3. This records the local authoring
integration in ADR 0009; it does not accept a lesson or change live publication.

| Check | Observed result |
| --- | --- |
| Shared skill installation | Claude Code and Codex resolve to the canonical repository skill; previous installations were backed up outside discovery roots |
| Native plugin installation | Both hosts installed 1.0.3; every packaged file matched the repository source |
| Skill validation | The skill-creator validator passed |
| Claude manifest/catalog | Strict validation passed; optional directory icon warning remains |
| Local project and ZIP tests | 10 passed: existing-work preservation, coherent continuation state, path boundaries, literal topic handling, zero-paid-speech defaults and allowlisted release contents |
| Studio dependencies | Studio 1.3.0 reported all required dependencies ready, including ManimGL 1.7.2 and the free Samantha voice |
| New video scaffold | Passed Studio plan validation and resolves the shared claim ledger; the initial empty-source defect was corrected |
| Editable video example | Plan and script validation passed: one episode, six scenes, 75 beats; nine Python source files parsed |
| Backend | Ruff and strict mypy passed; pytest: 390 passed, 10 skipped; coverage 89.77% |
| Frontend | Type checking, lint, all 51 JavaScript tests and production build passed |
| Linux deployment packaging | Linux amd64 image, sanitized build and output verifier passed; API, queue, shared services, Linux media dependencies and CDN assets were verified |
| Upload policy | All five local authoring/draft input examples were excluded; the required native artwork remained included |
| Clean distribution | The allowlisted plugin ZIP was built locally; no media, transcripts, account files or credentials are included |

The ten skipped backend cases require an explicitly configured disposable
Postgres database. Transactions were not changed in this iteration. No fresh
paid model generation or paid speech was invoked. The earlier rendered video and
its unresolved review findings are recorded in the
[example](../experiments/prefill-decode-video/README.md).

The final output audit found that the local packaging harness initially copied
the source-only example without applying upload exclusions. The harness now uses
the shared upload-rule checker, and the output verifier rejects local authoring
inputs in either packaged function. This does not change production app routes.

The personal Gmail Vercel identity, owner membership, project, Neon and private
Blob ownership were checked before the push. The app had no Git repository link;
this implementation does not establish automatic deployment. No Vercel deployment,
provider change, environment change or public directory submission was requested
or performed as part of this integration.

Native installation and deterministic tests are engineering evidence. A new
host-model routing/quality evaluation, uncoached continuation test, real-device
accessibility review and learner-transfer study were not run. Instructions cannot
grant execution capabilities to chat-only sessions, and local installation does
not publish a universal ChatGPT web/mobile listing.
