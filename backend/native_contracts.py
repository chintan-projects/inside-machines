"""Native studio v3 carries semantic teaching data, never substitute Part geometry."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .contracts import Source
from .teaching_contracts import Assessment, Claim

ID = r"^[a-z][a-z0-9-]{0,79}$"
SHA = r"^[a-f0-9]{64}$"


class NativeData(BaseModel):
    """Strict portable metadata; renderer functions belong to approved source modules."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class NativeRenderer(NativeData):
    id: str = Field(pattern=ID)
    fingerprint: str = Field(pattern=SHA)


class NativeComponent(NativeData):
    id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,39}$")
    name: str = Field(min_length=2, max_length=70)
    description: str = Field(min_length=10, max_length=500)
    label: str = Field(min_length=2, max_length=80)


class NativeStage(NativeData):
    """One actual narration cue; causal cues additionally need rendered mechanism change."""

    id: str = Field(pattern=ID)
    kind: Literal["orientation", "causal", "recombine"]
    start: float = Field(ge=0, le=600)
    end: float = Field(gt=0, le=600)
    still: float = Field(ge=0, le=600)
    title: str = Field(min_length=3, max_length=80)
    explanation: str = Field(min_length=20, max_length=900)
    narration: str = Field(min_length=20, max_length=900)
    duration: float = Field(gt=0, le=60)
    parts: list[str] = Field(min_length=1, max_length=20)
    cause: str = Field(min_length=10, max_length=400)
    input_state: str = Field(min_length=5, max_length=200)
    output_state: str = Field(min_length=5, max_length=200)
    focus: str = Field(min_length=1, max_length=40)
    source_indices: list[int] = Field(min_length=1, max_length=8)
    claims: list[str] = Field(min_length=1, max_length=10)


class NativeChoice(NativeData):
    value: str = Field(min_length=1, max_length=80)
    label: str = Field(min_length=1, max_length=100)


class NativeControl(NativeData):
    key: str = Field(pattern=ID)
    label: str = Field(min_length=3, max_length=100)
    options: list[NativeChoice] = Field(min_length=2, max_length=12)


class NativeAction(NativeData):
    id: str = Field(pattern=ID)
    label: str = Field(min_length=3, max_length=100)
    start: float = Field(ge=0, le=600)
    end: float = Field(gt=0, le=600)
    still: float = Field(ge=0, le=600)
    controls: dict[str, str] = Field(default_factory=dict, max_length=8)


class NativeScenario(NativeData):
    id: str = Field(pattern=ID)
    label: str = Field(min_length=3, max_length=100)
    kind: Literal["qualitative", "computed"]
    controls: dict[str, str] = Field(min_length=1, max_length=8)
    cue_id: str = Field(pattern=ID)
    outcome: str = Field(min_length=10, max_length=300)
    explanation: str = Field(min_length=20, max_length=700)
    claims: list[str] = Field(min_length=1, max_length=10)


class NativeTeaching(NativeData):
    goal: str = Field(min_length=20, max_length=400)
    misconception: str = Field(min_length=15, max_length=400)
    core: list[str] = Field(min_length=3, max_length=12)
    operation: Literal["simultaneous", "sequential", "controlled"]
    operation_note: str = Field(min_length=20, max_length=500)
    invariants: list[str] = Field(min_length=1, max_length=10)
    claims: list[Claim] = Field(min_length=2, max_length=20)
    prediction: Assessment
    transfer: Assessment
    teach_back: str = Field(min_length=15, max_length=300)
    teach_back_reasoning: list[str] = Field(min_length=2, max_length=6)
    scenarios: list[NativeScenario] = Field(min_length=2, max_length=12)


class NativeQuestion(NativeData):
    """Offline contextual answers address actual native cues, including timelines over seven cues."""

    question: str = Field(min_length=5, max_length=180)
    answer: str = Field(min_length=20, max_length=900)
    stage: int = Field(ge=0, le=23)
    part: str = Field(min_length=1, max_length=40)


class NativeLessonSpec(NativeData):
    """An additive artifact version; existing LessonSpec v1/v2 remain unchanged."""

    version: Literal[3] = 3
    spec_version: Literal["native-studio-1"] = "native-studio-1"
    title: str = Field(min_length=3, max_length=90)
    canonical: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=80)
    aliases: list[str] = Field(min_length=1, max_length=12)
    family: str = Field(min_length=4, max_length=120)
    question: str = Field(min_length=10, max_length=180)
    summary: str = Field(min_length=20, max_length=500)
    big_idea: str = Field(min_length=10, max_length=220)
    category: Literal["Kitchen", "Home", "Technology", "Transport", "Workshop", "Other"]
    accent: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    assumptions: list[str] = Field(min_length=1, max_length=12)
    sources: list[Source] = Field(min_length=1, max_length=8)
    renderer: NativeRenderer
    components: list[NativeComponent] = Field(min_length=3, max_length=40)
    stages: list[NativeStage] = Field(min_length=3, max_length=24)
    questions: list[NativeQuestion] = Field(min_length=3, max_length=6)
    prediction: str = Field(min_length=10, max_length=300)
    prediction_answer: str = Field(min_length=20, max_length=700)
    teaching: NativeTeaching
    controls: list[NativeControl] = Field(min_length=1, max_length=8)
    default_controls: dict[str, str] = Field(min_length=1, max_length=8)
    actions: list[NativeAction] = Field(min_length=1, max_length=12)

    @model_validator(mode="after")
    def connected_native_lesson(self) -> "NativeLessonSpec":
        """Check actual cue/control/component references without inventing geometric shapes."""
        components = {c.id for c in self.components}
        claims = {c.id: c for c in self.teaching.claims}
        cues = {c.id for c in self.stages}
        options = {c.key: {o.value for o in c.options} for c in self.controls}
        if (len(components) != len(self.components) or len(claims) != len(self.teaching.claims)
                or len(cues) != len(self.stages) or len(options) != len(self.controls)
                or len(set(self.teaching.core)) != len(self.teaching.core)
                or not set(self.teaching.core) <= components):
            raise ValueError("Native components, cues, claims and core identities must be real and unique")
        if any(c.source >= len(self.sources) for c in claims.values()):
            raise ValueError("Native claim references an absent source")
        elapsed = 0.0
        for cue in self.stages:
            if (abs(cue.start - elapsed) > .001 or cue.end <= cue.start
                    or abs(cue.duration - (cue.end - cue.start)) > .001
                    or not cue.start <= cue.still < cue.end):
                raise ValueError("Native cues must form one complete continuous narrated timeline")
            if (not set(cue.parts) <= components or cue.focus not in cue.parts
                    or cue.focus not in self.teaching.core or not set(cue.claims) <= claims.keys()
                    or not {claims[c].source for c in cue.claims} <= set(cue.source_indices)
                    or any(i < 0 or i >= len(self.sources) for i in cue.source_indices)):
                raise ValueError("Native cue needs a labeled core focus, input/output and applicable claim evidence")
            elapsed = cue.end
        if not any(c.kind == "causal" for c in self.stages):
            raise ValueError("A native explanation needs an actual causal working view")
        for control in self.controls:
            if len(options[control.key]) != len(control.options):
                raise ValueError("Native control choices must be distinct")
        if set(self.default_controls) != options.keys() or any(
            value not in options[key] | {"auto"} for key, value in self.default_controls.items()
        ):
            raise ValueError("Native initial controls must match their registered choices")
        if len({s.id for s in self.teaching.scenarios}) != len(self.teaching.scenarios):
            raise ValueError("Native scenarios must have unique identities")
        for scenario in self.teaching.scenarios:
            if (scenario.cue_id not in cues or not set(scenario.claims) <= claims.keys()
                    or any(key not in options or value not in options[key] for key, value in scenario.controls.items())):
                raise ValueError("Native scenario needs an actual cue, supported controls and evidence")
        if len({a.id for a in self.actions}) != len(self.actions):
            raise ValueError("Native action identities must be distinct")
        for action in self.actions:
            if (not 0 <= action.start <= action.still < action.end <= elapsed
                    or any(key not in options or value not in options[key] for key, value in action.controls.items())):
                raise ValueError("Native action exceeds its real timeline or controls")
        if any(q.stage >= len(self.stages) or q.part not in components for q in self.questions):
            raise ValueError("Native suggested question refers to an absent cue/component")
        if (self.prediction != self.teaching.prediction.prompt
                or self.prediction_answer != self.teaching.prediction.explanation
                or self.teaching.prediction.prompt == self.teaching.transfer.prompt):
            raise ValueError("Native assessments need consistent prediction and a different transfer question")
        return self
