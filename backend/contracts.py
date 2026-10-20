"""Validated, non-executable lesson contract shared with all future clients."""

import math
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from .teaching_contracts import TeachingSpec


class StrictModel(BaseModel):
    """Reject undeclared provider output fields."""

    model_config = ConfigDict(extra="forbid")


class Source(StrictModel):
    """A source that supports the lesson, with its actual scope recorded."""

    title: str = Field(min_length=3, max_length=180)
    url: HttpUrl
    supports: str = Field(min_length=10, max_length=500)


class Motion(StrictModel):
    """Bounded keyframed transform; never executable code."""

    stage: int = Field(ge=0, le=7)
    kind: Literal["rotate", "translate", "pulse", "flow"]
    amount: float = Field(ge=-720, le=720)
    axis: Literal["x", "y"]


class Part(StrictModel):
    """A recognizable part assembled from a small safe geometric vocabulary."""

    id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,39}$")
    name: str = Field(min_length=2, max_length=70)
    description: str = Field(min_length=10, max_length=500)
    shape: Literal["box", "ellipse", "ring", "path", "polygon", "text"]
    x: float = Field(ge=0, le=900)
    y: float = Field(ge=0, le=540)
    w: float = Field(ge=0, le=900)
    h: float = Field(ge=0, le=540)
    color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    stroke: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    points: list[list[float]] = Field(max_length=50)
    label: str = Field(max_length=50)
    layer: int = Field(ge=0, le=100)
    motion: list[Motion] = Field(max_length=8)

    @model_validator(mode="after")
    def safe_geometry(self) -> "Part":
        """Prevent invalid geometry, unsupported paths, or nonfinite coordinates."""
        if any(
            len(p) != 2 or not all(math.isfinite(v) and -1000 <= v <= 2000 for v in p) for p in self.points
        ):
            raise ValueError("Each point must have two bounded finite coordinates")
        if self.shape in ("path", "polygon") and len(self.points) < 2:
            raise ValueError("Paths and polygons need points")
        return self


class Stage(StrictModel):
    """One synchronized explanatory and narrated step."""

    title: str = Field(min_length=3, max_length=80)
    explanation: str = Field(min_length=20, max_length=700)
    narration: str = Field(min_length=20, max_length=700)
    duration: float = Field(ge=5, le=25)
    parts: list[str] = Field(min_length=1, max_length=20)
    cause: str = Field(min_length=10, max_length=300)
    input_state: str = Field(default="", max_length=160)
    output_state: str = Field(default="", max_length=160)
    focus: str = Field(default="", max_length=40)
    source_indices: list[int] = Field(default_factory=list, max_length=8)


class Question(StrictModel):
    """Authored contextual answer that remains useful offline."""

    question: str = Field(min_length=5, max_length=180)
    answer: str = Field(min_length=20, max_length=900)
    stage: int = Field(ge=0, le=7)
    part: str = Field(max_length=40)


class LessonSpec(StrictModel):
    """Portable visual teaching artifact, independent from runtime model provider."""

    version: Literal[1, 2]
    title: str = Field(min_length=3, max_length=90)
    canonical: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=80)
    aliases: list[str] = Field(min_length=1, max_length=12)
    family: str = Field(min_length=4, max_length=120)
    question: str = Field(min_length=10, max_length=180)
    summary: str = Field(min_length=20, max_length=500)
    big_idea: str = Field(min_length=10, max_length=220)
    category: Literal["Kitchen", "Home", "Technology", "Transport", "Workshop", "Other"]
    accent: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    assumptions: list[str] = Field(min_length=1, max_length=8)
    sources: list[Source] = Field(min_length=1, max_length=8)
    parts: list[Part] = Field(min_length=8, max_length=120)
    stages: list[Stage] = Field(min_length=3, max_length=7)
    questions: list[Question] = Field(min_length=3, max_length=6)
    prediction: str = Field(min_length=10, max_length=300)
    prediction_answer: str = Field(min_length=20, max_length=500)
    teaching: TeachingSpec | None = None
    graphics: list[Part] = Field(default_factory=list, max_length=120)

    @model_validator(mode="after")
    def connected_lesson(self) -> "LessonSpec":
        """Require real references and a bounded, useful narration."""
        ids = {part.id for part in self.parts}
        if len(ids) != len(self.parts):
            raise ValueError("Part identifiers must be unique")
        for stage in self.stages:
            if not set(stage.parts).issubset(ids):
                raise ValueError("A stage references an unknown part")
        for stage in self.stages:
            if stage.focus and stage.focus not in ids:
                raise ValueError("Stage focus references an unknown component")
            if any(index < 0 or index >= len(self.sources) for index in stage.source_indices):
                raise ValueError("Stage evidence references an unknown source")
        if any(m.stage >= len(self.stages) for p in self.parts for m in p.motion):
            raise ValueError("Motion references an unknown stage")
        if any(q.stage >= len(self.stages) or (q.part and q.part not in ids) for q in self.questions):
            raise ValueError("Question references an unknown stage or part")
        if sum(len(stage.narration.split()) for stage in self.stages) > 260:
            raise ValueError("Narration exceeds the alpha's 260-word budget")
        if self.version == 1 and (self.teaching is not None or self.graphics):
            raise ValueError("Teaching metadata requires a new v2 lesson revision")
        if self.version == 2:
            self._validate_teaching(ids)
        return self

    def _validate_teaching(self, ids: set[str]) -> None:
        """Validate the CE contract against the actual mechanism and drawings."""
        teaching = self.teaching
        if teaching is None or len(teaching.beats) != len(self.stages):
            raise ValueError("V2 requires teaching beats for every stage")
        if not set(teaching.core) <= ids:
            raise ValueError("Teaching core refers to unknown components")
        if any(claim.source >= len(self.sources) for claim in teaching.claims):
            raise ValueError("Claim refers to an unknown source")
        graphics = {p.id for p in self.graphics}
        if len(graphics) != len(self.graphics) or graphics & ids:
            raise ValueError("Graphics need distinct identities separate from mechanism parts")
        for beat in teaching.beats:
            if not set(beat.graphics) <= graphics or not {c.target for c in beat.changes} <= set(
                beat.graphics
            ):
                raise ValueError("Beat changes must target its declared graphics")
        for scenario in teaching.scenarios:
            beat = next(b for b in teaching.beats if b.id == scenario.beat)
            if not {c.target for c in scenario.changes} <= set(beat.graphics):
                raise ValueError("Scenario changes must target its declared beat graphics")
        if teaching.renderer == "ac-cutaway-v2" and self.canonical != "air-conditioner-ce-1":
            raise ValueError("Authored AC renderer is reserved for its immutable revision")


class AnswerSpec(StrictModel):
    """A contextual answer can only select existing visual actions."""

    answer: str = Field(min_length=10, max_length=2200)
    stage: int | None
    part: str | None
    source_indices: list[int] = Field(max_length=8)
    uncertain: bool


class ReviewSpec(StrictModel):
    """Automated editorial decision, never presented as human verification."""

    accepted: bool
    notes: list[str] = Field(max_length=10)
    lesson: LessonSpec


class ReviewDecision(StrictModel):
    """A verdict bound to the exact draft, without regenerating its scene."""

    accepted: bool
    notes: list[str] = Field(max_length=10)
    spec_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class AuthorLessonSpec(LessonSpec):
    """New authoring must use CE-1; historical v1 readers remain supported."""

    version: Literal[2] = 2
    teaching: TeachingSpec
    graphics: list[Part] = Field(min_length=2, max_length=120)


class TeachingReviewSpec(ReviewSpec):
    """A new lesson cannot lose its teaching contract during editorial review."""

    lesson: AuthorLessonSpec


def canonicalize(question: str) -> str:
    """Normalize common equivalent machine requests before any paid call."""
    q = re.sub(r"[^a-z0-9 /-]", " ", question.lower()).replace("-", " ").strip()
    # Preserve mechanism-changing qualifiers instead of returning a misleading hit.
    if re.search(r"\btop[ -]?load(?:ing|er)?\b", q) and re.search(r"wash|laundry", q):
        return "top-load-washing-machine"
    if re.search(r"\bstove[ -]?top\b", q) and "pressure" in q:
        return "stovetop-pressure-cooker"
    if electrical := re.search(r"\bac (motor|generator|circuit|power)\b", q):
        return "ac-" + electrical.group(1)
    if re.search(r"air condition|aircon|\ba/c\b|\bac\b", q):
        for qualifier in ("window", "portable", "car", "automotive"):
            if re.search(r"\b" + qualifier + r"\b", q):
                return ("automotive" if qualifier == "car" else qualifier) + "-air-conditioner"
    if "television" in q or re.search(r"\btv\b", q):
        for qualifier in ("oled", "lcd", "crt"):
            if re.search(r"\b" + qualifier + r"\b", q):
                return qualifier + "-television"
    if "espresso" in q and "lever" in q:
        return "lever-espresso-machine"
    aliases = {
        "air-conditioner": r"\b(air condition(?:er|ing|ers)|aircon|a/c|ac)\b",
        "washing-machine": r"\b(washing machine|washer|laundry machine)\b",
        "refrigerator": r"\b(fridge|refrigerator|refrigeration)\b",
        "pressure-cooker": r"\b(pressure cooker|instant pot)\b",
        "television": r"\b(tv|television|televisions)\b",
        "espresso-machine": r"\bespresso\b",
    }
    for key, pattern in aliases.items():
        if re.search(pattern, q):
            return key
    stop = {
        "how",
        "does",
        "do",
        "a",
        "an",
        "the",
        "work",
        "works",
        "working",
        "can",
        "you",
        "tell",
        "me",
        "about",
        "explain",
        "please",
        "what",
        "is",
        "to",
        "understand",
    }
    words = [w for w in re.findall(r"[a-z0-9]+", q) if w not in stop]
    return "-".join(words)[:80].strip("-")
