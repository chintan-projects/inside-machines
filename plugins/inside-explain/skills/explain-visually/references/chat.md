# Chat surfaces and follow-up

First inspect capabilities, not just the product name. A desktop/Codex session
with local files and a shell can produce and preview local HTML and Studio video.
A plugin's instructions do not grant filesystem, shell, account or billing access.

In a chat-only session, use the same question, evidence and causal sequence:

- If HTML/file generation is available, return a self-contained HTML artifact or
  downloadable file with embedded SVG and deterministic interaction. Do not claim
  it ran locally or that its controls were browser-tested unless they were.
- If rendering tools are unavailable, supply the storyboard and underlying
  content with a copyable local handoff. A requested MP4 remains unrendered; do
  not label HTML, a script or a still image as a completed video.
- Use supported artifact features only when actually present. Claude live-artifact
  behavior does not automatically transfer to ChatGPT. A saved HTML file is not
  a self-hosted AI chatbot. Continue questions in the conversation alongside it.

The local skill and plugin are installed separately from a public ChatGPT
directory listing. Repo marketplaces help desktop/Codex development; they do not
make the plugin globally available on every web/mobile account. A ChatGPT skills
package or public plugin submission is another distribution step. Never upload
private session logs or connect an MCP service just to share these instructions.

## Copyable starter for a chat without the plugin

Use the following request with your topic and sources:

> Help me understand [topic] through one concrete example. Show the input, each
> necessary operation and the result, using a labeled visual rather than decorative
> animation. Start with one prediction and finish with a changed-situation question
> before revealing its answer. Distinguish facts from illustrative assumptions.
> If you can create HTML, make it a self-contained interactive file with reset and
> a static explanation; otherwise give me a storyboard and say it is unrendered.
> Keep the first explanation concise, then let me ask to dive deeper. Do not call
> external paid APIs or publish anything.

For local continuation, hand over the question, sources, claim ledger, audience,
storyboard, requested mode and unresolved questions. The saved `explanation.json`
and brief are the continuity record, not an assumption that another chat remembers.
