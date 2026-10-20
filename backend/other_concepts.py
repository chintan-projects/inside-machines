"""Apply CE-1 to different mechanisms using the same contracts and renderers."""

from .contracts import LessonSpec, Stage
from .seed_geometry import part
from .teaching_authoring import Drawing
from .teaching_contracts import Beat, Claim, Property, TeachingSpec


def add_core_labels(spec: LessonSpec, labels: list[tuple[str, str, int, int]]) -> None:
    """Identify core hardware at readable, author-specified scene positions."""
    for target, text, x, y in labels:
        spec.parts.append(
            part(
                "label-" + target,
                text,
                "A permanent label identifying this working component.",
                "text",
                x,
                y,
                0,
                32,
                color="#29383d",
                label=text,
                layer=90,
            )
        )


def complete_concept(
    spec: LessonSpec,
    drawings: list[Drawing],
    changes: list[list[dict[str, object]]],
    rows: list[tuple[str, str, str, int, str]],
    teaching_data: dict[str, object],
    *,
    states: list[tuple[str, str, str]],
) -> LessonSpec:
    """Bind causal states, geometry, claims and legacy part identities in a new revision."""
    claims: list[Claim] = []
    beats: list[Beat] = []
    spec.stages = []
    for i, (title, text, focus, source, locator) in enumerate(rows):
        name, incoming, outgoing = states[i]
        claim = Claim(
            id=f"claim-{i}",
            statement=text,
            source=source,
            locator=locator,
            scope="generic",
            limitation="A generic qualitative teaching model; geometry and marker counts do not represent a specific appliance.",
        )
        claims.append(claim)
        spec.stages.append(
            Stage(
                title=title,
                explanation=text,
                narration=text,
                duration=18,
                parts=[focus],
                cause=text,
                input_state=incoming,
                output_state=outgoing,
                focus=focus,
                source_indices=[source],
            )
        )
        beats.append(
            Beat.model_validate(
                {
                    "id": f"beat-{i}",
                    "stage": i,
                    "short": title,
                    "requires": [] if i == 0 else [f"beat-{i - 1}"],
                    "claims": [claim.id],
                    "bridge": text.split(". ")[0] + ".",
                    "visible_change": text,
                    "static_explanation": text,
                    "action": "See this physical change",
                    "graphics": [p.id for p in drawings[i].parts],
                    "changes": changes[i],
                    "properties": [Property(name=name, before=incoming, after=outgoing)],
                }
            )
        )
    spec.teaching = TeachingSpec.model_validate(
        {"spec_version": "ce-1", "renderer": "declarative", "claims": claims, "beats": beats, **teaching_data}
    )
    spec.graphics = [p for d in drawings for p in d.parts]
    for p in spec.parts:
        p.motion = []
    parts = {p.id for p in spec.parts}
    for question in spec.questions:
        question.stage = min(question.stage, len(spec.stages) - 1)
        if question.part not in parts:
            question.part = spec.stages[question.stage].focus
    return LessonSpec.model_validate(spec.model_dump())
