# GPU — curated core iteration

Status: implemented for protected review; no human release acceptance.
Source record: `backend/curated/` trusted plan; current artifact `gpu-studio-1`.
The more developed AC, washer, cooker and vacuum retain their existing causal artwork.

## Identity and hypothesis

- Person: a curious beginner, with no assumed appliance-service or engineering knowledge.
- Question: How does a gpu work?
- Observable outcome: explain the input, working change and output; transfer that cause to a new condition.
- Hypothesis: after the complete core and comparison, at least four of five initially unfamiliar learners score 2 on causal explanation and the transfer below, before hints.
- Scope: Illustrative data-parallel computation, with CUDA as one documented example. Logical teaching diagram, not an actual GPU die, scheduler trace, benchmark or universal CUDA architecture. No core counts or performance numbers are claimed.
- CE-01–18 trace: complete causal core, purpose before terms, labeled working details, source/claim ledger, prediction, qualitative comparison, transfer, synchronized portable data, accessible/offline player and separate release evidence.

## Concrete teaching choices

- Grant: make a changing relationship visible, then test one altered condition; no motion merely for decoration.
- Feynman: A program defines work; memory supplies inputs; parallel execution produces stored results.
- Veritasium: ask “Does adding more execution lanes guarantee a proportional speedup?” before the reveal, address “A beginner may assume: Yes, twice the lanes always halves the time”.
- Anatomy: retain labeled working parts and their surroundings. The new library sections are schematic; a boxed locator is explicitly a system map, not finished physical overview artwork. This remains a craft limitation.

## Mechanism, claims and storyboard

Authoritative runtime claims, poses and evidence references are in the immutable CE specification. The planning ledger below states intended source scope; it is not an independent technical pass.

| Claim / beat | Labeled focus | Input → output | Evidence and locator |
| --- | --- | --- | --- |
| claim-0 / beat-0 | Program | Program and work-item identities → A defined set of calculations | [NVIDIA: writing SIMT kernels](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/writing-cuda-kernels.html), Thread hierarchy and unique thread identities; generic, technical check pending |
| claim-1 / beat-1 | Input memory | Available input data → Calculated and stored results | [NVIDIA: programming model](https://docs.nvidia.com/cuda/archive/13.2.2/cuda-programming-guide/01-introduction/programming-model.html), Memory hierarchy and kernel execution; generic, technical check pending |
| claim-2 / beat-2 | Execution lanes | Ready work and finite resources → Concurrent progress where permitted | [NVIDIA: writing SIMT kernels](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/writing-cuda-kernels.html), Synchronization and memory hazards; generic, technical check pending |

The chapters isolate attention; they do not assert that every machine job happens in this narrated order. Each scene uses the same versioned states for interaction, static and narrated export.

## Qualitative comparison

- Normal: Inputs available. The declared operations can consume their available operands.
- Changed: Required input withheld. Dependent work waits and its output is not fabricated. Other independent ready work can still proceed.
- Markers and arrows describe transfer, never measured rates, temperatures, pressure, particle counts or chip topology.

## Transfer rubric before disclosure

- Task: Can a calculation produce the right answer before a required input exists?
- Score 2: A correct computation uses its required operands. Waiting is a consequence of the dependency, not evidence that the program should guess the missing value.
- Score 1: identifies a component or outcome but omits the causal connection.
- Score 0: Yes, spare lanes can invent it
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
