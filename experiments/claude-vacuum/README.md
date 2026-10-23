# Claude + Anatomy vacuum trial

One Claude API-authored, locally inspected HTML candidate with explicit Codex
integration/geometry/playback repairs. This is an
experiment for owner craft review, not an enabled production provider or catalog
lesson. Read [BRIEF.md](BRIEF.md) and [request.md](request.md). The owner rejected
the earlier four-engine study; no engine/model has an acceptance claim.

The trial uses the existing shared gateway, trusted ProviderRegistry startup
composition, config loader, structured logger and Store/accounting functions.
Only the authoring task is enabled in the CLI process. The adapter supports plain
text and explicitly rejects schema/label requests; retrieval, chat, speech and
production structured authoring are not enabled. Production remains OpenAI.

`config.json` (Opus) and `config-art-first.json` (Sonnet) are JSON-form YAML mappings loaded by the shared config service and
validated by a strict Pydantic contract. Its model/rates/token/deadline limits are
an explicit trusted selection, not endpoints/keys supplied by a web client. The
Messages stream records input/output/cache usage and actual model identity. A
transport/protocol failure keeps the full bounded reservation as uncertain billing.
A complete stream with unusable output retains known usage instead. There is no
automatic retry or alternate model. This local ledger's $5 ceiling is separate
from the hosted app's unchanged $50 ceiling and its existing operation ledger.

## Run and inspect

The owner's key belongs only in the ignored `.env.local` as `ANTHROPIC_API_KEY`.
Never copy it into prompts, public output or a browser. No key/model request is
needed to view the packed result.

```sh
.venv/bin/python -m backend.claude_trial_run --operation sonnet-art-first --request experiments/claude-vacuum/request-art-first.md
```

Each operation is immutable and idempotent. Repeating a completed, matching
operation reuses its checkpoint. Failed/dispatched/mismatched operations stop.
Explicitly inspect the ledger and resolve a failure before authorizing a distinct
paid attempt; changing a name is not automatic recovery. Do not delete the ledger
to reset spending. Prompts/output/receipts stay under ignored owner-only
`.vercel/claude-vacuum/private/`; no production DB or Blob is accessed.

Inspect the completed HTML source before packing. This is a code-authoring spike;
generated JavaScript never enters the product's declarative lesson runtime.
`pack.mjs` rejects unexpected network/storage/import constructs, binds output to
the settled operation, embeds the actual vendored Anatomy modules, and inserts a
network-denying CSP. It uses esbuild from the previous study's isolated runtime;
install that runtime per its README if absent. The tiny embedded Python projection
is an interprocess JSON data channel, not an application log.

```sh
node experiments/claude-vacuum/pack.mjs sonnet-art-first
.venv/bin/python -m http.server 8067 --bind 127.0.0.1 --directory .vercel/claude-vacuum/public
```

Only the public subdirectory is served. It contains the single self-contained
`index.html`. Open `http://127.0.0.1:8067/` and use `?render` for stopped-clock
inspection. Review chapter stills at 390/768/1280 widths and use `window.seek(t)`
for reproducible motion. Frame inspection and any manual source repair must be
reported; completing an API response does not establish craft or accuracy.

The original article describes a Claude Code agent that builds, inspects and
repairs over several steps. This trial is an API generation plus explicit Codex
integration/review loop, not a claim of unattended equivalence. No application
generation or media feature is enabled by placing the key in `.env.local`.

## Actual run and final candidate

Three Opus attempts produced no usable HTML: one short read timeout, one overall
deadline, then a complete usage report with 24,000 output tokens consumed without
visible text. Those failed requests retain conservative allowances in the ledger;
the third predates the separate `billing_complete` flag and was not retroactively
reconciled. These failures do not evaluate Opus visual quality.

The shorter Sonnet profile uses its documented `between_tools` mode, which skips
up-front thinking in this no-tools request. One base page plus two deliberate
feedback revisions completed. Feedback notes are source controlled; the prompts
containing the complete prior generated HTML are private/ignored. Different
prompts, thinking settings and human repairs prevent an isolated model ranking.

`finish.mjs` applies hash-traceable manual repairs to the preserved final response:
camera/label alignment, actual kit corrugation options, motor support, open nozzle,
connected flow cues, shaft label, playback transitions, reduced-motion still and
source links. These are part of the production effort, not autonomous Claude output.

```sh
node experiments/claude-vacuum/finish.mjs
node experiments/claude-vacuum/pack.mjs sonnet-final reviewed
```

The packer validates the original settled response and the derived repair chain;
About discloses both. All artifacts and private receipts remain ignored. This
HTML is not a production LessonSpec; it has not passed `backend.quality` or the
publication gates. Source/craft inspection does not establish technical truth or
beginner learning. A second bounded iteration replaces the insufficient bag focus
ring with `bag-window.mjs`: a Codex-authored, independently rendered passage and
filter wall, labeled input/output, qualitative air/dirt evidence and a native
return-to-whole control. It consumes the same pose; blocked flow preserves the
retained sample. The real Anatomy figure remains the locator. This teaching
addition is disclosed as human/agent direction, not Claude API output. Three
renderer contract tests and strict JS type checking cover the new module.
Do not select a universal system or publish on engineering checks alone.
