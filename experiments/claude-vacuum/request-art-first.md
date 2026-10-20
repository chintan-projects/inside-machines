# Make a machine someone wants to explore

Create ONE complete standalone HTML page answering: “How does a vacuum cleaner
pick up dirt?” Your job is visual design and interactive authoring. The audience
is curious beginners, broadly 8–80. Answer enough to satisfy curiosity; let extra
depth recede. Return only HTML, starting <!doctype html>, no fences or analysis.
Target 350–500 lines using reusable drawing helpers, not unrolled markup.

Give it a beautiful, tactile, recognizably physical CANISTER vacuum, its side
opened to reveal the working parts. Think a carefully illustrated science book:
well-made coloured housing, rubber wheels, brushed-metal motor, fitted shaft,
curved fan/impeller blades, pleated bag, corrugated hose, an actual floor nozzle,
seams, screws, inlet collars, a handle and an outlet grille. Every detail belongs
to a real part. Filled volumes with several side shades, fine ink edges, short
neutral shadows. Make the object large and inviting. It is not a flat infographic.
Invent your own coherent palette, type and composition. Avoid a dashboard/card grid.

Take these moves from Elvar's original Anatomy workflow: concrete actions on the
object, a window that reveals work, one short hint for the visible change, one
authoritative pure model, deterministic seek for inspection. Grant: show the
causal relationship rather than repeat words. Feynman: name a job in plain words
before jargon. Veritasium: an optional prediction, then a visible counterfactual.
Anatomy: the recognizable connected physical object carries the explanation.

The causal chain for this GENERIC CLEAN-AIR BAGGED cleaner is:
electric motor → shaft → fan moves air → lower inlet-side pressure lets surrounding
room air enter the nozzle, carrying some loose dirt → hose takes both into the bag
→ the porous bag retains dirt, AIR passes through its walls → air reaches fan inlet
→ fan outlet exhausts air back to the room. All jobs operate together, not as a
sequence of machine on/off states. Your buttons change the learner's attention.
Do not send air through a solid motor, a sealed shell or an unconnected tube.
Do not send dirt through the bag to the outlet. No invented pressure/RPM/numbers.
This is a qualitative cutaway, not a simulation or a specific manufacturer's model.

Offer a MANUAL path and an optional ~45-second tour. Use a few action buttons
such as turn on, follow the air, look inside the bag. Next/replay can revisit.
Make the biggest action obvious within the initial phone screen, not buried below
a tall diagram. A short hint changes with the action. Return to the whole machine
and one plain takeaway. One optional thought experiment asks what happens if the
inlet is sealed airtight, with choices and a “Show me” skip BEFORE the answer.
Then show: the fan may still turn, but sustained INCOMING throughflow/pickup stops.
This is the ideal steady condition; real leaks/bypasses/transients are omitted.
The experiment changes only the drawing; never suggest blocking a real vacuum.
Optional transfer question before revealing: what if the hose is kinked airtight?

Use the REAL supplied Anatomy library to construct important physical parts.
Include <!-- ANATOMY_RUNTIME --> exactly once in your head. Our build replaces
it with a bundled script defining window.Anatomy = {k,G,T}. k is iso-kit.mjs, G
is lathe.mjs, T is tube.mjs. Their actual API reference follows this prompt.
No imports. Example usage: const {k,G,T}=window.Anatomy; append k.ISO_CSS to a
style element. k.fitProjection(extremePoints,width,height,{pad,azimuth,elevation})
sets projection P; k.iso([x,y,z],P) projects. k.solidSvg(k.slabOf(plan,z,h,P,8,1),
{tone:'hi'}) makes a bevelled filled solid. A plan is {x,y,w,d,r}. For round parts
G.frameAlong(origin,axis), G.lathe([[s,r],...],F,P), G.disc(s0,s1,r,F,P).
For hoses use T.tubePieces(route,r,P,{rings:{step:5,width:.5}}).map(T.tubeSvg)
or the documented polyline helpers. Check exact signatures before using functions.
Override --anatomy-* material tokens per group for the desired crafted finish.
Keep sensible painter order. No geometry-audit claim without the actual audit.

REQUIRED project override to upstream Anatomy: core parts have large anchored
on-scene labels (short leaders are fine). At a 390px viewport labels must still
read at least ~12px; prefer responsive HTML labels or sufficiently large SVG type.
Air and dirt differ by shape and direction, not colour alone. Provide a legend.
Keep a working mechanism and its physical surroundings visible in any closeup.

Implement a single pure stateAt(time,blocked) function. All drawing, hint text,
manual controls, playback and static poses use it. Expose window.vacuumStudy with
seek(seconds), play(), pause(), setBlocked(boolean), reset(), getState(). getState
returns time, playing, blocked, beat and a readable airflow/dirt/fan description.
Expose window.seek(t) as alias. Seek any time in any order deterministically.
No autoplay. ?render stops the clock. Honour reduced motion with meaningful still
poses/manual progress. Semantic buttons ≥44px, visible focus, no horizontal
overflow at 390/768/1280px. Keep the drawing prominent on mobile and desktop.

Use only embedded SVG/CSS/JS, no fetch, external fonts/assets, storage, telemetry,
eval, remote imports, microphone or speech. A network-denying CSP will be added.
Add a small sources/scope disclosure, not a wall of text above the object:
Dyson FAQ “How do vacuums work?” https://www.dyson.com/vacuum-cleaners.asp;
Dyson “It started with a cyclone” bag filtration section at
https://www.dyson.com/discover/innovation/behind-the-invention/filtration-at-dyson.
The blocked-inlet behavior is a qualitative mass-continuity inference. Technical
review and human learning results remain pending. Status can be in the footer;
the first impression should invite curiosity. No fabricated approval or scores.

Deliver a complete functioning page. Spend the pixels on the physical explanation.
