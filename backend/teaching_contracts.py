"""Versioned, non-executable teaching data; no provider or presentation rules."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TeachingModel(BaseModel):
    """Validate all externally authored teaching metadata strictly."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Pose(TeachingModel):
    """A bounded visual pose, interpolated by all renderers, never executable code."""

    x: float = Field(default=0, ge=-900, le=900)
    y: float = Field(default=0, ge=-540, le=540)
    sx: float = Field(default=1, ge=0.05, le=4)
    sy: float = Field(default=1, ge=0.05, le=4)
    angle: float = Field(default=0, ge=-720, le=720)
    fill: str = Field(default="", pattern=r"^(#[0-9a-fA-F]{6})?$")
    opacity: float = Field(default=1, ge=0, le=1)


class Change(TeachingModel):
    """A meaningful visual transformation applied only within its teaching beat."""

    target: str = Field(pattern=r"^[a-z][a-z0-9-]{0,39}$")
    before: Pose
    after: Pose
    via: list[Pose] = Field(default_factory=list, max_length=6)


class Property(TeachingModel):
    """Qualitative input/output state; never an invented instrument reading."""

    name: str = Field(min_length=2, max_length=40)
    before: str = Field(min_length=2, max_length=80)
    after: str = Field(min_length=2, max_length=80)


class Claim(TeachingModel):
    """Source locator and applicability for one consequential assertion."""

    id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,39}$")
    statement: str = Field(min_length=15, max_length=400)
    source: int = Field(ge=0, le=7)
    locator: str = Field(min_length=5, max_length=180)
    scope: Literal["generic", "documented-model", "inference"]
    limitation: str = Field(min_length=10, max_length=300)


class Assessment(TeachingModel):
    """A prediction or transfer check, with a predeclared causal explanation."""

    prompt: str = Field(min_length=15, max_length=240)
    choices: list[str] = Field(min_length=2, max_length=4)
    correct: int = Field(ge=0, le=3)
    explanation: str = Field(min_length=30, max_length=700)
    reasoning: list[str] = Field(min_length=1, max_length=4)
    misconception: str = Field(min_length=15, max_length=240)

    @model_validator(mode="after")
    def choices_valid(self) -> "Assessment":
        """Reject ambiguous choices and an answer outside the offered range."""
        if self.correct >= len(self.choices) or len(set(self.choices)) != len(self.choices):
            raise ValueError("Assessment needs distinct choices and a valid answer")
        if any(not choice.strip() or len(choice) > 100 for choice in self.choices):
            raise ValueError("Assessment choice is empty or too long")
        return self


class Beat(TeachingModel):
    """Stable pedagogical identity mapped to an existing stage/media checkpoint."""

    id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,39}$")
    stage: int = Field(ge=0, le=6)
    short: str = Field(min_length=3, max_length=45)
    requires: list[str] = Field(max_length=6)
    claims: list[str] = Field(min_length=1, max_length=5)
    bridge: str = Field(min_length=10, max_length=220)
    visible_change: str = Field(min_length=15, max_length=250)
    static_explanation: str = Field(min_length=20, max_length=500)
    action: str = Field(min_length=3, max_length=65)
    graphics: list[str] = Field(min_length=2, max_length=50)
    changes: list[Change] = Field(min_length=1, max_length=30)
    properties: list[Property] = Field(min_length=1, max_length=4)


class Scenario(TeachingModel):
    """A declared qualitative counterfactual, shared by every output/client."""

    id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,39}$")
    label: str = Field(min_length=3, max_length=65)
    beat: str = Field(max_length=40)
    kind: Literal["qualitative"]
    context: Literal["outside", "inside", "none"]
    outcome: str = Field(min_length=5, max_length=100)
    explanation: str = Field(min_length=20, max_length=500)
    claims: list[str] = Field(min_length=1, max_length=5)
    changes: list[Change] = Field(max_length=30)


class TeachingSpec(TeachingModel):
    """CE-1 contract adds causal teaching without reinterpreting v1 artifacts."""

    spec_version: Literal["ce-1"]
    renderer: Literal["ac-cutaway-v2", "declarative"]
    renderer_fingerprint: str = Field(default="", pattern=r"^([a-f0-9]{64})?$")
    goal: str = Field(min_length=20, max_length=300)
    misconception: str = Field(min_length=15, max_length=300)
    core: list[str] = Field(min_length=3, max_length=10)
    operation: Literal["simultaneous", "sequential", "controlled"]
    operation_note: str = Field(min_length=20, max_length=300)
    invariants: list[str] = Field(min_length=1, max_length=6)
    claims: list[Claim] = Field(min_length=2, max_length=10)
    beats: list[Beat] = Field(min_length=3, max_length=7)
    prediction: Assessment
    transfer: Assessment
    teach_back: str = Field(min_length=15, max_length=240)
    teach_back_reasoning: list[str] = Field(min_length=2, max_length=5)
    scenarios: list[Scenario] = Field(min_length=2, max_length=4)

    @model_validator(mode="after")
    def coherent_story(self) -> "TeachingSpec":
        """Enforce stable identities, acyclic prerequisites and real references."""
        claims = {c.id for c in self.claims}
        if len(claims) != len(self.claims) or len(set(self.core)) != len(self.core):
            raise ValueError("Claim and core identities must be unique")
        seen: set[str] = set()
        for index, beat in enumerate(self.beats):
            if beat.id in seen or beat.stage != index or not set(beat.requires) <= seen:
                raise ValueError("Beats need unique stable IDs, ordered stages and earlier prerequisites")
            if not set(beat.claims) <= claims:
                raise ValueError("Beat refers to an unknown claim")
            if len({c.target for c in beat.changes}) != len(beat.changes):
                raise ValueError("A beat may change each graphic only once")
            seen.add(beat.id)
        if len({s.id for s in self.scenarios}) != len(self.scenarios):
            raise ValueError("Scenario identities must be unique")
        for scenario in self.scenarios:
            if scenario.beat not in seen or not set(scenario.claims) <= claims:
                raise ValueError("Scenario refers to an unknown beat or claim")
            if len({c.target for c in scenario.changes}) != len(scenario.changes):
                raise ValueError("A scenario may change each graphic only once")
        if self.prediction.prompt == self.transfer.prompt:
            raise ValueError("Transfer must ask about a changed situation")
        return self
