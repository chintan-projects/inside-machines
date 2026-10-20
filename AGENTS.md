# Inside Machines engineering contract

Inherit `/Users/chintan/Projects/AGENTS.md`. This file adds enforceable project
conventions for all contributors and coding agents. Do not duplicate the shared
model gateway, configuration loader, logger or state manager.

## Architecture principles

1. **Reusability:** share lesson schemas, rendering primitives and API contracts.
   Web/PWA and future native clients consume the same versioned API and artifacts.
2. **Modularity:** API handlers handle transport; domain modules handle rules;
   provider/storage/queue adapters handle integrations. Keep provider SDK details
   out of domain, chat and pipeline modules. Keep files below 600 lines.
3. **Extensibility:** register trusted provider adapters at startup through
   `ProviderRegistry` and the shared gateway's `ModelBackend` protocol. Route
   research, authoring, review, chat and speech explicitly. Declare supported tasks and reject
   incompatible routes before serving. Do not load arbitrary plugin code or accept
   provider endpoints/credentials from clients. A registry is sufficient for now;
   do not introduce a plugin framework without a concrete need.
4. **Robustness:** preserve atomic budget reservations, idempotency, phase
   checkpoints and uncertain-billing handling across every adapter. Fail closed.
   Never silently retry a paid call or fall back to another provider. A timeout
   does not prove cancellation or zero billing. Never fabricate successful output.
5. **Observability:** use the shared structured logger. Record task, route,
   duration, failure type and the existing operation/job usage ledger. Receipts
   retain actual model identity, token counts and cost/estimate distinctions.
   Never log credentials, prompts, private chats or raw provider error bodies.
   Local logging is implemented; a hosted monitoring dashboard is not implied.
6. **Consistency:** use typed Python contracts and strict TypeScript interfaces,
   validate external data at boundaries, and follow established API errors and
   frontend loading/empty/error/offline states. Do not maintain duplicate business
   rules in UI components.

## Adding a model provider

- Implement `ModelBackend` behind the shared gateway; register a `ProviderPlugin`
  and explicit `TaskRoute` entries in trusted startup composition.
- Own credentials, protocol translation, structured-output handling, refusals,
  usage receipts and bounded network calls inside the adapter.
- Set and validate model-specific rates, task token limits and sufficient phase
  reservations before enabling a different model. Current default rates and the
  `OPENAI_API_KEY` readiness gate describe only the OpenAI deployment. A new
  registry entry alone does not make another provider production-ready.
- Research is a separately routed OpenAI adapter capability with a persisted evidence
  checkpoint. Configure a retrieval-capable research route before authoring; another
  adapter must implement equivalent retrieval or reject that task. Authoring and review
  consume that checkpoint and cannot add unseen source URLs. Never quietly omit evidence.
  Speech is also a separate capability.
- Add adapter contract tests for success, malformed/refused/incomplete output,
  timeout, quota failure and usage accounting. Add routing tests for task isolation.
- Run the same product evaluation cases before claiming comparable quality or
  switching defaults. Engineering tests do not establish factual/visual quality.

## Required verification before commits

```sh
.venv/bin/ruff check backend main.py tests
.venv/bin/mypy --strict backend main.py tests/backend
.venv/bin/pytest
npm run check:types
npm run lint
npm test
```

Maintain at least 80% backend coverage. Use the disposable Postgres regression
suite when modifying transactions. Run `npm run build` for frontend changes and
the Linux deployment packaging verifier for deployment changes. Record skipped
external checks honestly. Keep `PROGRESS.yaml` below 50 lines.

Secrets, local data, screenshots and generated artifacts stay ignored. Git pushes
on the linked main branch may trigger Vercel builds; verify readiness first and
report deployment failures rather than implying a successful release.

## Deployment identity contract

Use the owner's verified personal Gmail Vercel identity. A personal-looking
workspace name does not establish account ownership. Before linking, pushing or
deploying, verify the authenticated account's primary email, destination scope
ownership and connected Neon/Blob ownership against the approved destination.
The current source Hobby scope uses the work-email identity; hold further pushes
and deployments until the migration in `docs/DEPLOYMENT-OWNERSHIP.md` is resolved.
Preserve data, environment configuration and protection during that correction;
granting viewer access or changing the work account's email does not complete it.

## Learning publication contract

Before changing lesson content, authoring/review prompts, mechanism state,
renderers or assessments, read and follow
[ADR 0001](docs/architecture-decisions/0001-concept-explanation.md) and the
[concept explanation spec](docs/CONCEPT-EXPLANATION-SPEC.md). Keep Grant Sanderson's
visual reasoning, Feynman's plain causal explanations, Veritasium's prediction and
misconception work, and [Anatomy's physical craft](vendor/anatomy/SKILL.md) explicit
in the lesson's design choices. These are build/review requirements, not stylistic
name-dropping or a claim of creator endorsement.

Start each lesson iteration with the
[worksheet](docs/templates/lesson-iteration.md), a claim ledger, one falsifiable
learning hypothesis and a transfer rubric. The
[AC benchmark](design/lessons/air-conditioner.md) is the first build spec. Trace
changes and evidence to CE requirement IDs. Keep causal rules out of UI/rendering
adapters; align interactive, narration, captions, video and static outputs through
the same versioned mechanism/storyboard. Preserve old revisions and stage meaning.

Review engineering, technical truth, craft/accessibility and beginner learning
separately. Record observed versus inferred results and missing evidence in the
lesson record, friction log and journal. Iterate on the most consequential failure;
do not promote other machines or generated drafts based on AC-only evidence.
Documentation, structural checks and model review do not implement or satisfy the
new semantic gates by themselves. Owner agreement to the ADR is not lesson release
approval. The ADR records the project's label/motion overrides to Anatomy.

Apply `backend.quality` before review, after review and before publication. Every
core component needs an on-scene label; every chapter needs a labeled focus,
input/output and evidence. Preserve immutable published revisions and private
conversations when replacing a lesson. Read `docs/QUALITY-BAR.md`; structural tests
and automated model review never imply factual certification or human UI approval.

Causal insets render independently from the full-machine locator. Each must include
its own labeled working mechanism and physical surroundings; floating unlabeled
symbols at whole-machine coordinates fail review. New editorial calls return a
SHA-bound verdict, not a regenerated copy; rejection or mismatched hash must stop
publication. Saved draft recovery requires an explicit owner operation and the
current source/quality gates; it cannot bypass an editorial rejection.
