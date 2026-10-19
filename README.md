# Inside — how everyday machines work

A family-alpha web app with a growing shared library, interactive cutaways, narrated videos,
feedback and private follow-up chat. Web first, installable PWA next, with a versioned API and
lesson contract for future iOS and Android clients.

## Current state

The React interface and FastAPI backend are connected locally. Three authored starter lessons
cover a front-load washer, electric pressure cooker and split-system air conditioner. Each has
selectable parts, stage playback, included questions, sources, assumptions and a narrated MP4.
The washer also includes a small force-balance experiment with an illustrative speed control.

Family members can save a lesson and its video offline, filter saved lessons and restore their
playback position. Feedback records the lesson version and current stage. Private chat is stored
separately from the shared artifact. The owner report shows demand, reuse, feedback, jobs and a
cost ledger without conversation text.

**Not yet a completed release:** live model generation, measured provider costs, deployed private-video
delivery and deployed queue operation still require integration verification. A private Blob write/read/cleanup passed. The model key,
explicit spending ceiling and production database are not configured. No test fixture is
presented as live AI output. Native apps and exact-model manual ingestion are later releases.

See [BUILD-PLAN.md](docs/BUILD-PLAN.md) for the current scope and completion evidence.
The [release audit](docs/RELEASE-AUDIT.md) distinguishes implemented behavior from unverified hosted requirements.

## Run locally

Use Node 24 and Python 3.13. Preserve existing `.env.local` entries when adding settings from
[.env.example](.env.example). Use distinct random invite, owner and session values; keep the
provider key on the server. A zero budget keeps paid generation disabled.

```sh
uv venv .venv --python 3.13
uv pip install --python .venv/bin/python -r requirements.txt
npm ci
npm run build
# On macOS: render the authored starters with local computer speech, no paid AI calls.
.venv/bin/python -m backend.seed
npm start
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). For frontend development, keep the API
running and use `npm run dev` on port 5173. It proxies `/api` to port 8000.

Local development uses `.data/inside.sqlite3` and explicitly non-durable in-process jobs.
Production refuses to start without durable Postgres, private Blob storage and session settings.
Hosted model calls go through the actual workspace model gateway, using a hosted adapter.
Vendored workspace config, logging and checkpoint services remain unmodified.

## Verification

```sh
npm run build
npm run lint
npm test
.venv/bin/ruff check backend tests/backend main.py
.venv/bin/mypy --strict backend tests/backend main.py
.venv/bin/pytest --cov=backend --cov-fail-under=80
```

Backend test tools: pytest, pytest-asyncio, pytest-cov, mypy, ruff, types-PyYAML and types-Pillow.
Tests exercise real SQLite transactions and real MP4 encoding with explicitly synthetic provider
and audio fixtures. An optional Postgres regression test is restricted to a disposable database
on loopback port 55432; see [VERIFICATION.md](docs/VERIFICATION.md).

Vercel CLI 53 does not package the newer Python subscriber declarations. Deployment tooling is
pinned to CLI 64.5.0 in the Linux verification image, separately from application dependencies.
Do not upload an unchecked local prebuilt bundle. The source allowlist and bundle verifier check
that credentials, local data and test media are excluded and a real queue consumer exists.

```sh
node scripts/prepare-build-check.mjs
# Run the documented Linux verification container, then:
node scripts/check-deployment-output.mjs
```

The build-time `VERCEL_FASTAPI_STATIC_CDN=1` setting is required so the built shell and its
versioned service worker reach the CDN. The app shell is public; protected data lives under
`/api/v1`, which the service worker never caches. Only explicit lesson downloads enter IndexedDB.
Signing out clears downloaded lessons, progress and local conversation references.

Authored starter deployment is separate from local rendering:

```sh
.venv/bin/python -m backend.starters prepare
# Only after configuring the intended managed DATABASE_URL:
.venv/bin/python -m backend.starters import
```

Preparation uploads and verifies only the three authored videos. Import preserves existing lessons
and does not copy local users, chats, feedback or analytics. The manifest and production access
material stay in the ignored `.vercel/` directory; never publish those files.

## Cost and integrity

Lookup and pending-job deduplication happen before generation. Admissions reserve budget
atomically; each author/review/speech result is saved with its receipt before advancing.
Interrupted calls with unknown billing retain their allowance rather than silently paying again.
Publication requires validated lesson data and a completed narrated video. An automated editorial
check is not factual verification. Scenes are bounded data, never executable generated code.

Speech costs are estimates; token costs use configured rates. Provider invoices and provider-side
limits remain the authority for actual charges. Hosting/compute charges need separate accounting.
No measured live cost-per-machine benchmark exists yet.

## Product and research

- [PRD](docs/PRD.md), [current build plan](docs/BUILD-PLAN.md), [verification](docs/VERIFICATION.md)
- [Technical mobile path](docs/MOBILE-PATH.md)
- [Market research](docs/MARKET-RESEARCH.md), [iOS/business model](docs/IOS-AND-BUSINESS-MODEL.md)
- [Cost scenarios](docs/COST-TABLES.md), [repo/article research](RESEARCH.md)
- [Brief](BRIEF.md), [design direction](DESIGN.md), [friction log](design/friction-log.md)

The original Anatomy-based visual lab remains separate: `npm run build:lab`, then
`npm run start:lab` on port 4173. It builds into `dist-lab/`. Upstream is unchanged, pinned to
`1482e8469b0a9e0d8cc18ea2740a01423d29ae80`, with its MIT license retained in `vendor/anatomy/`.

## Engineering and provider routing

[AGENTS.md](AGENTS.md) records the project engineering contract. Shared gateway
access remains mandatory. `backend/routing.py` provides typed provider plugins and
explicit authoring, review, chat and speech routes. `configure_gateway` accepts a
validated registry at trusted startup composition; the default routes use the
existing OpenAI adapter and configured text/speech models. Neither clients nor
lesson prompts select provider endpoints.

Provider additions must supply task capabilities, protocol translation, usage
receipts, validated rates/reservations and adapter contract tests. Default
credential readiness and prices currently cover OpenAI only. Claude and open-model
adapters, runtime provider selection, and comparative quality evaluations are not
implemented. No automatic paid fallback is configured.
