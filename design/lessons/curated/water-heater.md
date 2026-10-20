# Water heater — curated core iteration

Status: implemented for protected review; no human release acceptance.
Source record: `backend/curated/` trusted plan; current artifact `water-heater-studio-1`.
The more developed AC, washer, cooker and vacuum retain their existing causal artwork.

## Identity and hypothesis

- Person: a curious beginner, with no assumed appliance-service or engineering knowledge.
- Question: How does a water heater work?
- Observable outcome: explain the input, working change and output; transfer that cause to a new condition.
- Hypothesis: after the complete core and comparison, at least four of five initially unfamiliar learners score 2 on causal explanation and the transfer below, before hints.
- Scope: Generic electric storage water heater. Simplified electric storage tank. Stratification, mixing, controls, corrosion protection and relief devices are not simulated; no service instructions.
- CE-01–18 trace: complete causal core, purpose before terms, labeled working details, source/claim ledger, prediction, qualitative comparison, transfer, synchronized portable data, accessible/offline player and separate release evidence.

## Concrete teaching choices

- Grant: make a changing relationship visible, then test one altered condition; no motion merely for decoration.
- Feynman: A tank stores hot water; cold replacement water enters as hot water is drawn.
- Veritasium: ask “Must the tank empty before fresh water enters?” before the reveal, address “A beginner may assume: Yes, it behaves like a bucket”.
- Anatomy: retain labeled working parts and their surroundings. The new library sections are schematic; a boxed locator is explicitly a system map, not finished physical overview artwork. This remains a craft limitation.

## Mechanism, claims and storyboard

Authoritative runtime claims, poses and evidence references are in the immutable CE specification. The planning ledger below states intended source scope; it is not an independent technical pass.

| Claim / beat | Labeled focus | Input → output | Evidence and locator |
| --- | --- | --- | --- |
| claim-0 / beat-0 | Immersed heater | Electrical input → Thermal energy stored in water | [DOE/NREL: residential water heaters](https://www.energy.gov/sites/prod/files/2014/01/f7/20110224_residential_water_heater_webinar.pdf), Technology Overview: Conventional Storage; generic, technical check pending |
| claim-1 / beat-1 | Cold inlet and hot outlet | Cold replacement water → Hot water delivered from the top | [Rheem: water-heater components](https://www.rheem.com/producteducation/), Dip Tube definition; generic, technical check pending |
| claim-2 / beat-2 | Thermostat | Temperature feedback and draw → Heating input managed | [DOE/NREL: residential water heaters](https://www.energy.gov/sites/prod/files/2014/01/f7/20110224_residential_water_heater_webinar.pdf), Conventional storage maintains a tank set point; generic, technical check pending |

The chapters isolate attention; they do not assert that every machine job happens in this narrated order. Each scene uses the same versioned states for interaction, static and narrated export.

## Qualitative comparison

- Normal: Heater input on. Energy enters the water through the immersed element.
- Changed: Heater input off. Additional input stops. Stored thermal energy remains and is not erased by the switch.
- Markers and arrows describe transfer, never measured rates, temperatures, pressure, particle counts or chip topology.

## Transfer rubric before disclosure

- Task: Could hot water continue briefly after heater power is stopped?
- Score 2: The tank stores thermal energy. How long it can supply a useful temperature depends on draw and the appliance, which this model does not predict.
- Score 1: identifies a component or outcome but omits the causal connection.
- Score 0: No, power-off instantly makes it cold
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
