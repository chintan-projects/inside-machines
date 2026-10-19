"""Validated, non-executable lesson contract shared with all future clients."""

import math
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


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


class Question(StrictModel):
    """Authored contextual answer that remains useful offline."""

    question: str = Field(min_length=5, max_length=180)
    answer: str = Field(min_length=20, max_length=900)
    stage: int = Field(ge=0, le=7)
    part: str = Field(max_length=40)


class LessonSpec(StrictModel):
    """Portable visual teaching artifact, independent from runtime model provider."""

    version: Literal[1]
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
    parts: list[Part] = Field(min_length=8, max_length=65)
    stages: list[Stage] = Field(min_length=3, max_length=7)
    questions: list[Question] = Field(min_length=3, max_length=6)
    prediction: str = Field(min_length=10, max_length=300)
    prediction_answer: str = Field(min_length=20, max_length=500)

    @model_validator(mode="after")
    def connected_lesson(self) -> "LessonSpec":
        """Require real references and a bounded, useful narration."""
        ids = {part.id for part in self.parts}
        if len(ids) != len(self.parts):
            raise ValueError("Part identifiers must be unique")
        for stage in self.stages:
            if not set(stage.parts).issubset(ids):
                raise ValueError("A stage references an unknown part")
        if any(m.stage >= len(self.stages) for p in self.parts for m in p.motion):
            raise ValueError("Motion references an unknown stage")
        if any(q.stage >= len(self.stages) or (q.part and q.part not in ids) for q in self.questions):
            raise ValueError("Question references an unknown stage or part")
        if sum(len(stage.narration.split()) for stage in self.stages) > 260:
            raise ValueError("Narration exceeds the alpha's 260-word budget")
        return self


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
