# One vacuum, four visual approaches

Local authored experiment, not a replacement production pipeline. Read [the brief](BRIEF.md).
Output: `.vercel/vacuum-lab/index.html`, a single self-contained HTML with eight actual
encoded films, static checkpoints, shared narration/text and private in-page preference.
No API key or model call is needed to open, replay, compare or export a preference.

The same OpenAI Codex interactive session authored all adapters from the saved common
and tool-specific briefs in `prompts/`. This does not measure unattended generation,
API token cost, model superiority, or the intrinsic ceiling of a rendering library.
Iteration and manual repairs count as authoring effort, not renderer run time.

## Reproduce on this Mac

Keep dependencies and media outside production packaging and tracked assets:

```sh
uv venv --python 3.13 .vercel/vacuum-lab/python
uv pip install --python .vercel/vacuum-lab/python/bin/python manim==0.22.0
mkdir -p .vercel/vacuum-lab/runtime
cp experiments/vacuum-lab/package.json .vercel/vacuum-lab/runtime/package.json
npm install --prefix .vercel/vacuum-lab/runtime --legacy-peer-deps
node experiments/vacuum-lab/render.mjs audio
node experiments/vacuum-lab/render.mjs anatomy
node experiments/vacuum-lab/render.mjs manim
node experiments/vacuum-lab/render.mjs motion
node experiments/vacuum-lab/render.mjs remotion
node experiments/vacuum-lab/pack.mjs
node --test experiments/vacuum-lab/model.test.mjs
.venv/bin/python experiments/vacuum-lab/verify_media.py
```

Requires macOS `say` with Samantha, FFmpeg/ffprobe, Cairo/Pango for Manim and a Chromium
download for the browser renderers. Remotion’s separate license applies; this individual
local evaluation does not buy or configure a hosted rendering service. The ignored runtime
package lock records exact installed Node versions; the packaged manifest records render
versions/hashes. Manim and Anatomy receive the same pure state as the other adapters.

For local HTTP review, serve **only** the output directory, bound to loopback. Opening the
HTML as a file should also work offline. No server, credentials, telemetry endpoint or
cloud data access is embedded. Dependencies, render PNGs and encoded artifacts remain ignored.

The boundary verifier decodes real MP4s at exactly 12, 23 and 34 seconds and compares
the stable shot text with a later frame of the same beat. It caught and now guards
against a previous-shot frame appearing after a chapter seek. Export locks prevent
overlapping runs of the same adapter, and packaging rejects active renders, stale
story/source hashes, incomplete media or changed receipt-bound video bytes.

## Select after looking

Use the same chapter/time and condition across candidates. Evaluate the diagram as well
as the film. Choose an owner preference, then check technical truth and uncoached learning.
One vacuum is enough to select a direction for another experiment, not enough to certify
a universal renderer for appliances, GPUs and LLMs. Do not silently publish a new default.
