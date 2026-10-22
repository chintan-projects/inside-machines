# Personal visual explanation skill

Installed on 2026-10-22 for both agents, without changing `CLAUDE.md` or other
agent configuration:

- Canonical skill: `/Users/chintan/.codex/skills/explain-visually/SKILL.md`.
- Claude Code: `/Users/chintan/.claude/skills/explain-visually` is a symlink to
  that same canonical directory, so the instructions cannot drift between copies.
- Anatomy dependency: `/Users/chintan/.codex/skills/anatomy`, shared by the
  `/Users/chintan/.claude/skills/anatomy` symlink. The complete upstream kit,
  references, examples and MIT license are included.

Invoke in Claude Code:

```text
/explain-visually Help me understand how GPT inference produces the next token.
/explain-visually Show what changed in this diff and trace one input before and after.
```

Invoke in Codex:

```text
$explain-visually Explain why the same owner build attempt keeps its identity after a lost response.
```

The installation is available on the next turn; start a new agent session if the
current one has cached its skill list. “GPT influencing” in the original request
is interpreted here as **GPT inference**, rather than fine-tuning or persuasion.

The skill builds a local interactive explanation with a complete core and optional
insight/model depth. Physical objects use the actual Anatomy kit. Software and
LLMs show real operations, values and dependencies, with illustrative numbers
identified as such. Code explanations read the actual diff and relevant code;
they do not invent an earlier implementation or infer duplicate billing merely
from a missing client identity. API keys, paid calls, publication and a full app
backend are not prerequisites or implied permissions.

Anatomy was installed using the Codex skill-installer helper from
[wheresryan22/anatomy at 1482e8469b0a9e0d8cc18ea2740a01423d29ae80](https://github.com/wheresryan22/anatomy/tree/1482e8469b0a9e0d8cc18ea2740a01423d29ae80).
Its `INSTALLATION.json` records provenance; upstream source was preserved. The
custom skill's relative links remain portable when installed beside Anatomy.

Both skill paths passed the skill-creator `quick_validate.py` check. An isolated
local exercise applied the workflow to the actual client change in `6c78275`:
the page ran the inspected `OwnerAttempts` helper with deterministic test IDs,
showed its real before/after request body, and offered three working depth views.
Observed browser behavior included repeated identity reuse, explicit replacement,
separate identities for another intent, reset, keyboard operation and a 390-pixel
layout without horizontal overflow. Reduced-motion emulation disabled animation.
The installed Anatomy dial-indicator example also built and changed its readout
with the arrow key. Both pages had no observed console errors.

Test artifacts are local and temporary:
`/tmp/explain-visually-smoke-20261022-0o6d6r5w/` contains the HTML, exact diff/code
snapshot, pure-model trace, observations and desktop/phone screenshots. The
loopback-only preview server was stopped and its test tabs closed afterward.
This was a self-applied workflow test, not a paid fresh Claude/Codex run, an
independent learner evaluation, a real-phone check or human craft approval.
