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
   authoring, review, chat and speech explicitly. Declare supported tasks and reject
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
- Research is currently an OpenAI adapter capability. Another authoring adapter
  must explicitly implement equivalent evidence retrieval or reject that task;
  never quietly omit source gathering. Speech is a separate capability.
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
