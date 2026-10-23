"""Typed authoring plans; sources and causal claims precede illustration geometry."""

from dataclasses import dataclass
from typing import Literal

from ..contracts import Source
from ..teaching_contracts import Assessment

Style = Literal["piston", "gear", "grip", "brake", "heat", "coil", "flow", "valve", "restrictor", "drum", "spray", "field", "filter", "trap", "tank", "compute"]


@dataclass(frozen=True)
class Step:
    title: str
    style: Style
    focus: int
    narration: str
    incoming: str
    outgoing: str
    source: int = 0
    locator: str = "How it works: working mechanism and input/output"


@dataclass(frozen=True)
class SystemPlan:
    id: str
    title: str
    category: Literal["Kitchen", "Home", "Technology", "Transport"]
    family: str
    idea: str
    core: tuple[str, ...]
    steps: tuple[Step, ...]
    sources: tuple[Source, ...]
    prediction: Assessment
    transfer: Assessment
    compare_stage: int
    normal: tuple[str, str]
    changed: tuple[str, str]
    limits: str
    aliases: tuple[str, ...] = ()


def source(title: str, url: str, supports: str) -> Source:
    """Ground generic claims without implying exact-model compatibility."""
    return Source.model_validate({"title": title, "url": url, "supports": supports})


def check(prompt: str, first: str, second: str, correct: int, explanation: str) -> Assessment:
    """An optional reveal with an explicit causal rubric, not answer collection."""
    return Assessment(prompt=prompt, choices=[first, second], correct=correct,
                      explanation=explanation, reasoning=[explanation],
                      misconception="A beginner may assume: " + [first, second][1-correct])
