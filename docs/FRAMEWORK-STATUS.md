# Shared framework and catalog rollout

**Implementation update, 2026-10-20:** the curated request pipeline, shared D1
production adapter, structured Claude authoring route, owner path editor,
artifact-bound notifications and 20 source-led core candidates are implemented.
See [current integration and limits](CURATED-LIBRARY.md). Render/deployment and
acceptance evidence are recorded separately; the historical audit below does not
describe the updated source. Native GPU/fridge experimental depth content has
not been silently certified or converted by this integration.

## Historical deployment baseline

Audit: 2026-10-20. The owner asks to push all work, keep every catalog topic on
one framework, and evaluate open-ended generation from the Vercel frontend.
This records observed state and a proposed rollout; it does not enable a new
production authoring route or approve any lesson.

## What exists

The read-only live database audit found nine immutable lesson records. Five
historical revisions are archived. All four active entries—AC, pressure cooker,
washer and vacuum—use LessonSpec v2 / CE-1 and the shared TeachingStudio. They
have videos and pass current structural checks. None has all required human
release gates. Historical v1 revisions remain readable without rewriting their
content, media, saved references or conversations.

The newer GPU and refrigerator studies share the D1 player, versioned
`learning-path-1` navigation, narration clock, design tokens and lesson contract.
Their pure domain rules and trusted scene adapters differ. The earlier local
Claude vacuum uses its preserved original player. These studies are not active
marketplace entries and are not served by the Vercel application.

The production queue already supports evidence → author → editorial review →
speech → rendering, with atomic admissions, deduplication, checkpoints and usage
receipts. It uses OpenAI. The text-only Claude adapter is an isolated local
authoring trial; it rejects structured production authoring and has no research
or speech route. Copying its registry entry into startup would not implement
production readiness. `path_prompt` and node context helpers prepare requests;
they do not dispatch a production multi-node generation job.

Consequently, submitting “How does a car work?” can enter the existing generic
generation pipeline if enabled and admitted. It cannot currently promise a page
matching the refrigerator's D1 interface, depth or inspected visual craft. No car
generation or model call was made during this audit.

## Recommended product policy

Keep the request box open. Start with roughly 5–10 excellent, reviewed lessons;
grow toward 50 in response to actual requests rather than creating 50 upfront.
This is a recommendation, not an agreed catalog limit or an implemented filter.

1. Find an existing lesson that matches the mechanism and scope. Reuse it freely.
2. Clarify ambiguity that changes the explanation. For a car: gasoline, electric,
   or a comparison. Generic versus an exact owner's model remains a separate choice.
3. Generate a private, clearly marked draft within a reserved per-job/alpha budget.
   Use a complete core before optional branches. An unsuccessful call remains
   recorded; no automatic paid retry or provider switch.
4. Validate evidence, supported mechanisms, geometry/labels, arithmetic, cue
   alignment and accessibility. Requester feedback helps prioritize revisions;
   a thumbs-up is not independent technical or learning certification.
5. Publish one immutable shared revision after the required review evidence and
   explicit owner release decision. Reuse it for later users. Unsupported visual
   families remain saved requests rather than fabricated completed lessons.

A curated published library and open discovery are compatible. The early scarce
resource is review/craft capacity; current evidence does not establish a reliable
unattended generation rate, cost or quality for arbitrary topics. The refrigerator
art calls totaled about $0.29 at configured rates, but that excludes human/agent
integration, source review, UI refinement and hosted production operations. It is
not an automatic full-lesson unit-cost benchmark.

## Work required before the hosted experience matches D1

- Adopt a versioned production path/artifact envelope and shared D1 client shell,
  with protected artifact resolution, offline downloads and private discussions.
  Keep old LessonSpecs and media immutable; do not branch the player by topic.
- Translate the inspected Anatomy craft into trusted declarative scene adapters
  and reusable mechanism families. Models author validated data, not executable
  HTML/JavaScript loaded into the app. Domain rules stay outside renderers.
- Add Claude structured authoring through the existing gateway/registry, with
  model-specific validated rates, reservations, refusal/truncation handling and
  adapter contract tests. Keep research/review/speech explicitly routed; preserve
  the evidence checkpoint and SHA-bound review. No silent route switch.
- Dispatch core and optional nodes through the existing durable queue/checkpoints.
  Complete/review the core first; budget optional branches independently. A
  request may outlive the browser connection. Do not replace the queue merely to
  adopt another workflow library.
- Migrate active catalog topics individually into reviewed D1 revisions. The
  shared framework is a reuse guarantee, not proof of scientific or visual quality.
- Evaluate an unseen, scoped car request end to end in a protected preview:
  source research → complete core → meaningful experiment → optional depth →
  narration/captions → exact paused return → second-user reuse without another
  generation charge. Inspect actual-phone craft and beginner transfer separately.

Claude supports JSON-schema-constrained output; this is a protocol building
block, not verification of a mechanism's truth or craft. See [Claude structured
outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).
Long-running generation can be hosted with durable state; Vercel documents one
[durable agent approach](https://vercel.com/kb/guide/how-to-build-a-durable-ai-code-agent-on-vercel).
Our existing checkpointed queue remains the chosen implementation. That guide's
retry examples do not override this project's no-silent-paid-retry contract.

## Git and deployment are separate

The current personal identity, Owner membership, project, Neon and private Blob
ownership were reverified against `chintansanghvi5@gmail.com` / `cdt9s-projects`.
The protected live app is healthy and generation-enabled; recorded app spend is
$3.212849538461539, with no outstanding reservations. The local trial has its own
separate ledger. Neither budget was changed.

Vercel's project has no Git link. Pushing the feature branch updates the private
repository and draft PR; it does not publish local studies or trigger a verified
production rollout. Personal GitHub login connection remains BUG-008. No account,
protection, environment, storage reference or live lesson was changed for this
audit. Private API responses, environment export and catalog inventory stay ignored
under `.vercel/push-audit-20261020`.
