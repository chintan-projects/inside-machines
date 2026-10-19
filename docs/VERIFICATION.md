# Family alpha verification — October 19, 2026

This is evidence about the implementation, not a release certification or an engineering review.

## Automated and runtime evidence

- 63 backend tests passed with the optional real Postgres test enabled, at 87.09% coverage, including qualified-machine lookup, stage-specific feedback and selective/idempotent starter import. Rerun before release.
- Five JavaScript tests cover the original deterministic cycle and the new idealized force-balance experiment.
- Python strict type checking, TypeScript checking, Python lint and frontend lint passed during implementation.
- The complete phase-pipeline test uses synthetic provider output but real transactions, artifact writes, checkpoints and ffmpeg encoding.
- Three actual authored starter MP4s are stored locally: washer 50.73 s, cooker about 42 s, AC about 45 s. Each has H.264 video and AAC audio; measured mean audio levels were approximately −19.5, −20.3 and −19.9 dB, respectively. This checks audibility, not narration quality with learners.
- Eight synchronized real Postgres connections reproduced a cold-start `pg_type_typname_nsp_index` violation. A transaction-scoped advisory lock fixes it; the regression also verifies one admitted job and rollback.
- A real private Blob write/read round trip passed using a unique temporary JSON object. The object was then deleted successfully. This verifies the adapter and credential, not video delivery from deployed functions.
- All three real starter MP4s were uploaded to content-addressed private Blob locations and read back with matching SHA-256 hashes. A production-mode ASGI smoke with real Postgres verified authenticated byte-range delivery for all three, Secure cookies, two-member reuse without new jobs, private chat isolation and persisted feedback. This was not a deployed Vercel runtime test.

## Browser observations

Observed through Chrome's browser tooling, rather than inferred only from source:

| Journey | Evidence |
| --- | --- |
| Family entry | Invite opens the three-lesson catalog; owner entry also exposes Alpha insights |
| Phone layout | At 375×844, document width is 375; playback controls end around y=645, inside the first lesson viewport |
| Tablet report | At 768×1024, document width equals viewport width; demand and feedback appear without overflow |
| Desktop | Catalog and lesson inspected at the normal 1512-pixel browser width |
| Stage/question | Selecting Tumble updates the text and selected motor; an included question opens its authored answer and visual action |
| Feedback | A positive response persisted and appeared in the owner report |
| Missing machine | Television request reports generation as disconnected and appears as demand; it does not simulate successful generation |
| Fully offline reload | Explicitly downloaded washer lesson reopened with network disabled |
| Offline video | Blob-backed video had readyState 4, duration 50.73 s, one caption track and advancing playback time |
| Sign-out isolation | Offline sign-out returned to entry; reconnect did not restore the session. Cache inspection found zero `/api` responses and zero saved lessons after switching members |
| Progress | After selecting Tumble and reloading, stage Tumble and timeline 8.75 seconds were restored |
| Causal control | Changing 45→90 rpm changed the displayed contact prediction and diagram consistently |

Network and viewport overrides were reset after testing. These checks do not establish iOS/Android installation, real-device behavior, VoiceOver or complete keyboard usability.

## Linux deployment packaging

Use the official Node and uv images in `scripts/Dockerfile.verification`, with Linux amd64 selected.
The sanitized source directory contains no actual credentials or local user data. The required build-only values are deliberately invalid for external services; no model calls or database connections occur during packaging.

```sh
docker build --platform linux/amd64 -f scripts/Dockerfile.verification -t inside-machines-verification:local scripts
node scripts/prepare-build-check.mjs
docker run --rm --platform linux/amd64 --cpus=2 --memory=4g \
  --mount type=bind,src="$PWD/.vercel/linux-validation",dst=/app \
  -e DATABASE_URL=postgresql://build-only.invalid/inside \
  -e BLOB_READ_WRITE_TOKEN=build-only \
  -e INSIDE_INVITE_CODE=build-only-family \
  -e INSIDE_OWNER_CODE=build-only-owner \
  -e INSIDE_SESSION_SECRET=build-only-session \
  -e INSIDE_BUDGET_USD=0 inside-machines-verification:local
node scripts/check-deployment-output.mjs
```

The verifier requires the API, a real `inside-lessons` queue trigger, shared services, a Linux ffmpeg executable, excluded private inputs and the built CDN shell/service worker. A CLI exit code by itself is insufficient. Local Mac cross-platform packaging cannot import Linux pydantic extensions for subscriber discovery; use the Linux check instead.

The Linux packaging verifier passed during implementation. The API function declares a 300-second
maximum. The queue trigger declares one concurrent delivery, five maximum deliveries and a
255-second retry delay. This is packaging evidence, not proof of deployed queue operation.

For the optional Postgres test, launch a disposable `postgres:17-alpine` container with database `inside_test`, port `127.0.0.1:55432`, and test-only credentials. Set `INSIDE_TEST_DATABASE_URL` explicitly. The test refuses other hosts, ports and database names and drops only its disposable `inside_state` table.

## Evidence still required

1. Human review of the rendered family-alpha UI and a target-phone accessibility/install walk.
2. Production database provisioning after the human accepts Neon's integration terms.
3. A live provider credential and explicit spending ceiling, then a measured new-machine build, contextual chat and second-member reuse without regeneration.
4. Deployed private-video delivery, queue delivery/retry, generation and feedback persistence across deploys, session isolation and deployed PWA smoke tests.

Database provisioning was retried and still returns `integration_terms_acceptance_required`.
The human must review and accept [Neon's marketplace terms](https://vercel.com/chintan-4466s-projects/~/integrations/accept-terms/neon?source=cli) before the integration can be created. No acceptance has been performed by the agent.

Vercel project and private Blob storage are configured. They do not prove the complete application is deployed. Keep the goal active until these remaining requirements are demonstrated.
