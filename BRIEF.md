# Inside product design brief

**Scope extension:** [ADR 0003](docs/architecture-decisions/0003-extensible-concept-lessons.md)
adds computational concepts such as GPUs and LLMs to the same learner job. Their
representations follow the concept: work/dependency views or token transformations
rather than invented appliance cutaways. The physical alpha and its open quality
gates remain the first benchmark; no new GPU/LLM lesson is approved by this change.

**Active teaching contract:** [ADR 0001](docs/architecture-decisions/0001-concept-explanation.md)
and the [concept explanation spec](docs/CONCEPT-EXPLANATION-SPEC.md) govern subsequent
lesson iterations. Grant's visual reasoning, Feynman's causal simplicity,
Veritasium's misconception/prediction structure and Anatomy's physical craft must
produce visible design choices and testable learner outcomes. Use the
[AC benchmark spec](design/lessons/air-conditioner.md) for the next build. The dated
directions below remain context; they do not establish current learning acceptance.

Draft direction for the next product iteration, October 19, 2026. This specifies future design; it does not restyle the existing prototype.

**Person:** An adult who has just asked a concrete question about an everyday machine and cannot picture the mechanism.

**One job:** Make the cause and consequence visible so the person can explain or predict what happens next.

**Posture:** Calm, precise, hands-on.

**References:** [Ciechanowski's engine explanation](https://ciechanow.ski/internal-combustion-engine/) for controls adjacent to the mechanism they change; [Tinybop Simple Machines](https://tinybop.com/apps/simple-machines) for direct manipulation that rewards curiosity. Avoid the current prototype's large editorial introduction on a direct lesson link: it delays the object the person came to understand. These are interaction references, not sources to copy.

## First screen

A direct lesson link shows the actual mechanism and a relevant action. For the washer:

- Title: “Why does the washer spin so fast?”
- Scope: “Generic front-load washer.”
- Main action: “Watch the cycle.”
- Exploration action: “Change drum speed.”
- Evidence control: “Sources and assumptions.”
- Specificity choice, when requested: “Understand the principles” or “Match my machine.”

The catalog shows recognizable machines and questions, not ten identical sales cards. The user does not complete a profile, buy credits, or identify a model before seeing a generic explanation. A customer API-key field has no place in this flow.

## Ranked decisions

1. Begin with the mechanism; introduce setup only when it changes the answer.
2. Simplify peripheral detail to make the causal part legible on a phone.
3. Keep authored learning available when AI or connectivity fails.
4. Distinguish documented details from schematic depiction at the point of use.
5. Ask before starting additional paid work; repeat playback consumes no credits.

## What stays still and what moves

Navigation, explanatory copy, and evidence controls stay still. Machine motion begins after an explicit action. Water/energy flow, the selected part, and its consequence form one coordinated explanation. Only one pedagogical animation owns attention at a time. Static stage progression must teach the same idea under reduced motion.

## Design hypothesis

The memorable moment is a user changing drum speed and predicting why the clothes stop tumbling. A stylish scene that cannot teach that relationship fails the brief. Validate this hypothesis before polishing an expanded catalog.

## October 19: action-led AC studio (supersedes the panel-heavy AC direction)

The latest human review rejects the labeled schematic as ordinary. A curious
beginner wants to picture where heat goes, not study refrigeration terminology.
The first question is “Why does an AC need an outdoor unit?” The job is to trace
heat out of a room, then predict the result of putting both units inside it.
Posture: tactile, focused, inviting.

Reference: visual-learning.app/microwave. Observed: a recognizable cutaway fills
the canvas; each step is a concrete action, a single sentence explains the change,
and the chocolate/turntable contrast gives the mechanism a reason to exist.
Take this teaching structure, not its drawing or brand palette. Anatomy supplies
the mechanical craft reference. Avoid our current screen's simultaneous state
cards, paragraphs, six tabs, dropdown and duplicate playback controls.

Decisions: one dominant cutaway; a quiet ordered story rail; one next action;
component names anchored to hardware, jargon secondary; an indoor/outdoor
experiment demonstrates the point. Technical detail, sources, private chat and
feedback remain available after the main experience. No invented temperatures or
measured efficiency. Reuse the stored lesson's facts and narration; no paid model
calls or changes to published content are required for this presentation revision.

At rest, all controls and diagram labels remain still. An explicit play/listen
action starts motion. Step changes focus the relevant mechanism; reduced-motion
users get static direction cues and the same outcome. Saved progress remains
member-scoped. Offline narration reuses the downloaded media's audio track.
