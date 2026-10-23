# Owner-composed learning paths

The Owner workspace includes **Compose a learning path**. It joins existing,
CE lesson revisions into one complete core with optional insight/model
branches. Composition itself does not generate content, fabricate depth or spend AI credits.
The ordinary one-node core remains supported.

Choose the core revision, edit the versioned path JSON, then attach it. Every node
must already have completed media and pass structural quality checks. By default,
each needs its own release evidence. **Allow review drafts** is an explicit owner
opt-in that permits whole-path preview before individual nodes are approved.
The bundle remains held until its branches and complete experience pass review.
The first node must use the selected core. Each branch references a different,
active leaf revision; nested paths are deliberately unsupported. Graph validation
checks a single core, earlier prerequisites, valid next edges, reachability and
cycles. Unexpected fields such as private chat, provider endpoints or code fail
validation.

Attaching a graph preserves lesson specifications, media, previous graph records,
private conversations and accounting. It writes an immutable content-addressed
record plus the core's current pointer in one Store transaction. The graph SHA
binds the path JSON. The bundle SHA additionally binds the core ID and every node's
exact specification/video hashes. A compare-and-swap field rejects edits made
from a stale owner session. Submitting the same exact composition is idempotent.
At most 32 compositions are retained per core; further iterations need a new core
revision.

The newly attached bundle requires fresh engineering, technical, craft, beginner
learning and release evidence. Prior standalone approval cannot approve new
branches or their relationships. The quality workbench sends the current bundle
SHA with every review. A stale review, changed artifact, withdrawn branch release,
missing record or damaged graph holds availability. Existing unbound embedded
paths remain readable with a review hold until the owner composes a bound record.

History can load an earlier graph into the editor. Attaching that exact prior
bundle can reuse evidence recorded for that same bundle, provided its artifacts
and branches remain current. Loading JSON alone changes nothing. Historical
records are never overwritten.

Requester updates bind to the bundle SHA as well as specification/video hashes.
A changed graph stops advertising the prior update as currently available. Fresh
bundle release creates at most one private in-app notice per topic/member/bundle.
Restoring a reviewed bundle can fulfill newly joined subscribers without creating
duplicate notices for existing recipients. No external messages are sent.

**Build a missing explanation** is a separate, funded owner action. It accepts one
insight/model question about the selected immutable core and reserves the server's
configured draft allowance. The same research, authoring, review and media pipeline
keeps the root example and scope. A completed job produces an independent review
draft; it does not attach or release a branch. The owner can then compose its real
lesson ID. Lost HTTP responses retain the same operation UUID; continuing cannot
silently create a second attempt. A failed operation needs an explicit new funded
attempt. Customer requests never invoke this endpoint.

Authenticated API contracts:

- `GET /api/v1/owner/lessons/{core}/learning-paths`: current pointer and immutable
  graph/artifact history, excluding private owner identity.
- `POST /api/v1/owner/lessons/{core}/learning-paths`: strict body
  `{ "path": <learning-path-1>, "expected_bundle_sha256": "" }`; use the current
  SHA after the first attachment. Returns bundle/path hashes, reuse and review state.
  Optional `allow_review_drafts: true` permits structurally valid media-complete
  drafts; it never supplies or waives release evidence.
- `GET /api/v1/learning-paths/{core}`: validated public path plus member-scoped
  lesson envelopes and `bundle_sha256`. Standalone synthesized cores use an empty
  bundle SHA. Node envelopes expose specification/video hashes for verified offline
  saves. Private conversations are never part of this response.
- `POST /api/v1/owner/lessons/{core}/depth-drafts`: owner-only funded body
  `{ "question": "<8–180 characters>", "role": "insight", "operation": "<UUID>" }`.
  The role can also be `model`. Returns the existing request/job contract; it never
  returns a fabricated lesson or bypasses the budget. The same intent/operation
  reuses the admitted job; a changed intent or terminal failed operation is rejected.
- Review submissions add `bundle_sha256`; an empty value preserves the existing
  standalone-review contract. Nonempty attachment hashes must match exactly.

Structural checks and synthetic database tests verify the implementation. They
do not establish the explanatory quality of a branch or record actual human
review evidence.
