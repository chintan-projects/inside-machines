# ADR 0007: publish trusted native visual lessons as their own artifact format

Date: 2026-10-22. Status: implemented for owner review; lesson release pending.

The selected local Claude/Anatomy workflow creates source-authored physical
figures and computational views. Hosted CE-1 authoring instead returns bounded
primitive geometry. Converting eight real refrigerator cues into fake Parts and
Changes would lose the artwork and misstate what was reviewed. A stronger prompt
cannot remove that format boundary.

Add `native-studio-1` as lesson version 3. Keep v1/v2 parsers, published specs and
hashes unchanged. Reuse the existing player, path envelope, media clock,
discussion, feedback, offline saving and artifact-bound review operations.
Topic modules own truthful domain state and a trusted renderer; the player does
not infer physics or manufacture a cutaway for a logical computation.

Native metadata describes actual components, cues, inputs/outputs, evidence,
assessments and control cases. Executable code comes only from a finite compiled
repository registry. API data cannot name arbitrary modules, URLs, credentials
or scripts. The registry binds exact renderer source, semantic spec and revision
identity. A read-only build gate rejects stale source or altered metadata;
registration is a separate explicit owner operation.

Production is local and owner-operated: author → render/critique → register →
export synchronized speech/video/checkpoints → verify → import a held draft.
Import does not attach a graph, replace a public lesson, run paid authoring,
approve review or notify requesters. Existing owner path, review and release
operations remain explicit. Native paid revise/depth calls reject with local
production guidance until a real operation exists.

Replacing an existing library entry requires a separate owner activation after
release. It binds exact artifacts/bundle and explicit old IDs, atomically records
the new head, and preserves old media/chats and alias resolution. Import and
release never silently activate a replacement.

Proof uses the actual trusted factory's default, reduced-motion and control
states. It rejects unsupported SVG, missing focus labels, unchanged causal
geometry, mismatched narration, source/spec/media hashes and unsafe references.
The same state/render functions supply the video. Completed media is installed
atomically; unknown or failed exports cannot fabricate success.

Previously released media and private conversations stay readable if a renderer
is retired. The client then preserves original media/text rather than inventing
a substitute drawing. Historical release identity cannot approve changed media,
a new lesson or a different attached bundle.

Refrigerator R2 tests physical production; GPU memory R1 tests one logical insight
through the same bridge. This does not upgrade the other review drafts, establish
accepted Anatomy craft or prove transfer to every topic. Technical truth,
craft/accessibility, actual-device behavior, beginner understanding and owner
release remain separate evidence under ADRs 0001–0006.
