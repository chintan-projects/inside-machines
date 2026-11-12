# ADR 0009: one reusable entry point for local explanations

Date: 2026-11-11. Status: owner-requested implementation; local workflow, no live
provider or lesson-publication change. Extends ADRs 0001, 0003–0005 and 0007.

The owner asks unfamiliar questions in Claude and ChatGPT, wants to explore an
answer further, and wants an optional compelling narrated video. Remembering an
engine/plugin name, reconstructing prompts and finding an ignored experiment
directory are friction before the learning starts. The new unit is a continuing
explanation project, not another marketplace backend.

## Decision

`explain-visually` is the stable entry point. Interactive HTML/SVG is the default;
explicit video requests use Heptabase Explainer Studio / ManimGL; “both” shares
claims/example/storyboard with explicit output-parity checks. “Dive deeper” and
format conversion first inspect the existing project. Anatomy remains the physical
craft dependency, not a container for video production or fictional hardware
metaphors for algorithms. Host model/account selection remains explicit.

Version the canonical skill in `plugins/inside-explain/skills/explain-visually`.
Package it for Claude Code and OpenAI skill/plugin hosts, with no MCP service,
account connection, lifecycle hook or hidden paid call. Shared local installation
points Claude/Codex discovery at that source; existing custom skills are backed
up only on an explicit replacement operation. Plugins carry the same content and
are refreshed by their host's normal package-update lifecycle.

A small deterministic helper creates the local brief, claim ledger, review record
and versioned manifest. It neither calls models nor certifies quality. The existing
host does authoring; Studio does video production; the app's shared services,
provider gateway, budgets, owner operations and publication gates remain unchanged.

## User experience and cost

The first interaction names the question and a reasonable inferred starting level,
then progresses to a complete causal explanation. Optional insight/model depth
cannot repair a missing core. Renderer choice is not an onboarding questionnaire.
Local projects persist the same example and evidence so a later agent can continue.

Use free local narration by default where available and keep speech budget at zero.
Missing capabilities produce a truthful storyboard/handoff, never a hidden paid
fallback. Model subscription usage, API-list-price estimates, verified charges and
unknown billing are separate fields; the narration budget is not a global account
cap. Browser/video playback is independent of model calls.

ChatGPT desktop/Codex with shell access can run local production. Chat-only
surfaces use the same teaching instructions and export content when supported;
skill installation does not grant shell access. Repo-local marketplace discovery,
public ChatGPT directory submission and web/mobile availability are distinct.
No directory publication is claimed in this implementation.

## Verification and boundaries

Test actual install/update preservation, project continuation, path boundaries,
speech defaults and clean ZIP contents. Validate the host manifests and skill,
install on both supported local hosts, and run the project's required regressions.
The editable prefill/decode example retains real review limitations and excludes
private sessions, downloaded articles and rendered media.

Skill tests do not evaluate model output quality. Keep engineering, technical,
craft/accessibility and beginner learning evidence separate; do not infer acceptance
from a renderer's checks or three model-review rounds. No published app schemas,
artifacts, conversations or provider routes change. A future library-ingestion
adapter needs its own explicit artifact binding and review gates.

## Product hypothesis

A returning user can start in one sentence and continue a saved explanation from
either local host without reconstructing prompts or re-entering source context.
Test the first interactive request, follow-up depth and conversion to video; count
unnecessary setup questions and lost context. No uncoached usability or learning
result is claimed by the deterministic helper tests.

Sources: [OpenAI skills](https://learn.chatgpt.com/docs/build-skills),
[plugin packaging](https://developers.openai.com/plugins/build/plugins),
[Claude Code plugins](https://code.claude.com/docs/en/plugins-reference),
[Heptabase Studio](https://github.com/heptameta/heptabase-explainer-studio).
