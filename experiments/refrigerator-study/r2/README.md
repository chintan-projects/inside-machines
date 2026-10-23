# Refrigerator R2 reference slice

This is a new, private craft candidate, with the actual Anatomy isometric solid and
tube toolkit behind a trusted TypeScript factory. It keeps the R1 cue plans and
pure refrigeration rules unchanged. No generated JavaScript response is evaluated.
The original R1 source and packed HTML remain historical records.

`index.ts` exports `refrigeratorR2Definitions(narrations?)`,
`createRefrigeratorR2Lessons(narrations?)`, `refrigeratorR2Metadata` and
`refrigeratorR2Path`. Each definition pairs the real shared-player lesson with a
data-only `native-studio-1` v3 specification. The hosted exporter must inject its
source fingerprint; the empty source placeholder is deliberately not publishable.

The reusable boundary is the lesson factory, cue/claim/control metadata, shared
player, source binding and publication proof. Refrigerator geometry and truthful
domain rules remain specific. A GPU does not become a refrigerator-shaped diagram.
The core is complete before the energy-accounting and cold-boiling branches.

Build a separate, reversible local preview:

```sh
node experiments/refrigerator-study/r2/build.mjs
python3 -m http.server 8073 --directory .vercel/refrigerator-r2/public
```

The first command attaches no audio. With `--reuse-audio`, it verifies and reuses
the existing local R1 computer-speech assets against the exact unchanged narration
plans and media hashes. It neither synthesizes speech nor calls a model. That
option requires the ignored local assets to be present. The shared player supplies
sound-off captions, explicit playback, keyboard controls and reduced-motion poses.
The local build writes only `.vercel/refrigerator-r2/public/index.html` and checks
that the old packed R1 hash has not changed.

Run the focused verification:

```sh
node --test experiments/refrigerator-study/model.test.mjs experiments/refrigerator-study/r2/geometry.test.mjs
```

The focused tests exercise real native frames through the backend's SVG boundary,
actual focus/core labels for every authored control case, cue identity, visual
changes, physical route joins, the unchanged fixed-length rod, stopped pumping,
energy accounting and the pressure comparison. They do not establish visual taste,
technical certification, physical-device accessibility or beginner comprehension.

The artwork uses the actual kit and depth-sorts actual volumetric tube spans and
solids. A complete `kit/audit.mjs` collision, support and occlusion proof has not
been supplied. Endpoint continuity tests are a narrower check. Human technical,
actual-phone and five-learner transfer reviews remain required; this candidate
must stay held until the artifact-bound gates are satisfied.
