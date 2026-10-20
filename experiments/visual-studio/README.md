# Local visual studio

Reusable standalone player for carefully authored concept studies. It shares a
typed lesson/scene contract, manual playback, pause/replay/reset/seek, responsive
labels, qualitative controls, optional predictions/transfer, source disclosure and
embedded narration with synchronized captions and safe local packing. GPU is the first consumer of this extracted shell. The earlier
vacuum artifact remains immutable and uses its original player; it has not been
quietly relabeled a generic engine. Both use the same actual Anatomy toolkit and
existing provider/gateway/accounting/checkpoints. No new model gateway or queue.

Each concept supplies a pure mechanism, storyboard data and a trusted reviewed art
adapter. The shell has no GPU arithmetic, task readiness or provider knowledge.
Renderers supply stable content identities and scoped attribute updates so progress
does not remount arithmetic labels every frame. Only trusted rendering adapters
choose these visual updates; the domain state stays pure.
The toy scheduler lives in `../gpu-study/model.ts`; physical concepts will supply
their own rules instead of being forced into execution lanes. This contract is a
local spike, not a new version of the public LessonSpec or an automatic catalog
generation feature. Generated code never enters the production app.

Add a lesson by filling the worksheet/claims/hypothesis/transfer rubric; create a
typed domain module and scene adapter; register a trusted build entry; budget
authoring through the existing gateway; inspect and hash-bind its output; then run
engineering, source, three-width craft, actual-device and beginner reviews. Never
infer acceptance for a new domain from the vacuum or one passing test suite.

```sh
node experiments/gpu-study/finish.mjs
node experiments/gpu-study/narrate.mjs
node experiments/visual-studio/build.mjs gpu
.venv/bin/python -m http.server 8068 --bind 127.0.0.1 --directory .vercel/visual-studio/public
```

Open `http://127.0.0.1:8068/gpu/`. Only the public directory is served. The page is
one self-contained HTML file, with no playback API requests, storage or telemetry.
Use `?render` for stopped-clock review; `window.seek(t)` is deterministic. The
`window.lessonStudio` inspection API exposes play/pause/reset/setControl/getState.
“Watch & listen” starts embedded computer narration after a deliberate click.
The media clock drives the full tour and captions. Pause/seek/reset/mute work
without network access; changing an experiment stops the fixed narration.
Reduced motion uses a reviewed still per cue while speech continues. Media failure
is visible and requires deliberate retry. No device volume settings are changed.
The cue plan is the single source for script, captions and stills; build rejects
stale audio hashes. Local synthesis needs Node 24, macOS `say`/Samantha and FFmpeg;
it fails if words exceed their allotted scene. Synthesizing/viewing incurs no API
cost. The packed HTML needs none of those authoring tools or browser speech voices.
Private API receipts, ledger, original response, derived source and screenshots
stay ignored under `.vercel/claude-vacuum/private`. Do not reset its ledger.

```sh
node_modules/.bin/tsc -p experiments/visual-studio/tsconfig.json
node_modules/.bin/eslint --config experiments/visual-studio/eslint.config.mjs experiments/visual-studio experiments/gpu-study
node --test experiments/gpu-study/model.test.mjs experiments/visual-studio/narration.test.mjs
```

The build rejects unknown registry entries, unsettled/mismatched source hashes and
unsupported execution/network patterns, embeds vendored MIT provenance, and denies
network, frames and workers through CSP. Only embedded `data:` media is allowed.
These checks are defense in depth for
manually inspected local authoring, not a safe arbitrary-code sandbox. A future
production adoption must translate the craft into trusted declarative adapters,
preserve publication/quality gates and align narration/video/static checkpoints.

## Complete core and optional depth (GPU-S3)

The page now consumes `learning-path-1`: core, insight and model nodes reference
trusted lessons, questions/outcomes, prerequisites, forward edges and reviewed
query aliases. `path-player.ts` owns navigation and ephemeral mounted-player state;
returning restores the paused scene and optional answers, with a consistent mute
preference. No automatic replay or model call occurs on navigation. Reload begins
the linked node afresh. Unknown/ambiguous questions report missing coverage.

`backend.learning_paths` supplies the same versioned planning schema, validation
and a provider-neutral `path_prompt`. `backend.prompts.path_node_prompt` reuses the
existing lesson author/evidence contract, adding the root question, shared example,
node scope and prerequisites. The author recovery policy fingerprints those rules.
Planner and node-author helpers prepare requests; they do not create another
provider, bypass reservations or enable a production path-generation endpoint.

The build validates real path JSON in both Python and TypeScript, rejects unknown
lesson refs/cycles/unreachable nodes, and emits `learning-path.schema.json` for API
integration. A vacuum structural fixture proves the envelope has no GPU-specific
fields; it is not a new vacuum lesson. Topic-specific arithmetic/physics and drawing
adapters still need authoring and review. Current GPU depth is deliberately authored,
not evidence that arbitrary AI-generated topics achieve this quality automatically.

```sh
node experiments/gpu-study/narrate.mjs
node experiments/gpu-study/narrate-depth.mjs
node experiments/visual-studio/build.mjs gpu
node --test experiments/gpu-study/*.test.mjs experiments/visual-studio/*.test.mjs experiments/shared/*.test.mjs
```

To revoice just one reviewed node, pass its plan ID to `narrate-depth.mjs`. Each
cue is checked against its scene duration; the build binds every embedded track
to the script hash. The four-track single HTML is about 4.4 MB, with no network
needed after loading. No MP4 export, hosted publication, universal simulation or
arbitrary AI follow-up generation is claimed. See ADR 0004 and the GPU-S3 journal.
