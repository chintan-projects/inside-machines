# Release audit — October 19, 2026

**Current quality status:** human AC review rejected the previous visual benchmark.
See [QUALITY-BAR.md](QUALITY-BAR.md) for the revision and remaining release criteria.
The table below is the historical pre-deployment baseline; the later deployment
section records resolved infrastructure checks. Family release remains held.

The objective remains the complete growing-library family alpha on Vercel, with a PWA and a documented path to native clients. It is **not achieved**. A local implementation, successful packaging and synthetic-provider tests do not establish live generation or a deployed service.

| Requirement | Current authoritative evidence | Release status |
| --- | --- | --- |
| Family access | Invite/session tests, browser login/logout, production-mode ASGI smoke with real Postgres and Secure cookies; actual production invite/owner/session secrets configured on Vercel | Implemented; deployed behavior unverified |
| Catalog and aliases | Authored catalog works locally; normalization tests preserve top-load, window AC, AC motor and other mechanism-changing qualifiers | Implemented; novel-topic matching needs live evaluation |
| New-machine creation | Checkpointed author/review/speech/video pipeline passes with synthetic model output and real encoding | **Missing live provider verification** |
| Shared reuse | Real Postgres smoke proves two members reuse an authored lesson without new jobs; concurrent admission tests prove one reservation | **Live generated-artifact reuse unverified** |
| Durable concurrency | Real Postgres synchronized cold starts, advisory initialization lock, transaction rollback, deduplication and interrupted-worker tests | Implemented; deployed queue delivery/retry unverified |
| Visual explanation | Three authored mechanisms, selected parts, stages and washer force-balance experiment inspected in Chrome | Implemented; human review and new-generation quality unverified |
| Narrated video | Three real H.264/AAC videos, audible streams, captions and offline playback; authenticated API reads actual private videos through real Postgres records | Implemented; deployed video delivery unverified |
| Feedback | Browser persistence, stage/version tests and real Postgres ASGI smoke | Implemented; persistence across cloud deployments unverified |
| Clarifying chat | Private persistent conversations, cross-member isolation, bounded answers/actions and streaming transport implemented | **Fresh live answers unverified** |
| Usage research | Owner-only demand, reuse, feedback, failures and token/cost ledger; private conversation text excluded from owner report | Implemented; actual new-machine cost benchmark missing |
| Cost control | Atomic reservations, bounded calls, idempotent settlement, unknown-billing retention and disabled-without-key-and-budget tests | Implemented; actual provider pricing/usage behavior requires a funded live test |
| PWA | Manifest/icons, versioned shell, explicit downloads, offline video/captions, saved filtering, progress restoration and logout cleanup verified in Chrome | Implemented; deployed and target-phone checks pending |
| Vercel | Project, auth configuration and private storage ready; Linux output verifier proves API/queue functions, encoder, shared services, CDN shell and private-input exclusion | **Not deployed; managed database not provisioned** |
| Mobile path | Versioned API/lesson contract and `MOBILE-PATH.md` document reuse and platform-specific work | Documented; native binaries remain outside the current delivery target |

## Additional deployment preparation

- `backend.starters prepare` uploaded and read back all three actual starter MP4s using content-addressed private locations and SHA-256 checks. Its deployment-only manifest is in the ignored `.vercel/` directory.
- Import tests prove that local users, chats, feedback, analytics and spend are not copied. The real Postgres smoke imported three lessons, then skipped all three on a repeat run without overwriting them.
- Production access material is stored privately at `.vercel/alpha-access.json` with owner-only file permissions. It must not be published or shared as a family invite: it also contains owner/server credentials.
- Current verification: 63 backend tests, 87.09% coverage, strict Python/TypeScript checks, frontend lint and five JavaScript tests pass. Rebuild and rerun the final gates before publishing.

## Setup resolved and protected deployment verification

The user accepted Neon's terms and authorized **$50 total app-AI spend**. The budget
is configured in Vercel Production, Preview and Development. This app-level ledger
is independent of hosting/storage charges and any OpenAI account billing limit.

- Personal GitHub: `chintan-projects/inside-machines` (private).
- Personal Vercel scope: `chintan-4466s-projects`; project `inside-machines-alpha`.
- Neon `inside-machines-db` provisioned on the free plan and connected. Three
  authored starter lessons imported; local users/chats/analytics were excluded.
- `OPENAI_API_KEY` is Sensitive and Production-only. It is intentionally unavailable
  to local environment pulls. Do not remove that protection to run tests.
- Vercel deployment is Ready and remains behind Vercel Authentication. Hosted
  sign-in, catalog and private MP4 byte-range delivery passed.
- A live chat used 1,853 input / 97 output tokens for $0.004676 at configured rates.
- Initial queued authoring reached the provider but returned HTTP 400. Unsupported
  URI format is removed only from the outbound provider schema; application HttpUrl
  validation remains. Regression coverage added; corrected live generation passed through publication.
- Initial schema rejection and subsequent 100-second timeout retain $1.30 total as **uncertain billing**, not
  reported as confirmed provider charges. Do not erase these allowances to improve the benchmark.
- A controlled retry uses configured low reasoning and a 210-second provider deadline
  inside the 240-second lease. It completed in 6m16s for $0.234596 including estimated speech.
  No implicit model fallback or paid retry is enabled.
- Hosted two-member starter reuse, private chat isolation, owner-route isolation,
  session revocation, MP4 range delivery and PWA shell assets all passed.

## Remaining release work

Live new-lesson generation, contextual follow-up, two-member generated-artifact
reuse and hosted Chrome offline reload/video/captions passed. See [LIVE-BENCHMARK.md](LIVE-BENCHMARK.md) for usage, costs, failures
and limitations. The catalog now contains three authored starters and one actual
AI-created lesson. Latest backend checks: 72 pass, one disposable-Postgres test
skipped; 86.58% coverage. Frontend strict checks, lint, five tests and build pass.

Human UI/device review remains before family access. The design-quality skill
requires the person's release decision. Vercel Authentication is still enabled;
do not tell family members this is an unrestricted invite-only release yet.
Native device install, accessibility review and hosted offline behavior on the
actual target phones need the human walkthrough. The requirement table above is
the earlier audit baseline; this section and the live benchmark supersede its
unverified hosted-generation rows. The full release objective is not complete.
