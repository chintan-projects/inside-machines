# Electric oven — curated core iteration

Status: implemented for protected review; no human release acceptance.
Source record: `backend/curated/` trusted plan; current artifact `electric-oven-studio-1`.
The more developed AC, washer, cooker and vacuum retain their existing causal artwork.

## Identity and hypothesis

- Person: a curious beginner, with no assumed appliance-service or engineering knowledge.
- Question: How does a electric oven work?
- Observable outcome: explain the input, working change and output; transfer that cause to a new condition.
- Hypothesis: after the complete core and comparison, at least four of five initially unfamiliar learners score 2 on causal explanation and the transfer below, before hints.
- Scope: Generic electric oven with optional convection fan. Illustrative heat paths, not measured air currents or cooking times. Broil, bake and convection controls differ across models.
- CE-01–18 trace: complete causal core, purpose before terms, labeled working details, source/claim ledger, prediction, qualitative comparison, transfer, synchronized portable data, accessible/offline player and separate release evidence.

## Concrete teaching choices

- Grant: make a changing relationship visible, then test one altered condition; no motion merely for decoration.
- Feynman: Elements supply heat; radiation, moving air and contact transfer it into food.
- Veritasium: ask “Does an off interval mean the food instantly stops receiving heat?” before the reveal, address “A beginner may assume: Yes, everything becomes cold”.
- Anatomy: retain labeled working parts and their surroundings. The new library sections are schematic; a boxed locator is explicitly a system map, not finished physical overview artwork. This remains a craft limitation.

## Mechanism, claims and storyboard

Authoritative runtime claims, poses and evidence references are in the immutable CE specification. The planning ledger below states intended source scope; it is not an independent technical pass.

| Claim / beat | Labeled focus | Input → output | Evidence and locator |
| --- | --- | --- | --- |
| claim-0 / beat-0 | Heating element | Electrical input → Thermal energy at elements | [Whirlpool: how ovens work](https://www.whirlpool.com/blog/kitchen/how-do-ovens-work.html), Understanding how ovens work: electric ovens; generic, technical check pending |
| claim-1 / beat-1 | Convection fan | Heated surfaces and air → Energy transferred into the load | [Whirlpool: how ovens work](https://www.whirlpool.com/blog/kitchen/how-do-ovens-work.html), Heat transfer and convection; generic, technical check pending |
| claim-2 / beat-2 | Temperature control | Temperature feedback → Heating input cycles | [GE: cycling elements during baking](https://products.geappliances.com/appliance/gea-support-search-content?contentId=16976), Electric Range Operation of the Elements During Bake; generic, technical check pending |

The chapters isolate attention; they do not assert that every machine job happens in this narrated order. Each scene uses the same versioned states for interaction, static and narrated export.

## Qualitative comparison

- Normal: Fan-assisted circulation. Air is moved through the cavity; radiation and contact transfer remain.
- Changed: Fan stopped. Forced circulation stops. Radiation and natural convection can still transfer heat; the oven does not instantly stop cooking.
- Markers and arrows describe transfer, never measured rates, temperatures, pressure, particle counts or chip topology.

## Transfer rubric before disclosure

- Task: Would a fan alone supply an oven's continuing cooking energy?
- Score 2: A fan redistributes air and uses some electrical work. The oven's heating system supplies the cooking heat in this model.
- Score 1: identifies a component or outcome but omits the causal connection.
- Score 0: Yes, air motion creates unlimited heat
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
