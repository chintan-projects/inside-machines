# Concept explanation specification

Version: 1.1, 2026-10-19.
Authority: [ADR 0001](architecture-decisions/0001-concept-explanation.md).
Scope: authored and generated machine lessons, follow-up visual actions, narration,
video and static alternatives across web/PWA and future native clients.

This is a build and review contract. The CE-1 typed data, prompts, player, media
and review workflow implement it; see the [implementation/evidence record](CONCEPT-IMPLEMENTATION.md).
Implementation does not establish technical correctness or human acceptance.
Grant, Feynman, Veritasium and Anatomy inform the decisions and source notes in the
ADR; the numbered requirements here are Inside's implementation of those ideas.

## Learner outcome and teaching structure

For an adult with a concrete machine question, the lesson must make a useful causal
relationship visible and support a new prediction. Recalling component names or
repeating the headline alone does not demonstrate understanding.

| ID | Requirement | Acceptance evidence |
| --- | --- | --- |
| CE-01 | Name one primary question, intended learner, scope and observable outcome before building. | A filled lesson worksheet and a transfer task with a predefined answer/rubric. |
| CE-02 | Offer a prediction that exposes a plausible misconception before revealing its resolution. Allow “Show me” without an answer; do not force guessing. | The result is initially concealed, choices/skip work, and feedback explains the mechanism without shaming. |
| CE-03 | Map prerequisite ideas and teach the missing relationship with a familiar concrete example. | A beginner can follow the next step without an unexplained prerequisite or a glossary detour. |
| CE-04 | Each causal beat establishes one new relationship: input → change/action → reason → output. | The learner can point to the visible change; the narration explains that same change. A highlighted shell alone fails for an internal action. |
| CE-05 | Identify every core component with an anchored on-scene label. Preserve identity through detail views and return to the whole. | Labels are readable at supported phone sizes and in video; selecting/focusing never refers to an unseen, unidentified part. |
| CE-06 | State the physical job in plain language before relying on its technical name. Use precise terms once motivated. | A reviewer can paraphrase the causal chain without unexplained jargon; simplification does not change the mechanism. |
| CE-07 | Give motion and visual encodings explicit physical meaning. Distinguish working fluid, surrounding air, heat and electrical work using labels/direction/shape as well as color. | A reviewer can trace each independently; decorative motion does not masquerade as a process or measurement. |
| CE-08 | Drive all dependent views from one authoritative state and supported scenario rules. | Equivalent state after seek, replay, step change and narration seek; changing a scenario updates the scene, explanation and readouts together. |
| CE-09 | Include at least one meaningful cause-and-consequence interaction or reviewed counterfactual. Declare whether it is qualitative, computed or an analogy. | The consequence and its limits are defined in the worksheet; arbitrary animation speed or a Next button alone does not satisfy this requirement. |
| CE-10 | Derive numerical readouts from a declared model with units/ranges and evidence or explicit illustrative assumptions. | Boundary/invariant tests verify implemented rules; no fabricated instrument readings or precision unsupported by the model. Qualitative lessons need no invented numbers. |
| CE-11 | Reassemble the complete system and identify what operates simultaneously, sequentially or under control. | The whole view connects each taught relationship and correctly depicts the machine's operating order. Chapter order cannot imply false on/off behavior. |
| CE-12 | Link consequential claims to supporting source locations and nearby assumptions. Distinguish a generic principle, documented model detail and unverified information. | A technical reviewer checks the actual claim/source relationship, including flow direction and applicable conservation rules. A URL alone is insufficient. |
| CE-13 | Test transfer with a changed situation before disclosing the answer. Offer an optional plain-language teach-back. | The rubric rewards causal reasoning and checks the targeted misconception; recognition-only questions are supplementary. |
| CE-14 | Preserve the core explanation without sound, color, motion or a fresh AI call. | Static steps/text, keyboard focus, reduced motion, saved offline playback and real-phone readability are reviewed. Online-only chat clearly reports its state. |
| CE-15 | Record engineering, factual, craft/accessibility and learner evidence separately for a specific revision. | Approval names the reviewer and scope; automated acceptance is never presented as independent scientific or human approval. |
| CE-16 | Preserve immutable revisions, stable semantic identities and member-private history. | New fields use versioned contracts/migrations; replacement does not mutate old lessons, attach chats to the wrong artifact or silently reinterpret saved progress. |
| CE-17 | Keep learning/evaluation playback free of implicit paid calls. Use existing budget and privacy controls for authoring or chat. | Replays and predictions are deterministic/offline where supported; failure cannot silently retry paid work. Logs contain no learner answers or chat text. |
| CE-18 | Keep interactive scenes, narration, captions, video and static alternatives semantically aligned. | For each reviewed checkpoint, component, state, action, outcome and explanation agree across outputs. Video may offer a pause-to-predict instead of interaction. |

Question, prediction and transfer are lesson-level elements; do not repeat a quiz
on every click. Beats may combine orientation with a prediction or reunification
with transfer. Chapter count follows the concept and current schema limits, rather
than an arbitrary six-step template. A shorter overview may link into deeper
prerequisite explanations without making them mandatory detours for every learner.
Follow-up chat reuses the validated mechanism and relevant visual checkpoint; each
reply need not replay the full lesson structure or repeat its assessment.

## Authoring contract and module boundaries

Start as a reviewed worksheet. The v2 lesson contract introduces the following
as typed, validated data; legacy v1 revisions retain their reader and identities:

| Record | Required information |
| --- | --- |
| Lesson identity | Lesson/revision ID, spec version, machine family, generic/exact scope, primary question, learner outcome and current review status |
| Mechanism | Stable component and connection IDs, material/energy transfers, supported qualitative scenarios or equations, units/ranges, relevant invariants and model limits |
| Claim | Stable ID, statement, evidence state, source URL and section/page locator, applicability, assumptions and review result |
| Teaching beat | Stable ID, purpose, prerequisites, focal component(s), input, action, reason, output, claim references, visible cue, short copy, narration and static equivalent |
| Interaction | Trusted action ID, allowed inputs, initial state/reset, state transition or reviewed scenario, expected consequence and qualitative/computed/analogy declaration |
| Assessment | Prediction/transfer prompt, reveal behavior, misconception addressed, expected reasoning, counterexamples and scoring rubric |
| Media manifest | Shared lesson/revision, scene and storyboard versions, checkpoint mapping, narration/caption/artifact identities and parity evidence |
| Review record | What was checked, method, reviewer, date, artifact revision, results, remaining gaps and owner's release decision |

The mechanism owns causal outcomes; the storyboard selects attention and order;
renderers display the resulting state. Keep deterministic scenario functions outside
React components. Adapter-specific geometry is permitted; duplicating physical
business rules across frontend, video renderer and chat is not.

Keep the existing shared model gateway, config, structured logger and state manager.
Register only trusted renderer/provider adapters with declared capabilities. The
model can propose validated data and supported visual actions; it cannot supply
runtime JavaScript, endpoints or credentials. Unknown action IDs and unsupported
mechanism families must fail clearly rather than render a plausible substitute.

Implement additive/versioned migrations with schema tests before enabling new
authoring fields. Preserve the current v1 lesson reader and stored stage identities.
Explicitly map stable teaching IDs to media checkpoints; array positions are not a
safe cross-version identity. Do not build a generic plugin engine or full physics
solver for the first AC iteration.

## Iteration loop

Use [the template](templates/lesson-iteration.md) and keep one active hypothesis per
lesson iteration. A complete vertical slice is more useful than disconnected visual
polish or an expanded catalog with untested explanations.

| Step | Deliverable | Exit evidence |
| --- | --- | --- |
| 1. Define | Question, misconception, desired mental model and changed-situation task | A falsifiable hypothesis with baseline and success/failure criteria |
| 2. Ground | Claim ledger, core parts/connections, prerequisite order and model limits | Technical risks resolved or explicitly pending; no invented facts |
| 3. Storyboard | Causal beats, input/action/output, visual plan and static equivalents | Every beat earns its place; all required ideas reconnect to the final system |
| 4. Build | One complete path with trusted state transitions and shared media meaning | Necessary implementation tests and usable browser preview |
| 5. Critique | Phone/tablet/desktop render review, interaction/failure checks and source review | Findings labeled observed/inferred; blockers and high-severity issues resolved |
| 6. Learn | Uncoached beginner prediction, teach-back and transfer | Anonymized rubric results and confusion locations; missing tests stay pending |
| 7. Decide | Revision outcome, owner's decision and next hypothesis | Release or another bounded iteration, with no self-certified learning claim |

Apply the design-quality skill's three render-review rounds per iteration; each
round targets the most consequential finding and covers hierarchy, typography,
mechanism craft, interaction/state and responsive/accessibility behavior. If the
owner rejects the result, record the unresolved cause and begin a new bounded
iteration. Do not turn a three-round limit into automatic approval or indefinite
cosmetic tweaking. Put evidence in the friction log and decision/prediction in the
journal; retain earlier observations as history.

## Evaluation and release evidence

### Engineering and model checks

Run the project checks in `AGENTS.md` for implementation. Add meaningful tests for
new causal transitions, invariants, invalid inputs, seeking/reset behavior and
shared-output agreement. Run actual geometry audits only where integrated; manual
inspection is not an audit pass. Current `backend.quality` continues before model
review, after it and before publication. New structural requirements belong there
only after their typed contract exists; semantic correctness still needs review.

### Technical and craft checks

A named technical reviewer checks every consequential claim, prerequisite,
conservation relationship and simplification against its evidence. Record their
expertise/scope and unresolved disputes. The owner separately walks the primary
journey on a real phone, including labels, touch/keyboard alternatives, sound-off,
reduced motion, offline/reconnect and return to the whole. Record factual errors
and misleading visuals as blockers even if the scene looks finished.

### Beginner learning check

For the first benchmark, recruit five target beginners for a formative test. Capture
their initial prediction/reasoning, allow the lesson without coaching, then ask for
a short causal explanation and a changed-situation prediction before hints/reveal.
Score using the lesson's rubric written beforehand:

| Score | Reasoning |
| --- | --- |
| 0 | Incorrect or the target misconception persists |
| 1 | Correct direction/name but missing or contradictory cause |
| 2 | Correct causal relationship at the declared level, including the changed situation |

Proposed benchmark gate: at least four of five score 2 on both the causal explanation
and transfer task, and no unresolved factual, accessibility or reliability blocker.
Record initial knowledge and individual anonymized results as well as totals; users
who knew the answer at baseline do not demonstrate a learning gain. Recruit additional
beginners if fewer than five lacked the target causal understanding initially.
Ask a next-day transfer variant when feasible; report retention as unmeasured until
tested. Five people provide iteration evidence, not statistical proof or superiority
to another teaching method. The PRD's larger comparative pilot remains later work.

Learner participation and storing an answer are optional. Private answers stay in
ignored local/private storage, not public lesson artifacts, general logs or analytics.
Commit only anonymized aggregate findings without identifying details. The
telemetry implementation collects only coarse consented events such as a skipped
prediction, reset, confusing beat or thumb; it must not collect answer/chat text
implicitly. The API requires explicit consent for counts; written answers remain in ephemeral browser memory.

Thumbs and chat identify confusion and demand; they do not replace teach-back and
transfer evidence. Human reviewers own any ambiguity in scoring. A model may assist
review within budget but may neither approve itself nor silently incur evaluation
cost. Report abstentions and missing observations separately from correct answers.

## Implementation and remaining evidence

The [implementation record](CONCEPT-IMPLEMENTATION.md) traces CE-01–18 to modules,
tests and limitations. The AC, washer and cooker now have distinct CE-1 draft
storyboards, causal insets, prediction/transfer, source ledgers and newly rendered
narrated media. New generation requires the v2 contract. Existing v1 artifacts and
private conversations remain immutable. The owner workbench records each required
review against exact spec/video hashes; it does not supply those human judgments.

Independent technical review, actual-phone craft/accessibility and five-beginner
learning evidence are still required. Each family and newly generated draft needs
its own acceptance; AC evidence cannot promote the rest of the catalog.
