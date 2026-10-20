# Claude authoring route

The hosted authoring pipeline supports a trusted Claude Messages adapter through
the existing model gateway. This is separate from the local HTML/art experiment:
it returns structured lesson data for the shared renderer, never executable model
code. It does not establish comparable technical or visual quality by itself.

Set `INSIDE_AUTHORING_PROVIDER=anthropic` and the server-only
`ANTHROPIC_API_KEY` to select this route explicitly. Keep `OPENAI_API_KEY`: research,
editorial review, private chat and speech retain their separate OpenAI routes.
No customer request can supply a provider, model, endpoint or credential. The
default remains `openai` until the owner explicitly selects the new route.

The verified production tuple is `claude-sonnet-5-5`, $2 per million input tokens
and $10 per million output tokens. Cache reads use $0.10 and the conservative
one-hour cache-write rate is $4; requests do not enable prompt caching. These are
the [official model prices](https://platform.claude.com/docs/en/models/sonnet-5-5/overview),
checked October 20, 2026. A different model needs a pricing/adapter evaluation
revision. Environment overrides may raise the configured prices but cannot lower
them below this verified tuple.

The body is bounded to 100,000 UTF-8 bytes, including its schema. With the configured
10,000 output-token cap, 4,096 token protocol headroom, conservative cache input
pricing and $0.03 additional headroom, the maximum modeled allowance is $0.546384.
The existing $0.65 text-phase reservation covers it. This is a reservation ceiling,
not the expected cost of a lesson. Full-job reservation remains $2, covering
research, authoring, review and at most seven narrated stages; receipts retain
actual observed tokens, model identity, cache categories and computed cost.

Claude's [structured-output grammar subset](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
does not enforce every application bound. The transport moves unsupported numeric,
string and array bounds into schema descriptions; the original Pydantic contracts,
evidence checkpoint and quality gates still validate every returned lesson.
Refusals, partial JSON, incomplete streams and identity mismatches stop the phase.

There is one bounded request with no automatic paid retry, provider fallback,
retrieval tools or code execution. A terminal usage event is required before
stream billing becomes complete. If a stream fails after revealing its model but
before final billing, settlement retains the entire phase allowance for owner
reconciliation. Replaying a saved paid result retains the existing checkpoint
behavior. No private thinking, raw provider errors, prompt or credential is logged.

Automated adapter tests intercept HTTP and cover structured success, refusal,
token exhaustion, malformed JSON/SSE, quota/timeout, truncated streams, missing
usage, wrong identity, schema translation, routing isolation and uncertain billing.
The same product evaluation cases and human lesson gates remain necessary before
claiming release quality. This change itself made no paid provider calls.
