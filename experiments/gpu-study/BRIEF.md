# GPU: many little jobs, one useful idea

Local standalone Figure study, revision GPU-S1. The owner called the vacuum trial
“quite good” and chose GPU as the second example on 2026-10-19. That is positive
craft feedback on the vacuum, not technical/learning/release approval. Preserve its
artifact. Follow ADRs 0001/0003, CE-01–18 and the lesson iteration worksheet.

## Person, job and direction

A curious beginner, intended range 8–80, wants to picture what a GPU does without
an architecture lecture. One job: explain why many similar independent jobs can
progress together, and why adding lanes cannot erase a dependency. Posture:
tangible, playful, exact. Anatomy contributes filled volume and purposeful board
detail; the successful vacuum contributes object-first actions and a working
detail window. Avoid a dashboard, pretend silicon conveyor or tiny unlabeled die.

The default tour of chip names would fail because the learner can repeat “lots of
cores” without predicting anything. Instead make one batch of eight numerical
pixel values tangible. Each job adds one. Keep job identities and actual arithmetic
visible; change only the prerequisite graph or available lanes/data. Reassemble
the physical chip, nearby memory and logical view explicitly.

Tenets: earn the first tap with the object; one visible causal change beats a parts
inventory; truthful abstraction beats fictitious machinery; extra depth is optional.
Reuse the science-book ink/type/material direction, with cool silicon and copper
accents belonging to components. No purple AI glow, giant text hero or card grid.
Default is a readable still; all motion starts deliberately.

## Hypothesis, mechanism and claim ledger

Hypothesis: after comparing the same eight add-one jobs with independent inputs
and a result chain, at least 4/5 initially unfamiliar beginners can explain which
jobs may start together and solve a new dependency example without hints.

| Claim | Evidence / locator | Applicability and limit | Review |
| --- | --- | --- | --- |
| G1: GPU computation can run many instances of code over different data | NVIDIA CUDA Programming Guide, §1.2.1, kernel launch paragraph | CUDA example supports the general idea; no universal core/thread counts | pending |
| G2: resources and grouping constrain which work executes | Same guide §1.2.2 and §1.2.2.1 | Four illustrative lanes are not SMs, warps, die layout or a CPU comparison | pending |
| G3: memory/data availability matters | Same guide §1.2.3 introduction and DRAM section | Toy data hold has no real latency or bandwidth value | pending |
| G4: a job cannot consume a predecessor's answer before it exists | Declared toy dependency graph, executable prerequisite rule | Mathematical model inference, not hardware timing | pending |

Source checked 2026-10-19:
https://docs.nvidia.com/cuda/cuda-programming-guide/01-introduction/programming-model.html
Eight jobs A–H each add one in one ideal teaching round. Independent inputs are
0–7. Chained inputs start at zero and then use the previous result. Both yield
1–8. Available lanes are one or four, with stable ready-job ordering. A held-input
scenario starts no jobs. Nine illustrative gray levels encode these toy brightness
values (0–8), not calibrated display luminance or a full color pipeline.
Round counts are exact ONLY within this declared toy
model; animation seconds are viewing time, never GPU clock cycles or benchmarks.
Ignore transfers, launch/scheduling overhead, caches, divergence and unequal jobs.
No claim of guaranteed real speedup, real die layout or universal GPU superiority.

## Storyboard and review rubric

Grant: stable input/job/result identities make concurrency visible. Feynman:
“Can this job start without another job's answer?” precedes “dependency”.
Veritasium: optional prediction whether more lanes must help every workload;
show before/after graph change. Anatomy: a recognizable graphics board locates
chip and memory; the enlarged logical view declares its abstraction and returns
to the whole. Project label/manual-motion overrides apply.

| Beat | Focus and input → action → output | Visible evidence / static alternative |
| --- | --- | --- |
| Orient | GPU chip + memory; inputs → repeated work → results | Labeled physical board and miniature image |
| Independent work | Eight input values → same add-one operation on available lanes → eight results | Job IDs, arithmetic, working/ready/done states, true toy rounds |
| Waiting | Same jobs with a predecessor chain → only ready jobs start → same results | Prerequisite links, waiting reason and idle lanes |
| Recombine | Chip computes; memory holds data; dependencies constrain work | Whole-board return plus one short takeaway |

Interaction: one/four lanes, independent/chain, input hold/release. Rules live in a
pure domain module, not renderer/player. Reset and arbitrary seek are deterministic.
Prediction choices and skip precede deliberate reveal. Transfer before answer:
two independent chains of four jobs—can four lanes keep all four busy? Score 2:
at most two jobs ready at a time, each chain waits on its own predecessor; 1: right
direction without cause; 0: four lanes guarantee four simultaneous jobs. Teach-back
asks why eight independent jobs differ from one chain. Next-day variant: ready
independent work with missing data. No learner answers persist or enter logs.

## Build and gates

Reuse provider/gateway/config/accounting/Store, one isolated private ledger and the
existing $5 cumulative trial ceiling. One explicit Sonnet authoring call uses the
existing trusted art-first rates/limits; inspect before any deliberate revision.
No production route, database, Blob or Vercel writes. Viewing has no paid calls.
Generated art is manually inspected and hash-bound in an isolated build, never
loaded by the production declarative player. Shared local player/build controls
are new reusable modules; vacuum's approved-looking prototype is preserved, not
silently claimed to have been migrated into them.

CE-01–07: this brief, predictions, stable labeled jobs and causal changes.
CE-08–11: one exact toy scheduler, declared assumptions, deterministic shared poses.
CE-12–18: sources, transfer, keyboard/reduced-motion/static behavior, artifact hashes,
privacy and separate gates. No narrated MP4 is promised in this local slice.
Review 390/768/1280 widths in at most three bounded craft rounds, keyboard,
seeking/reset, reduced motion and loaded offline playback. Engineering tests do
not establish learning. Technical, actual-device, five-beginner and owner release
gates remain pending; owner can judge this candidate's craft separately.

## GPU-S2: restore sound deliberately (2026-10-19)

Observed failure: the owner expected audio, but GPU-S1 contained no narration
track and its CSP denied media. This is a playback omission, not evidence of a
muted phone. Preserve the silent HTML and its SHA before replacing the local view.

Bounded hypothesis: an explicit “Watch & listen” action with embedded computer
narration will play an intelligible story whose words, captions and depicted jobs
agree at arbitrary seek/pause points. A lane, dependency or data change must stop
that fixed narration before the scenario changes. The G1–G4 claim ledger above
still applies; add no performance claims. Transfer rubric and human learning
hypothesis stay unchanged. Grant: words follow visible job states; Feynman: short
causal sentences; Veritasium: retain prediction and transfer; Anatomy: retain the
whole-board locator and independent labeled logical view.

CE-08/11/14/18 implementation: one authored cue plan drives local speech synthesis,
spoken captions and reduced-motion stills. Embedded MP3 provides offline playback
without a provider call. The media clock drives the tour, with explicit play
failure, pause, seek, reset, mute and stale-request handling. Free exploration is
silent and must say so. No autoplay, device volume changes or narrated MP4 claim.
Review browser decoding/advancing clock, seeking, completion, interruption, offline,
keyboard and reduced-motion behavior separately from actual speaker/phone audibility.
Record the new artifact hash and missing human evidence; do not promote a catalog
lesson or claim the broader quality bar has passed.
