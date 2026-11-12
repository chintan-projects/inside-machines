# Inside Explain

Ask a question. See the mechanism. Keep exploring.

One skill, **Explain Visually**, creates an interactive explanation by default and
a narrated video when you ask for one. Use the same project to ask follow-ups,
go deeper or turn the explanation into another medium. Claude Code and Codex use
the same versioned instructions; no app backend or customer API key is required.

## Use it now

From this repository, install the shared local skill:

```sh
node scripts/install-explainer-skill.mjs
```

An existing installation is preserved. Use `--replace` to update it with a backup.
Start a new agent session after installing.

| Surface | Example |
| --- | --- |
| Claude Code | `/explain-visually How does an induction cooker heat the pan?` |
| Codex / ChatGPT desktop with local skill support | `$explain-visually Explain prefill versus decode.` |
| Installed Inside Explain plugin in ChatGPT | Select **Inside Explain** with `@`, then ask your question. |

Then say **“dive deeper into why that happens”**, **“show a concrete calculation”**,
or **“turn this into a short narrated video”**. The agent inspects the existing
project and preserves its example, claims and sources instead of starting over.

Interactive drawings use the actual [Anatomy](https://github.com/wheresryan22/anatomy)
kit for physical mechanisms. Computation uses appropriate data and dependency
views. Video uses [Heptabase Explainer Studio](https://github.com/heptameta/heptabase-explainer-studio)
and ManimGL. These are separate renderers behind one teaching workflow; no claim
of automatic cross-renderer synchronization or human quality acceptance is made.

## Plugin installation

Claude Code, from a checkout:

```sh
claude plugin marketplace add "$PWD"
claude plugin install inside-explain@inside-machines --scope user
```

Or add `chintan-projects/inside-machines` as the marketplace on a new machine.
The plugin command is `/inside-explain:explain-visually`; the short
`/explain-visually` command comes from the standalone installation above.

Codex CLI, from a checkout:

```sh
codex plugin marketplace add "$PWD"
codex plugin add inside-explain@inside-machines
```

The repo's `.agents/plugins/marketplace.json` also provides a local marketplace
for supported ChatGPT desktop surfaces. Refresh/start a new session to discover
it. Installation in a local desktop marketplace does not publish a global
ChatGPT web/mobile listing. Public directory submission remains a separate step.

For chat without local execution or this plugin, use the copyable
[chat starter](skills/explain-visually/references/chat.md). The same teaching
workflow can produce HTML/content there; a completed MP4 requires a capable
execution environment. Instructions cannot grant shell access or preserve
Claude-specific live-artifact behavior on another host.

## Local project and cost defaults

The agent creates `.explainers/<topic>/` with the brief, claims, review record and
`explanation.json`. Video mode adds a Studio series skeleton. The helper is
optional when continuing an existing folder; it never overwrites a project.

```sh
node plugins/inside-explain/skills/explain-visually/scripts/project.mjs doctor
node plugins/inside-explain/skills/explain-visually/scripts/project.mjs init cooker --topic "Why can a pressure cooker cook faster?"
node plugins/inside-explain/skills/explain-visually/scripts/project.mjs status .explainers/cooker
```

These commands make **no model calls**. Authoring uses the current host's account
and consumes its subscription allowance or configured API usage. No provider is
silently substituted. A CLI API-equivalent estimate is not a verified bill; paid
overage settings can still matter. Speech defaults to a **$0 narration budget**
and macOS Samantha when available. Other platforms need an explicit local voice
or an unrendered storyboard; paid speech never starts as a fallback. This speech
budget does not cap all model/account spending. Playback makes no AI calls.

No MCP server, Heptabase account, hosted backend or upload is required. The plugin
does not install its rendering dependencies or change account/billing settings
on load. Read [video mode](skills/explain-visually/references/video.md) for setup.

## Source and distribution

The [prefill/decode example](https://github.com/chintan-projects/inside-machines/tree/main/experiments/prefill-decode-video)
contains editable source, provenance and known review limitations. Media, model
transcripts, account identity and downloaded source articles are excluded.

```sh
node scripts/package-explainer-plugin.mjs
```

This creates an allowlisted skills-only ZIP under `.vercel/plugin-release/` for
future distribution. It does not submit to a directory or connect accounts.
The workflow belongs here; upstream Anatomy and Heptabase remain independent
dependencies with their own licenses. Our package is [MIT licensed](LICENSE).

Package/skill installation, native plugin discovery and deterministic helper tests
are different from end-to-end model-quality evaluation. See the repository's
[quality bar](https://github.com/chintan-projects/inside-machines/blob/main/docs/QUALITY-BAR.md); no new lesson is automatically accepted
or added to the live marketplace by this plugin.
