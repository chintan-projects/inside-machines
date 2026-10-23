"""One safe CE compiler for independently scoped systems, never executable model output."""

from collections.abc import Callable

from ..contracts import LessonSpec, Question, Stage
from ..quality import require_learning_quality
from ..teaching_authoring import Drawing
from ..teaching_contracts import Beat, Claim, Property, Scenario, TeachingSpec
from . import mechanics, panels, separation, specialties
from .catalog import SYSTEMS
from .connections import LINKS, reunion
from .plans import Step, SystemPlan

BUILDERS: dict[str, Callable[[SystemPlan, Step, int], panels.Panel]] = {
    "heat": panels.heat, "coil": panels.coil, "flow": panels.flow,
    "valve": panels.valve, "restrictor": panels.restrictor, "tank": panels.tank,
    "piston": mechanics.piston, "gear": mechanics.rotor, "drum": mechanics.drum,
    "grip": mechanics.contact, "brake": mechanics.contact, "filter": separation.filter_panel,
    "field": separation.field, "spray": separation.spray, "trap": separation.trap,
    "compute": separation.compute,
}


def panel(plan: SystemPlan, step: Step, index: int) -> panels.Panel:
    """Select trusted physical rules at authoring time; the runtime stays topic-independent."""
    if step.style == "valve" and plan.id in {"electric-oven", "electric-kettle", "water-heater", "pressure-cooker"}:
        return specialties.circuit(plan, step, index)
    if step.style == "valve" and plan.id == "heat-pump":
        return specialties.reversing(plan, step, index)
    if step.style == "heat" and plan.id == "clothes-dryer":
        return specialties.dryer_heat(plan, step, index)
    if step.style == "heat" and plan.id == "induction-cooktop":
        return separation.field(plan, step, index)
    if step.style == "flow" and plan.id == "water-heater":
        return specialties.storage_flow(plan, step, index)
    if step.style == "flow" and plan.id in {"table-fan", "electric-oven"}:
        return specialties.air_motion(plan, step, index)
    if step.style == "flow" and plan.id == "faucet":
        return specialties.mixing(plan, step, index)
    if step.style == "valve" and plan.id == "faucet":
        return specialties.disc(plan, step, index)
    if step.style == "trap" and plan.id == "toilet":
        return specialties.toilet_trap(plan, step, index)
    return BUILDERS[step.style](plan, step, index)


def context(plan: SystemPlan) -> Drawing:
    """A labeled locator diagram is explicit about layout; it is not a false physical cutaway."""
    d = Drawing("")
    d.box("system-boundary", 60, 80, 780, 380, "#edf2f7")
    d.text("layout", "System map · positions simplified", 100, 28, 30)
    for i, name in enumerate(plan.core):
        x, y = 100, 105 + i*85
        d.box(f"component-{i}", 720, y-2, 65, 40, "#b7cada")
        d.text(f"label-component-{i}", name, x, y, 32)
    while len(d.parts) < 8:
        d.box("locator-" + str(len(d.parts)), 410, 260, 24, 12, "#748c9f")
    return d


def compile_system(key: str) -> LessonSpec:
    """Compile a source-led plan to all shared media/player/assessment contracts."""
    plan = SYSTEMS[key]
    together = plan.idea + " " + ". ".join(link[2] for link in LINKS[key]) + ". The map connects jobs; it is not their physical layout or a start-up sequence."
    steps = (*plan.steps, Step("Put the whole system together", "flow", 0, together,
                              "Inputs reach the working parts", "The connected jobs produce a useful output"))
    views = [panel(plan, step, i) for i, step in enumerate(plan.steps)] + [reunion(plan, len(plan.steps))]
    # At a 343px phone scene, 40 source pixels are approximately 15px. Tiny
    # labels were a concrete earlier failure, so reserve space before rendering.
    for view in views:
        for graphic in view.drawing.parts:
            if graphic.shape == "text" and len(graphic.label) <= 25:
                graphic.h = max(40, graphic.h)
                graphic.x = min(graphic.x, 870 - len(graphic.label) * graphic.h * .62)
    claims, beats, stages = [], [], []
    for i, (step, view) in enumerate(zip(steps, views, strict=True)):
        sentences = step.narration.split(". ")
        first = sentences[0].rstrip(".") + "."
        claims.append(Claim(id=f"claim-{i}", statement=step.narration, source=step.source,
                            locator=step.locator, scope="generic", limitation=plan.limits))
        beats.append(Beat(id=f"beat-{i}", stage=i, short=step.title,
                          requires=[] if i == 0 else [f"beat-{i-1}"], claims=[f"claim-{i}"],
                          bridge=first, visible_change=f"{step.incoming} becomes {step.outgoing}.",
                          static_explanation=step.narration if i < len(plan.steps) else plan.idea + " Follow the linked jobs. This is a relationship map, not their physical layout or a start-up sequence.", action="See " + step.title.lower(),
                          graphics=[p.id for p in view.drawing.parts], changes=view.changes,
                          properties=[Property(name="This change", before=step.incoming, after=step.outgoing)]))
        stages.append(Stage(title=step.title, explanation=step.narration, narration=step.narration,
                            duration=18, parts=[f"component-{step.focus}"], cause=first,
                            input_state=step.incoming, output_state=step.outgoing,
                            focus=f"component-{step.focus}", source_indices=[step.source]))
    i = plan.compare_stage
    teaching = TeachingSpec(spec_version="ce-1", renderer="declarative", goal=plan.idea,
        misconception=plan.prediction.misconception, core=[f"component-{j}" for j in range(len(plan.core))],
        operation="controlled", operation_note="Chapters isolate related jobs. They are explanation steps, not a real-time operating sequence.",
        invariants=["Energy and matter are transferred or stored, never created by the illustration.", plan.limits],
        claims=claims, beats=beats, prediction=plan.prediction, transfer=plan.transfer,
        teach_back="Explain how the input becomes the result, and what changes in the comparison.",
        teach_back_reasoning=[plan.idea, plan.changed[1]],
        scenarios=[Scenario(id="normal", label=plan.normal[0], beat=f"beat-{i}", kind="qualitative", context="none",
                            outcome=plan.normal[0], explanation=plan.normal[1], claims=[f"claim-{i}"], changes=views[i].changes),
                   Scenario(id="changed", label=plan.changed[0], beat=f"beat-{i}", kind="qualitative", context="none",
                            outcome=plan.changed[0], explanation=plan.changed[1], claims=[f"claim-{i}"], changes=views[i].alternate)])
    questions = [Question(question=plan.prediction.prompt, answer=plan.prediction.explanation, stage=0, part="component-0"),
                 Question(question=plan.transfer.prompt, answer=plan.transfer.explanation, stage=i, part=f"component-{plan.steps[i].focus}"),
                 Question(question="What does this model leave out?", answer=plan.limits, stage=0, part="component-0")]
    spec = LessonSpec(version=2, canonical=f"{plan.id}-studio-1", title=plan.title, aliases=[plan.id, *plan.aliases],
                      family=plan.family, question=f"How does a {plan.title.lower()} work?", summary=plan.idea,
                      big_idea=plan.idea, category=plan.category, accent="#365cd4",
                      assumptions=[plan.family, plan.limits], sources=list(plan.sources), parts=context(plan).parts,
                      stages=stages, questions=questions, prediction=plan.prediction.prompt,
                      prediction_answer=plan.prediction.explanation, teaching=teaching,
                      graphics=[p for v in views for p in v.drawing.parts])
    require_learning_quality(spec)
    return spec
