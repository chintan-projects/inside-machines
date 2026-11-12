---
name: explain-visually
description: Explain a concept, system or code change with a local interactive visual or narrated explainer video. Use for requests to visualize how something works, dive deeper into an existing explanation, or turn it into a video.
---

# Explain Visually

Help a curious person see the mechanism, explain it in their own words and predict
what changes in a new situation. The entry point is the same in Claude Code,
Codex and ChatGPT; available execution tools determine what can actually be built.

## Choose the experience

Infer the mode from the request, without an engine-selection questionnaire:

- **Interactive** is the default: one local HTML page with inline SVG, a useful
  cause-and-consequence control, a reset and a sound-off explanation.
- **Video** when explicitly requested: a narrated, captioned video made with
  Heptabase Explainer Studio / ManimGL. Read [video.md](references/video.md).
- **Both** only when requested: share the question, claims, example and causal
  storyboard; changes must reach both outputs. Separate implementations are not
  automatically synchronized. Verify their checkpoints explicitly.
- **Continue** for “dive deeper”, a correction, or “turn this into a video”:
  inspect the existing project first. Preserve its sources and stable example;
  add the missing relationship or a new revision instead of starting over.

On a chat surface without filesystem/shell access, read
[chat.md](references/chat.md). Do not claim to have installed tools, rendered a
video, updated a local file or opened a Claude artifact there. Do not silently
switch to another model, a hosted service or a paid API to overcome missing tools.

## Ground the explanation

Start from the user's actual question. Infer a reasonable starting level and state
the assumption; ask only for information that materially changes the explanation.
Pick one observable takeaway, a falsifiable learning hypothesis, a plausible
misconception and a changed-situation transfer question with its answer rubric.

Build the complete input → operations/dependencies → useful output chain before
adding optional depth. Source consequential claims from actual code or primary
references. Separate documented facts, illustrative numbers and inference.
Never invent measurements, source quotations, model internals or review results.

Use Grant Sanderson's purposeful visual reasoning, Feynman's plain causal language
and Veritasium's prediction/misconception work as decisions, not creator imitation
or endorsement. Motivate a technical name by showing its job first. Each beat
shows the same operation that the narration describes. Prediction is optional;
hold its answer until the reveal, then test transfer before revealing that answer.

## Pick an honest representation

- **Physical mechanisms:** use the actual Anatomy skill and kit, including its
  craft/geometry references and the closest shipped example. Locate `anatomy`
  among installed skills or a trusted checkout's `vendor/anatomy`. Read its
  `SKILL.md`, `references/craft.md` and `references/kit.md`; use the real kit rather
  than imitating it with generic boxes. If missing, explain the dependency and
  use the installation instructions in [interactive.md](references/interactive.md).
  Do not call an unverified schematic accepted Anatomy craft.
- **Software, GPUs, LLMs and algorithms:** show real values, operations, state and
  dependencies. A physical metaphor or hardware locator must not replace the
  computation. For inference, read [computing.md](references/computing.md).
- **Code changes:** inspect repository instructions, status, the actual diff/base,
  callers and tests. Trace one input before and after; state what changed and what
  is preserved. For new behavior, say it was absent rather than inventing a broken
  predecessor. Do not run arbitrary changed code merely to illustrate it.

Essential parts need readable, anchored labels. Motion, arrows and colors carry
declared meaning; reinforce color with words or shape. Keep causal rules outside
the drawing. A meaningful interaction changes the cause and all dependent views,
not just animation speed or highlighting.

## Save work that can be continued

For local work, use this skill's `scripts/project.mjs` to create a project:

```sh
node <skill-directory>/scripts/project.mjs init <slug> --mode interactive --topic "The user's question"
```

Default output is `.explainers/<slug>/` in the current workspace. The helper
creates a brief, claim ledger, review record and `explanation.json`; video projects
also have a Studio series skeleton. It makes no model calls, installs nothing,
and never overwrites an existing project. Read `--help` for `status` and `doctor`.
An existing user folder/layout takes precedence; do not move it merely to comply.

Fill the brief and claim ledger before drawing. Use the manifest to record actual
output paths, revision, model identity when known, and evidence. Keep unresolved
reviews explicit. Put generated outputs and private session material in the local
project; do not automatically commit, publish or upload them.

## Cost and execution boundaries

Use the current host model/account unless the user selected another. A skill does
not authenticate a model or authorize a new API charge. Explain any required
change before invoking a different account/provider. No keys belong in prompts,
HTML, receipts or logs. Never read `.env` merely to make a local explanation.

Interactive playback and exported video playback make no AI calls. Default to
free local narration on supported systems; paid speech requires an explicit
provider and budget. Never infer an invoice from a CLI API-equivalent dollar
estimate. Record subscription usage, API-equivalent estimates, verified charges
and unknown billing separately. Never silently retry an uncertain paid call.

## Review and hand off

Inspect the actual rendered output, not only source. Exercise controls, seek/reset,
keyboard and sound-off behavior; review narrow layouts and reduced motion where
supported. For video, follow Studio's screenshot and delivery checks. For Anatomy,
run applicable kit checks before claiming geometry validation.

Fix the most consequential confusion first. Keep source correctness, engineering,
craft/accessibility and beginner learning evidence separate. An automated review
or three review rounds is not human acceptance. State any remaining confusion;
do not silently label a draft approved.

Deliver the artifact link, the main insight, observed checks and material limits.
Make the next action obvious: “ask a follow-up here”, “dive deeper”, or “make a
video”. Clarify that follow-up conversation lives in the agent session unless a
working embedded chat was explicitly built. Keep a static/transcript alternative
and preserve prior revisions when iterating.
