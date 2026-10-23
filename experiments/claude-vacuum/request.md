# Deliver the strongest single candidate

You are the author and visual designer for this local Claude + Anatomy trial.
The owner rejected all four prior examples as ordinary. We have deliberately NOT
included any old artwork/layout. Use the supplied brief and the actual Anatomy
documentation to create your own compelling physical illustration and explanation.
Make an experience someone wants to touch and explore, not a technical dashboard.

Use the original Elvar article's practical moves, adapted to this machine: let
actions operate or reveal the object, keep the working window large, put a single
brief hint beside the visible effect, and finish on one clear causal takeaway.
Prefer action verbs (turn on, follow the air, inspect the bag) to abstract chapter
names. Keep a manual path and an optional continuous tour. Do not falsely imply
that fan, inlet and collection operate one after another. A hand-made physical
finish with material-specific shading and short neutral/warm shadows can carry
delight; avoid the earlier blue-grey schematic. Choose your own tasteful palette.
No need for mascots, decoration or arbitrary sliders to demonstrate complexity.

Return ONE complete standalone HTML document, beginning <!doctype html>. No
markdown fences, analysis or extra files. Keep below 600 source lines. Give the
visual the space and purpose it deserves. Mobile first, tasteful on desktop.
Use compact reusable geometry helpers and loops rather than huge unrolled markup.
Aim for ~45 seconds of optional playback and an equally good stepped/still view.
Use short plain copy, clear play/pause/replay, optional depth and one prediction
experiment. No narration API/audio dependency is needed for this first craft trial;
sound-off visual explanation must work independently. Be explicit that this is a
generic bagged cleaner, a qualitative explanation and a local teaching draft.

The build inserts an ACTUAL bundled Anatomy library before your scripts, replacing
the exact marker <!-- ANATOMY_RUNTIME --> in your head. Include that marker once.
Use `window.Anatomy.k`, `window.Anatomy.G`, `window.Anatomy.T` as namespaces:
- k: actual iso-kit.mjs, including ISO_CSS, fitProjection, iso, slabOf, cylinder,
  extrude, solidSvg, lineSvg, dotsSvg, pathOf, figureSvg and the other documented API.
- G: actual lathe.mjs, frameAlong, frameOf, pointOf, disc, ringBand, lathe, sphereOf,
  prismOf and other documented API. Check signatures: G.disc(s0,s1,r,F,P),
  G.ringBand(s0,s1,rIn,rOut,F,P), G.lathe(profile,F,P).
- T: actual tube.mjs, tubePieces/tubeSvg. Inspect documented signatures.
These are not invented replicas. Use actual k/G geometry for meaningful parts.
Inject k.ISO_CSS into a style element if using solidSvg, then choose coherent
--anatomy-* token overrides. Normal SVG/CSS/JS can complement the kit for labels,
flow and controls. Do not assume k exports functions from G or T.

No imports, external fonts/assets, fetch, localStorage, analytics, service worker,
eval, remote requests, form submissions or browser speech. A network-denying CSP
will be inserted. Text content uses no personal data. Buttons must be semantic,
touch targets ≥44px, keyboard focus visible, respect reduced-motion and work at
390/768/1280 widths. Avoid hiding the main Play action below a tall figure on phone.
Air and dirt differ by shape/direction as well as color. Large on-scene labels with
short leaders are REQUIRED overrides to upstream Anatomy. Readability beats tiny
engraving, and label collisions or an arrow drawn through a motor fail the trial.

Expose `window.vacuumStudy` with `seek(seconds)`, `play()`, `pause()`,
`setBlocked(boolean)`, `reset()`, `getState()`; getState returns time/playing/blocked/
beat plus a human-readable account of airflow/dirt state. This is an observation
hook, not a physics engine. Keep causal rules in one pure state function and have
all controls, text, stills and motion consume it. Never autoplay on page open.
Include sources/scope in an unobtrusive disclosure. Do not claim geometry audit,
scientific certification, human approval or proven learning.
Also expose window.seek(seconds) as an alias and honor ?render by keeping the
clock stopped. Seeking must reconstruct ANY frame in ANY order independently;
we will render chapter midpoints and scan motion for unintentional discontinuity.

Spend your effort on physical coherence, visual storytelling and elegant mobile
composition. Meet the brief, then make a concrete design decision of your own.
