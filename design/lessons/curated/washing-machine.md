# Washing machine — curated core iteration

Status: implemented for protected review; no human release acceptance.
Source record: `backend/curated/` trusted plan; current artifact `washing-machine-ce-1`.
The more developed AC, washer, cooker and vacuum retain their existing causal artwork.

## Identity and hypothesis

- Person: a curious beginner, with no assumed appliance-service or engineering knowledge.
- Question: Why wash slowly, then spin quickly?
- Observable outcome: explain the input, working change and output; transfer that cause to a new condition.
- Hypothesis: after the complete core and comparison, at least four of five initially unfamiliar learners score 2 on causal explanation and the transfer below, before hints.
- Scope: Generic front-load washing machine. Front-load example. No cycle times, load limits or measured speed threshold; controls, suspensions and pumps vary.
- CE-01–18 trace: complete causal core, purpose before terms, labeled working details, source/claim ledger, prediction, qualitative comparison, transfer, synchronized portable data, accessible/offline player and separate release evidence.

## Concrete teaching choices

- Grant: make a changing relationship visible, then test one altered condition; no motion merely for decoration.
- Feynman: Gentle tumbling cleans; draining and faster rotation remove the used water.
- Veritasium: ask “Why not use the fastest spin for the whole wash?” before the reveal, address “A beginner may assume: Faster is always better cleaning”.
- Anatomy: retain labeled working parts and their surroundings. The new library sections are schematic; a boxed locator is explicitly a system map, not finished physical overview artwork. This remains a craft limitation.

## Mechanism, claims and storyboard

Authoritative runtime claims, poses and evidence references are in the immutable CE specification. The planning ledger below states intended source scope; it is not an independent technical pass.

| Claim / beat | Labeled focus | Input → output | Evidence and locator |
| --- | --- | --- | --- |
| claim-0 / beat-0 | Inlet valve | Supply water → Wash solution in the tub | [Samsung: front-load washing mechanism](https://www.samsung.com/us/home-appliances/buying-guide/difference-between-top-load-and-front-load-washers/), Front-load washer: small water amount and detergent; generic, technical check pending |
| claim-1 / beat-1 | Drum and motor | Motor work and wash solution → Laundry repeatedly moves through water | [Samsung: front-load washing mechanism](https://www.samsung.com/us/home-appliances/buying-guide/difference-between-top-load-and-front-load-washers/), How do front load washers work?; generic, technical check pending |
| claim-2 / beat-2 | Drain pump | Wet laundry and used water → Drained water and less-wet laundry | [Samsung: front-load washing mechanism](https://www.samsung.com/us/home-appliances/buying-guide/difference-between-top-load-and-front-load-washers/), After washing and rinsing: high-speed spin and drain; generic, technical check pending |

The chapters isolate attention; they do not assert that every machine job happens in this narrated order. Each scene uses the same versioned states for interaction, static and narrated export.

## Qualitative comparison

- Normal: Slow tumble. Clothes are lifted, then fall through the wash solution.
- Changed: Fast-spin comparison. The load stays against the drum instead of undergoing the same lift-and-drop motion. Real speeds are not specified.
- Markers and arrows describe transfer, never measured rates, temperatures, pressure, particle counts or chip topology.

## Transfer rubric before disclosure

- Task: If water leaves the fabric but cannot leave the tub, is the drain job complete?
- Score 2: Spinning and pumping are separate. Water that leaves the clothes remains in the system until it can drain.
- Score 1: identifies a component or outcome but omits the causal connection.
- Score 0: Yes, spin destroys the water
- Teach-back: name the input, mechanism, output and a consequence of changing the path/control.
- Optional next-day check: ask for the same relationship with a familiar system from a different category. Not yet measured.

## Build and evidence

- One shared CE-1 adapter and D1 player; distinct trusted domain drawings, no per-topic player.
- Local authored seed and computer narration: zero new paid API calls. Hosting/storage and human review are not free or measured here. Owner costs distinguish receipts from allowances.
- No answer text is stored by these prediction/transfer controls; chats remain member-private.
| Gate | Evidence | Current result |
| --- | --- | --- |
| Engineering | Required automated and rendered checks recorded in the library implementation record | In progress; not a quality certification |
| Technical | Independent human checks claims, mechanism direction and declared simplifications | Pending |
| Craft/accessibility | Actual-phone readability, sound, keyboard, reduced motion and offline walkthrough | Pending; browser emulation is separate |
| Beginner learning | Five baseline-unfamiliar learners, anonymous 0/1/2 causal and transfer scores | Pending |
| Owner release | Exact spec/video/bundle hashes, after preceding gates | Held |

Observed implementation findings and the largest remaining gap are in the shared friction log and journal. Structural validity alone does not show that a beginner learned the concept.
