# Narrated video production

Use this for an explicit video request. Heptabase Explainer Studio does production;
the host agent does authoring. It is usable from Claude Code or Codex with a shell;
it does not require changing the app's AI provider or giving customers an API key.

## Capability and cost check

Run `explainer-studio doctor --json` and `explainer-studio guide`. Read the matching
runtime's file-format, teaching and rendering guidance before writing a series.
Use the reviewed installed version for an existing project; record its version.
Upgrading dependencies is a separate action, not a prerequisite for every revision.

If missing, explain the dependency footprint (ManimGL, ffmpeg, LaTeX and fonts),
then use the official [Heptabase plugin](https://github.com/heptameta/heptabase-agent-plugins)
and [Studio source](https://github.com/heptameta/heptabase-explainer-studio).
The evaluated runtime was 1.3.0 at commit
`60a1482fb2cbd231e89b4071157efa3a77e80dcd`; it is a reproducibility pin, not a claim
that this remains the newest version. Follow the current installer only after
source inspection and authorization for the installation. Do not pipe unreviewed
remote scripts into a shell or alter the app's Python environment.

On macOS, the default zero-paid-speech plan is:

```yaml
narration_budget_usd: 0
narration:
  provider_name: macos-say
  voice: Samantha
  words_per_minute: 165
background_music:
  provider_name: none
```

Check the voice is actually installed. On another OS, keep narration unset and
offer a storyboard or an explicitly configured local voice. Do not silently switch
to paid speech. The helper's zero narration budget is not a hard cap on model
subscription usage or all external spending. Report those scopes separately.

For a Claude subscription session, verify account/authentication and avoid API-key
overrides. Paid usage credits are a separate account setting: do not claim no
extra charge without billing evidence. The host's reported model and token/cost
receipt are evidence; an API-list-price estimate is not an invoice. The same
distinction applies to Codex/ChatGPT plan usage versus API billing.

## Produce one complete explanation

1. Read supplied sources. Define a single question, audience assumption, causal
   spine, misconception and transfer rubric in the shared project brief/claims.
   Infer a short scope when the user asks for a quick explanation. Do not inflate
   the core to answer every optional follow-up.
2. Write the Studio plan, design and script. Prefer one running example. Let the
   selected presenter's playbook guide composition; do not blend imitation styles.
   Keep a proposed plan review when needed; existing explicit production approval
   satisfies the starting authorization instead of asking it again.
3. Use fresh audience-review contexts as the runtime requires. In Claude Code use
   Agent; in another capable host use its equivalent. If unavailable, record the
   missing check and stop before a gate that requires it; never fabricate records.
   Keep automated review distinct from a real learner test. Three rounds do not
   mean unresolved confusion is accepted.
4. Narrate with the chosen local voice; author scenes/cover/credits/cards using
   the actual ManimGL scene kit. Use `preview`, inspect every listed sheet/frame,
   fix errors, then `render`. No copied replacement renderer or invented success.
5. Check final media, narration, captions, cards and static explanation against
   the current script. **A parallel notes writer can retain an obsolete claim.**
   Any script or scene change after rendering requires the affected narration,
   preview/render and parity checks again before delivery. Preserve review history.
6. Run `notes check`, then `deliver`, then `video open --no-browser`. Verify actual
   browser playback and caption/seek behavior when tools are available. Retain
   editable production sources, a revision-bound receipt and unresolved issues.

For “both”, keep the interactive and video outputs in the same project and map
their checkpoints explicitly. Matching titles or schemas do not prove parity.
Do not claim ManimGL video is an interactive Anatomy SVG or a live chat artifact.

## Review focus for computing examples

Read `computing.md`. In ordinary causal-transformer inference, distinguish a token
that has been sampled from one that has been processed. The first output token
comes from prefill; its K/V exists only after it is processed as a new input.
Attention includes the current position's own K/V plus allowed earlier positions.
Specify the token-count convention and state workload assumptions. More tokens
alone do not establish an exact runtime ratio. Illustrative timeline widths,
probabilities and hardware dots must not masquerade as measurements.

## Finish with an honest receipt

Record runtime/model identities when observed, output paths/hashes, actual audio
and caption checks, speech charges, API-equivalent estimates, subscription usage,
and billing unknowns. Keep private model transcripts outside the public package.
After a timeout, inspect saved state before deciding on a paid retry; do not assume
zero billing. Export/playback does not make AI calls.

Publishable source examples live in the repository's
`experiments/prefill-decode-video/`; rendered media and private sessions are local.
The example illustrates production structure and known review limitations, not a
certified teaching result or an automatic public-library ingestion path.
