# Air conditioner — curated core iteration

Status: implemented for protected review; no human release acceptance.
Source record: `backend/curated/` trusted plan; current artifact `air-conditioner-ce-1`.
The more developed AC, washer, cooker and vacuum retain their existing causal artwork.

## Identity and hypothesis

- Person: a curious beginner, with no assumed appliance-service or engineering knowledge.
- Question: Why does an AC need an outdoor unit?
- Observable outcome: explain the input, working change and output; transfer that cause to a new condition.
- Hypothesis: after the complete core and comparison, at least four of five initially unfamiliar learners score 2 on causal explanation and the transfer below, before hints.
- Scope: Generic split-system air conditioner in cooling mode. Cooling mode and qualitative coil sections. No temperatures, pressures, refrigerant specification or actual installation layout is predicted.
- CE-01–18 trace: complete causal core, purpose before terms, labeled working details, source/claim ledger, prediction, qualitative comparison, transfer, synchronized portable data, accessible/offline player and separate release evidence.

## Concrete teaching choices

- Grant: make a changing relationship visible, then test one altered condition; no motion merely for decoration.
- Feynman: Heat goes outside through refrigerant tubing; the indoor air does not travel through that tubing.
- Veritasium: ask “Does the refrigerant pipe bring outside air into the room?” before the reveal, address “A beginner may assume: Yes, that is what the pipe carries”.
- Anatomy: retain labeled working parts and their surroundings. The new library sections are schematic; a boxed locator is explicitly a system map, not finished physical overview artwork. This remains a craft limitation.

## Mechanism, claims and storyboard

Authoritative runtime claims, poses and evidence references are in the immutable CE specification. The planning ledger below states intended source scope; it is not an independent technical pass.

| Claim / beat | Labeled focus | Input → output | Evidence and locator |
| --- | --- | --- | --- |
| claim-0 / beat-0 | Indoor cold coil | Room air warmer than the coil → Heat enters refrigerant | [Carrier: how air conditioners work](https://www.carrier.com/us/en/residential/hvac-resources/air-conditioners/how-do-air-conditioners-work/), Cold side and evaporator; generic, technical check pending |
| claim-1 / beat-1 | Compressor | Low-pressure vapor plus work → Hotter refrigerant rejects heat | [Carrier: refrigerant cycle](https://www.carrier.com/residential/en/ca/products/air-conditioners/ac-refrigerant/), Compression and condensation; generic, technical check pending |
| claim-2 / beat-2 | Expansion device | Liquid on the high-pressure side → Low-pressure evaporator supply | [Carrier: refrigerant cycle](https://www.carrier.com/residential/en/ca/products/air-conditioners/ac-refrigerant/), Expansion and the repeating cycle; generic, technical check pending |

The chapters isolate attention; they do not assert that every machine job happens in this narrated order. Each scene uses the same versioned states for interaction, static and narrated export.

## Qualitative comparison

- Normal: Cold coil absorbs heat. Heat passes from room air into the colder working fluid.
- Changed: No temperature difference. At the declared equal-temperature comparison, there is no net heat transfer through the coil wall. No transient is simulated.
- Markers and arrows describe transfer, never measured rates, temperatures, pressure, particle counts or chip topology.

## Transfer rubric before disclosure

- Task: Could cooling continue indefinitely if the warm side could reject no heat?
- Score 2: The incoming heat and work need an exit from the cycle. The system cannot store them indefinitely.
- Score 1: identifies a component or outcome but omits the causal connection.
- Score 0: Yes, the cold coil stores unlimited energy
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
