# Refrigerator — curated core iteration

Status: implemented for protected review; no human release acceptance.
Source record: `backend/curated/` trusted plan; current artifact `refrigerator-studio-1`.
The more developed AC, washer, cooker and vacuum retain their existing causal artwork.

## Identity and hypothesis

- Person: a curious beginner, with no assumed appliance-service or engineering knowledge.
- Question: How does a refrigerator work?
- Observable outcome: explain the input, working change and output; transfer that cause to a new condition.
- Hypothesis: after the complete core and comparison, at least four of five initially unfamiliar learners score 2 on causal explanation and the transfer below, before hints.
- Scope: Generic vapor-compression refrigerator. Exposed service-layout cutaway; real coil placement and compressors vary. The front opening is a drawing aid. No temperatures, pressures or efficiency are predicted.
- CE-01–18 trace: complete causal core, purpose before terms, labeled working details, source/claim ledger, prediction, qualitative comparison, transfer, synchronized portable data, accessible/offline player and separate release evidence.

## Concrete teaching choices

- Grant: make a changing relationship visible, then test one altered condition; no motion merely for decoration.
- Feynman: It carries heat out of the food compartment; electricity keeps the journey going.
- Veritasium: ask “Does the refrigerator make heat disappear?” before the reveal, address “A beginner may assume: Yes, it destroys heat”.
- Anatomy: retain labeled working parts and their surroundings. The new library sections are schematic; a boxed locator is explicitly a system map, not finished physical overview artwork. This remains a craft limitation.

## Mechanism, claims and storyboard

Authoritative runtime claims, poses and evidence references are in the immutable CE specification. The planning ledger below states intended source scope; it is not an independent technical pass.

| Claim / beat | Labeled focus | Input → output | Evidence and locator |
| --- | --- | --- | --- |
| claim-0 / beat-0 | Cold coil | Warmer cabinet air → Energy enters refrigerant | [GE Appliances: sealed system operation](https://products.geappliances.com/appliance/gea-support-search-content?contentId=16911), Sealed System Operation, evaporator and return steps; generic, technical check pending |
| claim-1 / beat-1 | Compressor | Low-pressure vapor → Hotter, higher-pressure vapor | [GE Appliances: sealed system operation](https://products.geappliances.com/appliance/gea-support-search-content?contentId=16911), Sealed System Operation, compressor steps 1–2; generic, technical check pending |
| claim-2 / beat-2 | Warm coil | Hot refrigerant → Heat leaves; liquid forms | [GE Appliances: sealed system operation](https://products.geappliances.com/appliance/gea-support-search-content?contentId=16911), Sealed System Operation, condenser steps 3–4; generic, technical check pending |
| claim-3 / beat-3 | Narrow tube | High-pressure liquid → Low-pressure mixture | [GE Appliances: sealed system operation](https://products.geappliances.com/appliance/gea-support-search-content?contentId=16911), Sealed System Operation, capillary and evaporator steps 5–7; generic, technical check pending |

The chapters isolate attention; they do not assert that every machine job happens in this narrated order. Each scene uses the same versioned states for interaction, static and narrated export.

## Qualitative comparison

- Normal: Compressor running. Work maintains sustained circulation around the loop.
- Changed: Compressor stopped. Sustained pumping stops. The real cold coil can still absorb heat briefly; that transient is omitted.
- Markers and arrows describe transfer, never measured rates, temperatures, pressure, particle counts or chip topology.

## Transfer rubric before disclosure

- Task: Would an open refrigerator cool a closed kitchen overall?
- Score 2: The warm side returns the removed heat plus added work. A cool patch near the door does not establish net room cooling.
- Score 1: identifies a component or outcome but omits the causal connection.
- Score 0: Yes, because cold air escapes
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
