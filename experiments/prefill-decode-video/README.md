# Prefill versus decode — editable video example

Source for the local 2026-11-11 Heptabase Explainer Studio experiment: **Why does
AI write one token at a time?** The rendered example was 5:48, 1920×1080 H.264/AAC,
with English captions and free macOS Samantha narration. It was a review draft;
the owner has not accepted its craft or learning quality.

`production/` contains the actual six ManimGL scenes, shared drawing primitives,
plan, script, cover, credits, chapter cards, design and model-review records.
Rendered media, narration caches, account identity, raw agent transcripts and
downloaded source articles are deliberately excluded. The original local artifact
is preserved separately; committing this source does not publish that video or
add a lesson to the live marketplace.

## Reuse

Invoke **Explain Visually** in Claude Code or Codex and point it at this folder:

```text
Use explain-visually to continue this prefill/decode example. Read its sources
and review limitations first. Keep free local narration. Build a new local
revision, preserving the original example and never publishing automatically.
```

The local runtime evaluated here was Studio 1.3.0 at commit
`60a1482fb2cbd231e89b4071157efa3a77e80dcd`, with ManimGL 1.7.2. Runtime and
renderer source remain upstream; this is not a fork. Install/check them through
the [video workflow](../../plugins/inside-explain/skills/explain-visually/references/video.md).
Copy this source to a local working series before producing media; fetch/read the
linked primary sources and record changes. Existing model reviews are historical
evidence, not approval of a modified script.

In that working copy, the production commands are:

```sh
explainer-studio plan validate
explainer-studio script validate ep01
# Fresh review when changing the script; then free local narration and previews.
explainer-studio narrate ep01
explainer-studio preview ep01
explainer-studio render ep01
explainer-studio notes check ep01
explainer-studio deliver ep01
explainer-studio video open ep01 --no-browser
```

These commands do not themselves author a new script. The agent follows the
matching runtime guide and inspects actual rendered frames. Never manufacture
review records to bypass a gate.

## Evidence and limitations

The original production used Claude Opus 5.5 through a personal subscription.
Its CLI reported **$10.512594 in API-list-price-equivalent usage**, including
research, reviews and revisions; that number is not an invoice or a prediction
of future per-video charges. Account-level paid overage settings were not checked.
Speech API charges were $0. Rewatching the exported video makes no model calls.

Observed: genuine workflow through delivery, zero final automatic layout issues,
all final by-beat sheets and text-visibility frames inspected, browser playback,
caption/seek/keyboard operation, 185 ordered caption cues, −16.0 LUFS and −3.8 dBFS
true peak. A simulated 390px layout had no horizontal overflow; video labels are
small in portrait and better in fullscreen/landscape. App regression checks do
not establish teaching quality.

Source checks corrected self-attention to include the current token's own K/V,
distinguished sampled from processed tokens and clarified the end-token count.
An authoring error claimed fixed prefill pushed the total-time ratio below ten.
That was false: 99/9 decode steps is 11, and a fixed prefill alone does not determine
the total-time ratio. The video script and current cards now assert no ratio.
This card error also survived a parallel notes pass and had to be corrected.

Three model audience-review rounds still found confusion in cache reuse, GPU
memory/batching and the closing count/time reasoning. Subsequent corrections were
not re-read by a fresh reviewer. These records are simulated-reader feedback,
not human learner evidence. No independent human technical review, owner craft
approval, real-phone/screen-reader acceptance or beginner transfer study exists.
The exact earlier Token Timeline artifact was unavailable for a controlled A/B.

Reusable workflow source is [MIT licensed](LICENSE). Anatomy is MIT and Studio
has its own upstream license; their assets/source are not redistributed here.
