# Prefill and decode — complete reference draft

One prompt, two choices: “The sky is → blue → and.” The interactive page and narrated film share a deterministic two-layer toy computation and a canonical story. This is a local reference awaiting owner and unfamiliar-learner acceptance; it is not a validated teaching result or a live app update. Earlier revisions and their failed audience reviews are preserved.

The core answers why known prompt positions can be processed together within a layer while ordinary generation needs the selected token fed back before the following selection. Optional depth exposes actual attention and feed-forward calculations, causal-mask edits, cache on/off and logical batching. These are illustrative computations, not measurements of a real chatbot or GPU. The fixed toy stops after two selections.

## Run it

From this directory:

```sh
node build.mjs
node tests/invariants.mjs
```

Open `interactive/index.html` for the interactive explanation. The film is a separate local asset and requires the render/delivery steps below. “Dive deeper” opens prepared views; follow-up AI conversation lives in Claude Code or Codex. The page has no embedded model or API key.

For the film, use the reviewed Explainer Studio 1.3.0 runtime and read the [video skill](../../plugins/inside-explain/skills/explain-visually/references/video.md). The included plan explicitly selects ElevenLabs and a $1 **speech-estimate** budget. This is paid generation, not a cap on subscriptions or all account billing. Supply your own authorized credential through Studio's environment, or use the skill wrapper with an existing owner Keychain preference:

```sh
explainer-studio script validate ep01 --series video
explainer-studio preview ep01 --series video
# Inspect every listed screenshot before production.
node ../../plugins/inside-explain/skills/explain-visually/scripts/project.mjs studio narrate ep01 --series video
explainer-studio preview ep01 --series video
# Inspect again with actual narration timing.
explainer-studio render ep01 --series video
explainer-studio notes check ep01 --series video
explainer-studio deliver ep01 --series video
node review.mjs --port 8879
```

Open `http://127.0.0.1:8879/` for the interactive page, narrated film, actual-timeline chapter buttons, captions and transcript. The server serves only the review assets, supports byte-range video seeking and does not expose the project folder. Playback and controls make no AI calls.

## Continue it

Edit `lesson/story.js` for narration, visual beat descriptions, prediction, assessment and follow-up routing. Edit `lesson/mechanism.js` for toy rules; `lesson/checkpoints.js` derives both media's states. `build.mjs` generates the script, Python state data and inline app. ManimGL scenes consume those generated values; the SVG app uses the same pure module.

Changing narration invalidates affected cached speech. Changing script or drawings requires the affected audience read, preview/render and parity checks again. Keep the review history; never turn a model review into a human acceptance claim. The [review packet](review/HUMAN-REVIEW.md) separates engineering, technical, owner craft and learner evidence. Generated media, private authoring sessions, credentials and participant answers are excluded from Git.

## Observed production result

The delivered local film is **6:19**, with 38 speech segments and 166 caption cues. Speech is **$0.37176 estimated** for this iteration; actual provider charges are unverified. Initial Claude authoring reported $5.5935764 API-equivalent, not an invoice; host editing/review usage is not measured. See [the revision-bound review](REVIEW.md) and [receipt](review/receipt.json).

The proposed 4:10 plan grew to 800 words/38 beats. Automated readers still flagged layers, next-token selection, saved K/V and caching as confusing. This is a concrete testable draft, not acceptance of that extra length or proof of learning. Full arithmetic lives in optional depth; a human check must establish whether the core is sufficient.

Frozen automated readings live in `review/audience/round-XX.json`. Build seeds Studio's required YAML from these genuine records only when that file is absent. Subsequent local reads must be retained; build never overwrites them. The runtime's combined review file is generated and ignored.
