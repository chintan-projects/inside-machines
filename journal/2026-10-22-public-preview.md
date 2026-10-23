# Public repository and no-login learning preview

The owner explicitly asks why the product was called unfinished, requests a
current README with screenshots and a Vercel link, and authorizes making the
repository and app public with no visitor login or special access. The remaining
work is lesson craft and human learning evidence; that is separate from whether
people may explore a clearly labelled preview. ADR0008 records the distinction.

Implementation must preserve owner authorization, unique private visitor sessions,
historical conversations, artifact identities and the existing spending ledger.
Public missing-topic requests collect interest without paid authoring. Native
preview permission is explicit and bound to exact artifacts/graph. It records
exposure permission, not quality approvals, replacement activation or release
notifications. No actual paid model call is needed to verify these boundaries.

A separate read-only audit inspected every reachable local ref,44commit objects,
967unique blobs/7,805,432bytes (964text and3binary), and450tracked paths atf45dc0d.
Gitleaks scanned all44commits/~3.07MB of changes; its sole generic-key alert was
an explicitly documented artwork SHA256 at9e193b5, not a credential. Independent
scans of every text blob and commit object found no actual provider/auth/bypass
keys, private keys, JWTs or password URLs. Fixture values and tokenizer metadata
were distinguished from real credentials. No committed environment, private
chat/database export, screenshots or generated audio/video was found. The three
binaries are two app icons and the Inter font.

The audit also checked remote refs and PR1's merge tree, with no issue/PR comments
or reviews containing private material. Main was20commits behind the audited
feature branch; publishing the old default branch would misrepresent the app.
Anatomy MIT and Inter OFL notices are retained. The shared runtime comes from
the same owner's workspace-shared repository; no restrictive notice was found.
No root license was invented. Nonsecret deployment IDs, the author's email and
local paths remain in engineering history. Ignored local files, production stores
and the external submodule's full history were outside the credential audit;
this is not formal proof that no secret exists anywhere.

Only deliberately selected public visitor screenshots may be committed under
docs/images/readme. Raw owner captures, credentials, private discussions, data
and generated media remain ignored. Actual public runtime/viewport checks,
repository visibility and deployment outcomes are recorded below after completion.

## Observed local visitor journeys

A fresh browser on the isolated public-mode server opened the refrigerator
without an invite or account form. The public review label and all six component
labels rendered at 375px and 1440px. Desktop mechanism selection changed the
working cutaway and caption. Typing `dive deeper` opened the energy explanation.
Saving the complete path, disabling the network and reloading retained the guest
identity and all three nodes; the depth action worked offline. GPU data-supply
controls changed ready work and completed results at tablet/desktop widths;
Watch & listen entered narration playback. Browser console reported no errors in
these checks. Physical-device audio/VoiceOver and beginner learning are untested.
Three public-visitor screenshots were deliberately selected for the README;
none includes an owner session, private discussion or credentials.

Independent review reproduced two issues before public release: recomposing an
identical rejected artifact as a one-node path could bypass its rejection, and
10,000 ordinary telemetry events could evict active anonymous admission records.
Both must be fixed with regressions before deployment; the global atomic budget
ceiling remained intact in the second case.

The local owner path editor displayed the exact enabled preview, revoked it with
a visible confirmation and accepted re-enabling it. Signing out returned to the
public bootstrap. This test used isolated local credentials and data; no
production owner code was entered into browser automation.

## Pre-deployment verification

Both reported issues were fixed and independently rechecked: identical-root
one-node recomposition returns409 after a current artifact rejection; excess
guest issuance returns429 after10,000 telemetry events and a Store reload.
Thirty-six focused public/rate/chat tests pass. Dedicated bounded counters use
the shared Store transaction, migrate active historical admission events before
telemetry rotation and fail closed at capacity. Paid quota consumption and budget
reservation roll back together. Native media delivery checks actual bytes against
the stored video hash; preview enabling checks metadata/proof/source/rejection
bindings and does not independently fetch media at enable-time.

Ruff and strict mypy127files pass. The full backend run has390passed,10optional
Postgres skips and89.77%coverage; the real disposable Postgres suite is recorded
separately below. Frontend types, lint,41tests and the production/PWA build pass.
Native source/spec registrations remain unchanged. No model call was made.

All10 real Postgres regressions passed separately against the disposable local
Postgres database, including concurrent public chat admission with exactly12
network admissions and matching budget receipts. The owned test container was
removed. No production database was used for transactional regression tests.

The sanitized Linux/amd64 build with public mode enabled completed. The deployment
verifier confirms two Python functions, the durable queue trigger, shared services,
Linux encoder, versioned CDN/PWA assets and exclusion of private inputs.
The staged credential scan has zero findings.
