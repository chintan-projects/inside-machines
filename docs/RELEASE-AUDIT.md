# Release audit — October 19, 2026

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

## External inputs required

1. The human must review and accept [Neon's marketplace terms](https://vercel.com/chintan-4466s-projects/~/integrations/accept-terms/neon?source=cli). Provisioning currently returns `integration_terms_acceptance_required`; no acceptance has been performed by the agent.
2. Configure a server-side `OPENAI_API_KEY` locally or in the project environment. Do not paste it into chat or a browser-facing `VITE_` variable.
3. Supply an explicit total app-AI spending ceiling. No paid app-model requests have been made; generation remains disabled.

These conditions have persisted across multiple consecutive goal turns. Independent implementation, storage preparation and local integration checks are complete enough that further release progress now requires human input or an external-state change.

## Resume sequence

Provision/link the managed database, import only the prepared starter lessons, configure the approved provider/budget, run an actual new-machine generation and private follow-up, measure tokens/cost including failures, verify second-member reuse, resolve failures, finish the human UI/device review, then deploy and verify the complete hosted/PWA experience. Do not call the goal complete before that evidence exists.
