"""Local trusted native media export; no provider, storage or publication operations."""

import hashlib
import io
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Timer
from time import perf_counter
from xml.etree import ElementTree as ET

import imageio_ffmpeg  # type: ignore[import-untyped]  # Upstream has no typing marker.
import resvg_py
from _shared.services.logger import get_logger
from PIL import Image, ImageDraw
from pydantic import BaseModel, ConfigDict

from .native_contracts import NativeLessonSpec
from .native_proof import NativeFrame, NativeProof, inspect_svg, verify_proof
from .native_registry import canonical_digest, renderer_for, verify_sources
from .render import audio_duration, scene_font
from .settings import ROOT
from .starters import digest_spec

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
logger = get_logger(__name__)


class AttributeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    selector: str
    name: str
    value: str


class RawFrame(NativeFrame):
    """Additional trusted renderer hints consumed before immutable proof serialization."""

    contentKey: str | None = None
    attributes: list[AttributeUpdate] = []


def materialize(frame: RawFrame) -> NativeFrame:
    """Apply a deliberately bounded subset of the player's SVG attribute updates."""
    inspect_svg(frame)
    wrapped = '<svg xmlns="' + NS + '">' + frame.svg + '</svg>'
    root = ET.fromstring(wrapped)
    for update in frame.attributes:
        match = re.fullmatch(r"\[(data-[a-z0-9-]+)\]", update.selector)
        identity = re.fullmatch(r"#([a-z][a-z0-9-]*)", update.selector)
        if (not (match or identity) or update.name not in {"width", "opacity", "transform"}
                or len(update.value) > 200 or re.search(r"NaN|Infinity|url|[<>]", update.value)):
            raise ValueError("Native export cannot materialize an unsupported attribute update")
        nodes = [node for node in root.iter() if
                 (match is not None and match[1] in node.attrib)
                 or (identity is not None and node.get("id") == identity[1])]
        if not nodes:
            raise ValueError("Native export update has no corresponding scene element")
        for node in nodes:
            node.set(update.name, update.value)
    value = frame.model_dump(exclude={"attributes", "contentKey"})
    value["svg"] = "".join(ET.tostring(node, encoding="unicode") for node in root)
    final = NativeFrame.model_validate(value)
    inspect_svg(final)
    return final


def wrap_scene(frame: NativeFrame) -> str:
    """Use exactly the same figure and anchored labels, fitted within a video page."""
    vp = frame.viewport
    svg = ET.Element("svg", {"xmlns": NS, "width": "1280", "height": "866",
                             "viewBox": "0 0 1280 866", "font-family": "Inter"})
    ET.SubElement(svg, "rect", {"width": "1280", "height": "866", "fill": "#ffffff"})
    inner = ET.SubElement(svg, "svg", {"x": "24", "y": "56", "width": "1232", "height": "610",
        "viewBox": f"{vp.x} {vp.y} {vp.width} {vp.height}", "preserveAspectRatio": "xMidYMid meet"})
    source = ET.fromstring('<svg xmlns="' + NS + '">' + frame.svg + '</svg>')
    inner.extend(source)
    for label in frame.labels:
        group = ET.SubElement(inner, "g")
        width = len(label.text) * 10.5 + 14
        ET.SubElement(group, "rect", {"x": str(label.x - width / 2), "y": str(label.y - 14),
            "width": str(width), "height": "28", "rx": "4", "fill": "white", "stroke": "#d3d8e1"})
        ET.SubElement(group, "text", {"x": str(label.x), "y": str(label.y + 6),
            "font-size": "18", "font-weight": "600", "text-anchor": "middle", "fill": "#202733"}).text = label.text
    return ET.tostring(svg, encoding="unicode")


def raster(frame: NativeFrame, spec: NativeLessonSpec) -> Image.Image:
    """Render the trusted scene with bundled typography and its exact narration cue."""
    png = resvg_py.svg_to_bytes(svg_string=wrap_scene(frame), width=1280, height=866,
        skip_system_fonts=True, font_files=[str(ROOT / "public/fonts/Inter.ttf")])
    image = Image.open(io.BytesIO(png)).convert("RGB")
    if image.size != (1280, 866):
        raise ValueError("Native rasterizer returned unexpected dimensions")
    draw = ImageDraw.Draw(image)
    draw.text((32, 14), spec.question, font=scene_font(26), fill="#202733")
    cue = next(cue for cue in spec.stages if cue.id == frame.cue_id)
    draw.rectangle((0, 682, 1280, 866), fill="#f1f4f8")
    draw.text((32, 696), cue.title, font=scene_font(22), fill="#344d96")
    font = scene_font(23)
    lines: list[str] = []
    for word in cue.narration.split():
        if not lines or draw.textlength(lines[-1] + " " + word, font=font) > 1216:
            lines.append(word)
        else:
            lines[-1] += " " + word
    if len(lines) > 4:
        raise ValueError("Native narration cannot fit its visible video caption; revise the cue")
    draw.multiline_text((32, 736), "\n".join(lines), font=font, fill="#202733", spacing=7)
    return image


def render_native(folder: Path) -> NativeProof:
    """Read prepared local data and encode frames from the exact trusted factory functions."""
    data = json.loads((folder / "source.json").read_text())
    spec = NativeLessonSpec.model_validate(data["spec"])
    registration = renderer_for(spec)
    verify_sources(registration)
    started = perf_counter()
    logger.info("native_render_started", extra={"task": "native-render", "route": registration.id,
                "lesson_id": spec.canonical, "fps": 24})
    audio = folder / "narration" / "narration.mp3"
    if abs(audio_duration(audio) - spec.stages[-1].end) > .15:
        raise ValueError("Native narration duration does not match its cue plan")
    narration = json.loads((audio.parent / "manifest.json").read_text())
    if narration["mp3_sha256"] != hashlib.sha256(audio.read_bytes()).hexdigest():
        raise ValueError("Native narration changed after its local synthesis receipt")
    plan_bytes = (folder / "narration-plan.json").read_bytes()
    plan = json.loads(plan_bytes)
    if (narration["plan_sha256"] != hashlib.sha256(plan_bytes).hexdigest()
            or plan["duration"] != spec.stages[-1].end
            or plan["cues"] != [{"start": cue.start, "end": cue.end, "still": cue.still,
                                  "text": cue.narration} for cue in spec.stages]):
        raise ValueError("Native narration receipt must bind the exact scene cue plan")
    output = folder / "lesson.mp4"
    if output.exists():
        raise ValueError("Native export preserves existing media; choose a new output folder")
    checkpoints = subprocess.run(["node", str(ROOT / "native/export.mjs"), "checkpoints", spec.canonical],
        cwd=ROOT, capture_output=True, text=True, check=True, timeout=60)
    fresh = json.loads(checkpoints.stdout)
    if canonical_digest(data["frames"]) != canonical_digest(fresh):
        raise ValueError("Prepared native checkpoints differ from the trusted factory; prepare again")
    frames = [materialize(RawFrame.model_validate(value)) for value in fresh]
    temporary = TemporaryDirectory(prefix="native-encode-", dir=folder)
    partial = Path(temporary.name) / "lesson.mp4"
    producer = subprocess.Popen(["node", str(ROOT / "native/export.mjs"), "frames", spec.canonical],
        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    command = [imageio_ffmpeg.get_ffmpeg_exe(), "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", "1280x866", "-r", "24", "-i", "pipe:0", "-i", str(audio), "-c:v", "libx264", "-preset", "veryfast",
        "-threads", "2", "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
        "-movflags", "+faststart", "-shortest", str(partial)]
    encoder = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    def expire() -> None:
        for child in (producer, encoder):
            if child.poll() is None:
                child.kill()
    deadline = Timer(600, expire)
    deadline.start()
    count = 0
    try:
        if producer.stdout is None or encoder.stdin is None:
            raise RuntimeError("Native frame pipeline did not start")
        for line in producer.stdout:
            frame = materialize(RawFrame.model_validate_json(line))
            if abs(frame.time - count / 24) > .001 or frame.controls != spec.default_controls:
                raise ValueError("Native frame stream does not match its declared clock and controls")
            encoder.stdin.write(raster(frame, spec).tobytes())
            count += 1
            if count % (24 * 8) == 0:
                logger.info("native_render_progress", extra={"task": "native-render", "route": registration.id,
                            "frames": count, "duration_ms": round((perf_counter() - started) * 1000)})
        producer.wait(timeout=30)
        if producer.returncode or count != math.ceil(spec.stages[-1].end * 24):
            raise ValueError("Native frame production failed or returned an incomplete story")
        encoder.stdin.close()
        encoder.wait(timeout=30)
        if encoder.returncode:
            raise ValueError("Native video encoding failed")
    finally:
        deadline.cancel()
        for process in (producer, encoder):
            if process.poll() is None:
                process.kill()
                process.wait(timeout=10)
        if encoder.stdin and not encoder.stdin.closed:
            encoder.stdin.close()
        if producer.stdout:
            producer.stdout.close()
    proof = NativeProof(schema_version="native-proof-1", renderer_id=spec.renderer.id,
        renderer_fingerprint=spec.renderer.fingerprint, spec_sha256=digest_spec(spec),
        video_sha256=hashlib.sha256(partial.read_bytes()).hexdigest(), video_duration=audio_duration(partial),
        fps=24, width=1280, height=866, frames=frames)
    verify_proof(spec, proof)
    from .native_publication import verify_video

    verify_video(partial, proof)
    partial.replace(output)
    temporary.cleanup()
    (folder / "proof.json").write_text(proof.model_dump_json(indent=2))
    (folder / "production.json").write_text(json.dumps({"spec_sha256": digest_spec(spec),
        "proof_sha256": canonical_digest(proof.model_dump(mode="json")), "frames": count,
        "video_sha256": proof.video_sha256, "api_cost_usd": 0, "authorship": "Locally authored trusted source revision"}))
    logger.info("native_render_completed", extra={"task": "native-render", "route": registration.id,
                "frames": count, "duration_ms": round((perf_counter() - started) * 1000)})
    return proof


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prepared_folder", type=Path)
    arguments = parser.parse_args()
    result = render_native(arguments.prepared_folder.resolve())
    sys.stdout.write(json.dumps({"spec_sha256": result.spec_sha256, "video_sha256": result.video_sha256,
                               "checkpoints": len(result.frames), "paid_api_calls": 0}) + "\n")
