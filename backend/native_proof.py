"""Verify real native render checkpoints; no geometric placeholder can satisfy this gate."""

import hashlib
import re
from typing import Literal
from xml.etree import ElementTree

from pydantic import Field

from .native_contracts import ID, SHA, NativeData, NativeLessonSpec
from .native_registry import canonical_digest, renderer_for


class NativeLabel(NativeData):
    text: str = Field(min_length=1, max_length=120)
    x: float
    y: float


class NativeViewport(NativeData):
    x: float
    y: float
    width: float = Field(gt=0, le=2000)
    height: float = Field(gt=0, le=2000)


class NativeFrame(NativeData):
    cue_id: str = Field(pattern=ID)
    time: float = Field(ge=0, le=600)
    scenario_id: str = Field(default="", max_length=80)
    controls: dict[str, str] = Field(max_length=8)
    svg: str = Field(min_length=30, max_length=500000)
    labels: list[NativeLabel] = Field(max_length=40)
    viewport: NativeViewport
    caption: str = Field(min_length=20, max_length=2400)
    alt: str = Field(min_length=20, max_length=2400)


class NativeProof(NativeData):
    schema_version: Literal["native-proof-1"]
    renderer_id: str = Field(pattern=ID)
    renderer_fingerprint: str = Field(pattern=SHA)
    spec_sha256: str = Field(pattern=SHA)
    video_sha256: str = Field(pattern=SHA)
    video_duration: float = Field(gt=0, le=600)
    fps: Literal[24]
    width: Literal[1280]
    height: Literal[866]
    frames: list[NativeFrame] = Field(min_length=3, max_length=100)


TAGS = {"svg", "g", "defs", "path", "rect", "circle", "ellipse", "line", "polyline", "polygon",
        "text", "tspan", "linearGradient", "radialGradient", "stop", "clipPath", "mask", "pattern",
        "filter", "feGaussianBlur", "feOffset", "feMerge", "feMergeNode", "feColorMatrix", "marker", "title", "desc", "style"}
GEOMETRY = {"d", "x", "y", "x1", "x2", "y1", "y2", "width", "height", "cx", "cy", "r", "rx", "ry", "points", "transform", "opacity"}


def _visible(label: str, texts: set[str]) -> bool:
    return any(label.casefold() in text.casefold() for text in texts)


def inspect_svg(frame: NativeFrame) -> tuple[set[str], str]:
    """Accept bounded SVG structure and local paint references, never executable resources."""
    if re.search(r"<!DOCTYPE|<!ENTITY", frame.svg, re.I):
        raise ValueError("Native scene cannot contain document/entity declarations")
    try:
        root = ElementTree.fromstring(frame.svg if frame.svg.lstrip().startswith("<svg")
                                      else '<svg xmlns="http://www.w3.org/2000/svg">' + frame.svg + '</svg>')
    except ElementTree.ParseError as exc:
        raise ValueError("Native scene must contain valid final SVG") from exc
    texts: set[str] = set()
    geometry: list[object] = []
    count = 0
    for node in root.iter():
        count += 1
        if count > 8000:
            raise ValueError("Native scene exceeds its bounded element count")
        tag = node.tag.split("}")[-1]
        if tag not in TAGS:
            raise ValueError("Native scene contains an unsupported executable/resource element")
        if tag == "style" and re.search(r"@import|url\(|https?:|expression\s*\(", node.text or "", re.I):
            raise ValueError("Native scene CSS cannot load external resources")
        for key, value in node.attrib.items():
            local = key.split("}")[-1].lower()
            if (local.startswith("on") or "href" in local
                    or any(not ref.strip().strip("'\"").startswith("#") for ref in re.findall(r"url\((.*?)\)", value, re.I))
                    or re.search(r"javascript:|https?:|\b(?:NaN|Infinity)\b", value, re.I)):
                raise ValueError("Native scene attributes cannot execute code or fetch resources")
        if tag in ("text", "tspan"):
            value = " ".join("".join(node.itertext()).split())
            if value:
                texts.add(value)
        geometry.append([tag, {key: value for key, value in node.attrib.items() if key in GEOMETRY}])
    for label in frame.labels:
        if not (frame.viewport.x <= label.x <= frame.viewport.x + frame.viewport.width
                and frame.viewport.y <= label.y <= frame.viewport.y + frame.viewport.height):
            raise ValueError("Native on-scene label leaves its own viewport")
        texts.add(" ".join(label.text.split()))
    return texts, canonical_digest(geometry)


def native_spec_issues(spec: NativeLessonSpec) -> list[str]:
    """Structural floor for the real native contract; human acceptance remains separate."""
    try:
        renderer_for(spec)
    except (ValueError, OSError):
        return ["The exact native renderer source and lesson metadata are unavailable or changed"]
    return []


def verify_proof(spec: NativeLessonSpec, proof: NativeProof) -> None:
    """Require source-bound actual focus labels, real causal changes and reviewed scenarios."""
    from .starters import digest_spec

    renderer_for(spec)
    if (proof.renderer_id != spec.renderer.id or proof.renderer_fingerprint != spec.renderer.fingerprint
            or proof.spec_sha256 != digest_spec(spec)
            or abs(proof.video_duration - spec.stages[-1].end) > .15):
        raise ValueError("Native proof must bind the exact source, spec and narrated media timeline")
    components = {c.id: c for c in spec.components}
    cues = {c.id: c for c in spec.stages}
    scenarios = {s.id: s for s in spec.teaching.scenarios}
    baseline: dict[str, list[tuple[NativeFrame, str]]] = {cue: [] for cue in cues}
    covered_scenarios: set[str] = set()
    whole = False
    seen: set[str] = set()
    for frame in proof.frames:
        cue = cues.get(frame.cue_id)
        if cue is None or not cue.start <= frame.time < cue.end:
            raise ValueError("Native proof frame falls outside its real narration cue")
        key = canonical_digest({"cue": frame.cue_id, "time": frame.time, "scenario": frame.scenario_id,
                                "controls": frame.controls})
        if key in seen:
            raise ValueError("Native proof cannot duplicate a checkpoint")
        seen.add(key)
        texts, geometry = inspect_svg(frame)
        if not _visible(components[cue.focus].label, texts):
            raise ValueError("Every native working view needs its own visible focus label")
        whole = whole or all(_visible(components[c].label, texts) for c in spec.teaching.core)
        if frame.scenario_id:
            scenario = scenarios.get(frame.scenario_id)
            expected = {**spec.default_controls, **scenario.controls} if scenario else {}
            if scenario is None or scenario.cue_id != cue.id or frame.controls != expected:
                raise ValueError("Native scenario frame must use its exact reviewed controls and cue")
            covered_scenarios.add(scenario.id)
        else:
            if frame.controls != spec.default_controls:
                raise ValueError("Native default cue proof must use its exact initial controls")
            baseline[cue.id].append((frame, geometry))
    if not whole:
        raise ValueError("Native proof needs a whole-system locator with every anchored core label")
    for cue in spec.stages:
        frames = baseline[cue.id]
        if not any(abs(frame.time - cue.still) <= .001 for frame, _ in frames):
            raise ValueError("Every native narration cue needs its exact reduced-motion checkpoint")
        if cue.kind == "causal" and len({geometry for _, geometry in frames}) < 2:
            raise ValueError("Every native causal cue needs a visible mechanism change beyond color")
    if covered_scenarios != set(scenarios):
        raise ValueError("Every reviewed native scenario needs an actual rendered checkpoint")


def proof_digest(proof: NativeProof) -> str:
    """Bind private production evidence without logging or exposing its full scene payload."""
    return hashlib.sha256(proof.model_dump_json().encode()).hexdigest()
