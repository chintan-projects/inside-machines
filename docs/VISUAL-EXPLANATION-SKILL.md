# Explain Visually: a reusable local learning workflow

The versioned source is
[`plugins/inside-explain/skills/explain-visually`](../plugins/inside-explain/skills/explain-visually/SKILL.md).
It supports interactive explanations, explicit narrated-video requests and
continuation/deeper questions in the same project. See
[ADR 0009](architecture-decisions/0009-local-explanation-workflow.md).

## Install and invoke

From the repository:

```sh
node scripts/install-explainer-skill.mjs
```

Existing custom skills are preserved. To update an earlier installation, use
`--replace`; the installer backs it up outside skill-discovery roots. `--check`
is read-only. The installed Claude and Codex skills resolve to the same canonical
source, without edits to model, account or billing configuration.

Start a new agent session, then:

```text
Claude Code: /explain-visually Explain how a heat pump moves heat.
Codex:       $explain-visually Explain prefill versus decode.
Follow-up:   Dive deeper into why that happens.
Video:       Turn this explanation into a short narrated video.
```

The [plugin README](../plugins/inside-explain/README.md) covers Claude/OpenAI
marketplace installation. Select the installed **Inside Explain** plugin in
supported ChatGPT surfaces. A repo-local plugin is not a globally published
ChatGPT directory listing, and installation does not grant local shell access.
For a chat-only surface, use the packaged
[starter/handoff](../plugins/inside-explain/skills/explain-visually/references/chat.md).

## What stays shared

The question, audience assumption, primary sources, claim ledger, causal
storyboard and transfer rubric govern every output. Physical illustrations use
the actual Anatomy kit; computation uses honest data/dependency views. Explicit
video requests use Heptabase Studio / ManimGL. The upstream Anatomy skill itself
is not modified or filled with video-production responsibilities.

The helper creates `.explainers/<slug>/` with a brief, claims, review record and
`explanation.json`. It never calls a model or overwrites an existing project.
“Dive deeper” continues that context; changing format requires checking that
state, narration, captions, cards and interactive output still agree.

Speech defaults to a zero-paid-API budget and an available local voice. A model's
subscription allowance, API-equivalent cost estimate and actual account charges
are different things. Paid overage settings are not inferred from a session's
reported dollar figure. Playback is independent of model calls; authoring uses
the explicitly selected host account/provider.

## Evidence and historical context

The original 2026-10-22 installation shared an owner-local custom skill between
Claude Code and Codex. Its local exercise of the `6c78275` client change observed
identity reuse, explicit replacement, separate intents, reset, keyboard use and
a 390px layout; the Anatomy dial-indicator example also changed its readout. That
was a self-applied workflow check, not a fresh model or beginner evaluation.

The 2026-11-11 [prefill/decode experiment](../experiments/prefill-decode-video/README.md)
adds real video production evidence and known failures. Its editable source is
committed; generated media, source-article downloads and private transcripts stay
local. Three model-review rounds did not establish comprehension. The example
records source corrections and remaining craft/learning limitations.

The first-class package adds deterministic tests for install preservation,
continuation state, path validation, speech defaults and clean release ZIPs.
Host manifests and actual local discovery are checked separately. None of these
tests certify model output quality or accept a lesson for live publication.
See the [current verification record](LOCAL-EXPLAINER-VERIFICATION.md) for observed
checks and the remaining external and learner evidence.
