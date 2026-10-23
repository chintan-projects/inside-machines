# Heat pump — curated core iteration

Status: implemented for protected review; no human release acceptance.
Source record: `backend/curated/` trusted plan; current artifact `heat-pump-studio-1`.
The more developed AC, washer, cooker and vacuum retain their existing causal artwork.

## Identity and hypothesis

- Person: a curious beginner, with no assumed appliance-service or engineering knowledge.
- Question: How does a heat pump work?
- Observable outcome: explain the input, working change and output; transfer that cause to a new condition.
- Hypothesis: after the complete core and comparison, at least four of five initially unfamiliar learners score 2 on causal explanation and the transfer below, before hints.
- Scope: Generic reversible air-source heat pump. Qualitative reversible cycle. Defrost, auxiliary heat, real performance, refrigerants and weather limits vary; no efficiency or capacity numbers.
- CE-01–18 trace: complete causal core, purpose before terms, labeled working details, source/claim ledger, prediction, qualitative comparison, transfer, synchronized portable data, accessible/offline player and separate release evidence.

## Concrete teaching choices

- Grant: make a changing relationship visible, then test one altered condition; no motion merely for decoration.
- Feynman: The cycle moves heat; a valve changes which coil receives hot refrigerant.
- Veritasium: ask “Does cold outdoor air mean there is no energy to collect?” before the reveal, address “A beginner may assume: Yes, cold means no thermal energy”.
- Anatomy: retain labeled working parts and their surroundings. The new library sections are schematic; a boxed locator is explicitly a system map, not finished physical overview artwork. This remains a craft limitation.

## Mechanism, claims and storyboard

Authoritative runtime claims, poses and evidence references are in the immutable CE specification. The planning ledger below states intended source scope; it is not an independent technical pass.

| Claim / beat | Labeled focus | Input → output | Evidence and locator |
| --- | --- | --- | --- |
| claim-0 / beat-0 | Outdoor coil | Outdoor air and colder fluid → Heat enters the refrigerant | [DOE: heat pump systems](https://www.energy.gov/energysaver/heat-pump-systems), How heat pumps work: heating mode; generic, technical check pending |
| claim-1 / beat-1 | Compressor | Collected heat and work → Heat delivered indoors | [DOE: heat pump systems](https://www.energy.gov/energysaver/heat-pump-systems), Heat transfer and compressor work; generic, technical check pending |
| claim-2 / beat-2 | Expansion device | Higher-pressure liquid → Colder low-pressure mixture | [DOE/NREL: heat pump system basics](https://betterbuildingssolutioncenter.energy.gov/sites/default/files/attachments/87812.pdf), Heat Pump Basics: refrigerant expansion and coil roles; generic, technical check pending |
| claim-3 / beat-3 | Reversing valve | Changed refrigerant routing → Coils exchange heating/cooling roles | [DOE/NREL: heat pump system basics](https://betterbuildingssolutioncenter.energy.gov/sites/default/files/attachments/87812.pdf), Appendix: Heat Pump Basics, Reversing Valve; generic, technical check pending |

The chapters isolate attention; they do not assert that every machine job happens in this narrated order. Each scene uses the same versioned states for interaction, static and narrated export.

## Qualitative comparison

- Normal: Heating role. The indoor side receives heat from the hot refrigerant.
- Changed: Cooling role. Routing changes: the indoor side supplies heat to colder refrigerant. This is a mode comparison, not a valve-transition simulation.
- Markers and arrows describe transfer, never measured rates, temperatures, pressure, particle counts or chip topology.

## Transfer rubric before disclosure

- Task: What must change to cool the house instead?
- Score 2: Refrigerant routing changes which coil absorbs and which rejects heat. Air movement alone cannot reverse the refrigeration cycle.
- Score 1: identifies a component or outcome but omits the causal connection.
- Score 0: Only the indoor fan needs to reverse
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
