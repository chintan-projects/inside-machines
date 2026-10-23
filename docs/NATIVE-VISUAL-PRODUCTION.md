# Native visual production

The hosted schematic authoring pipeline remains a separate format. It cannot
preserve an Anatomy coding session merely by producing more JSON primitives.
`native-studio-1` carries real component identities, narration cues, evidence,
assessments and controls. Its executable artwork is compiled from a finite,
trusted repository registry, never supplied by a browser or model response.

The shared player, path, clock, discussion, offline media and budget services
remain common to every topic. The refrigerator R2 is a new physical reference;
GPU memory R1 demonstrates the same import adapter with a logical computation.
The latter is a scoped insight, not a new complete GPU course.

## Owner workflow

1. Begin the lesson worksheet, claim ledger, hypothesis and transfer rubric.
   Author source locally with Claude plus actual Anatomy for physical figures.
   Use a truthful logical representation for computation. Render and critique.
2. Add a versioned, trusted definition in `native/definitions.ts`. Keep source
   and domain rules separate. Preserve every previous revision and its sources.
3. Explicitly register that new revision with `node native/export.mjs registry`.
   This canonicalizes metadata through Python and pins its source bytes and
   exact spec hash. An existing registration cannot be silently overwritten.
4. Prepare an ignored output folder:

   ```sh
   node native/export.mjs prepare .vercel/native-production-<revision>
   ```

5. For each prepared lesson folder, synthesize local computer narration and
   export the same state/render functions to H264/AAC media:

   ```sh
   node native/export.mjs speech .vercel/native-production-<revision>/<lesson-id>
   .venv/bin/python -m backend.native_render .vercel/native-production-<revision>/<lesson-id>
   ```

6. Finalize, verify and import into an isolated local review store:

   ```sh
   node native/export.mjs finalize .vercel/native-production-<revision>
   .venv/bin/python -m backend.native_publication verify .vercel/native-production-<revision>/manifest.json
   .venv/bin/python -m backend.native_publication import .vercel/native-production-<revision>/manifest.json --local-data .vercel/native-review-state
   ```

Import creates owner-only held drafts. It does not replace served lessons, attach
a path or approve a release. The manifest's optional path is a composition
suggestion; use the existing explicit owner path operation to preview it.
Configured cloud import requires a separate explicit command and the personal
deployment identity checks in `DEPLOYMENT-OWNERSHIP.md`.

After the complete path passes the separate human release gates, explicitly
activate it in the owner path editor. Select the current explanation to replace;
activation binds the exact released spec/video/bundle and old IDs. Release alone
does not activate a replacement. Old aliases then resolve to the new active head,
while earlier media and private conversations remain available at their original
IDs. Unreleased or stale replacements are rejected.

## Public learning previews

The owner separately authorized a no-login public demo on2026-10-22. In public
mode, use the owner path editor's Public Preview control to expose a completed
native core and its exact attached nodes as review drafts. This permission binds
the current spec/video/bundle and node artifacts; it does not fabricate human
review passes, activate a replacement or send release notifications. Revocation
or a changed binding removes preview access. Owner administration stays protected.
See [ADR0008](architecture-decisions/0008-public-preview-and-anonymous-sessions.md).

The same operation is available through authenticated
`GET /api/v1/owner/lessons/{id}/public-preview` and
`PUT /api/v1/owner/lessons/{id}/public-preview`. GET returns the current candidate
and saved permission. PUT requires `enabled` and the exact `spec_sha256`,
`video_sha256` and `bundle_sha256`; revocation uses the saved permission's binding
so it remains possible after artwork changes. Public preview is an explicit
owner operation, never an automatic side effect of import.

## Evidence and limits

The exporter uses actual factory checkpoints, including each reduced-motion
pose, causal change and reviewed control case. It rejects unsupported SVG,
unapplied attribute updates, stale source, different metadata, changed media
and mismatched speech plans. Proof, source, spec and video hashes are retained;
failed encodes never replace completed output. Build verification is read-only:
`npm run build` checks registrations and never re-registers changed artwork.
It also checks Vercel upload traversal for every required source and parent
directory. A child inclusion cannot recover a directory already pruned by the
uploader; retain both the unsuffixed kit-directory exception and its descendants
in `.vercelignore`. The Linux function verifier additionally checks the shipped
MIT notice. Local packaging alone does not verify the CLI's source selection.

Import, composition, technical review, craft/accessibility, beginner learning and
release remain separate operations. Structural and model checks cannot certify
truth or infer human understanding. The current twenty curated review cores
remain intact; this bridge alone does not upgrade their artwork or release them.

Local authoring/export performs no paid API calls. That does not erase historical
Claude artwork costs, earlier failed calls or human production/review time.
Completed playback uses no model call; optional live chat retains its existing
server budget and receipts.
