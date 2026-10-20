# Curated library: implementation and review boundary

The web application now uses the shared D1 studio from `web/studio` for every
compatible CE lesson. Local studies import that same player. Historical readers,
artifact hashes and unavailable-renderer video/text fallbacks remain intact.
This implements the integration boundary; it does not certify lesson quality.

## Member and owner flow

1. A member asks a general question. A matching lesson opens without a model call.
2. A missing topic creates or joins one free, durable interest record. Repeating
   the request is idempotent. The member's request list and inbox are private.
3. The owner sees aggregated demand, plans/declines the request, binds an existing
   lesson or explicitly starts a budgeted draft. Customers cannot dispatch that
   build. There is no automatic paid retry or provider fallback.
4. Evidence retrieval, authoring, SHA-bound editorial review, speech and rendering
   retain separate checkpoints and receipts. Completion produces a **review draft**.
5. The owner records engineering, independent technical, actual-phone craft and
   beginner-learning evidence, followed by release for the exact artifacts.
6. Release creates one in-app update per requester/artifact. Revocation, archive,
   artifact mismatch or a changed learning bundle removes its availability link.

Notifications are in-app. Email delivery, browser push, subscription billing and
automatic arbitrary-topic publication are not implemented or implied.
The family alpha can inspect clearly labeled drafts; a draft is never a release.
Specific-model documentation remains outside this generic-system seed library.

## Twenty source-led core scopes

Gasoline car, GPU, refrigerator, microwave, dishwasher, induction cooktop,
electric oven, washing machine, vacuum cleaner, table fan, vented clothes dryer,
air conditioner, electric kettle, pressure cooker, pump-driven espresso machine,
electric storage water heater, reversible heat pump, gravity-tank siphonic toilet,
sink drain/P-trap and ceramic-disc faucet.

The more developed AC, washer, cooker and vacuum teaching artwork is retained.
Sixteen added cores use distinct trusted sections and a final job-relationship
map. The map is explicitly **not physical layout or appliance timing**. Work,
fluid and information/control paths have different encodings. Numeric GPU examples
are declared toy arithmetic, never hardware/performance measurements.

Each source plan has a scope, misconception, claims/locations, labeled input and
output, qualitative comparison, transfer rubric and limitations. Iteration records
are in `design/lessons/curated/`. Playback, static steps, comparisons and saved
offline use incur no AI calls. New media uses local computer speech at the existing
1280×866/24fps format; completed bytes and metadata are verified and checkpointed.

The new schematic sections and boxed locators have **not** established the selected
Claude/Anatomy trial's physical craft standard. They remain review candidates.
Human technical, actual-device, beginner and owner quality gates remain held.
The earlier GPU/refrigerator native studies retain their distinct deep-path
content; adding a CE core does not silently promote those experimental branches.

## Progressive depth and integrity

A complete core is a valid one-node path. The owner editor can connect actual
existing core, insight and model revisions. It cannot invent depth by changing
button labels. Optional draft composition allows the whole experience to be
reviewed before all branches are approved; release remains held.

Graph history and exact node spec/video identities are immutable. Compare-and-swap
protects concurrent owner edits. New graphs require new bundle-bound reviews.
Private chat and feedback follow the **active revision**. Offline downloads verify
all node video hashes and commit atomically; a failure preserves the earlier save.
Idle tabs cannot overwrite another tab's newer progress.

See [path composition](LEARNING-PATH-COMPOSITION.md) and
[curation decision](architecture-decisions/0006-curated-library-and-interest.md).

## Cost interpretation

The owner table exposes all 20 scopes, build/chat token counters, recorded versus
estimated costs, uncertain billing, historical revisions and unallocated operations.
It reads the shared operation ledger; it is not a second billing system.

- Seed lessons: locally prepared content and computer speech, **zero new paid app API calls**.
  This is not an AI-generated-per-machine price benchmark. Storage, hosting and
  coding-agent use and human authoring/review effort are separate.
- Missing requests and repeat views: zero model calls.
- An owner AI build: the configured **$2 reservation** is an admission allowance,
  not an expected charge or a promise of publishable quality. Each phase settles
  against its receipt; unknown billing remains reserved conservatively.
- Speech quotes use script length and an explicitly disclosed speaking-rate
  assumption. They remain estimates until a provider receipt exists.
- The app's $50 AI ceiling is preserved. It is not a Vercel-wide invoice limit.

Claude structured authoring can be selected explicitly. OpenAI research,
editorial review, chat and speech stay separately routed. Provider contract tests
do not establish comparative visual quality. See [Claude routing](CLAUDE-AUTHORING.md).

## Verification and evidence

Automated regressions cover request privacy/deduplication, zero-cost member requests,
owner-only builds, release/revocation notifications, exact bundle reviews, old
artifact/private history, cache integrity and provider failure accounting.
Disposable Postgres exercises concurrent subscribers, atomic release notices,
rollback and competing path attachments. Required full checks and deployment
evidence are recorded in the session journal, not inferred from this document.

The browser review found and corrected idle-tab progress erasure and crowded mobile
navigation. Emulated phone/tablet/desktop and offline checks are separate from a
real-device craft pass. No learner results or independent human approval are invented.
