"""Safe vector rendering used by CE video, checkpoint exports and parity tests."""

import io
from html import escape

import resvg_py
from PIL import Image, ImageOps

from .contracts import LessonSpec, Part
from .renderer_assets import ac_renderer_fingerprint, authored_context
from .section_assets import section_asset
from .settings import ROOT
from .teaching_contracts import Change
from .teaching_state import sampled_pose, scenario_for, teaching_at


def graphic_svg(part: Part, change: Change | None, progress: float) -> str:
    """Draw a validated primitive; external resources/markup are never accepted."""
    pose = sampled_pose(change, progress, part.color)
    x, y, w, h = part.x, part.y, part.w, part.h
    fill = pose.fill or part.color
    style = f'fill="{fill}" stroke="{part.stroke}" stroke-width="2"'
    if part.shape == "box":
        shape = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" {style}/>'
    elif part.shape in ("ellipse", "ring"):
        style = f'fill="none" stroke="{part.stroke}" stroke-width="5"' if part.shape == "ring" else style
        shape = f'<ellipse cx="{x + w / 2}" cy="{y + h / 2}" rx="{w / 2}" ry="{h / 2}" {style}/>'
    elif part.shape == "text":
        shape = f'<text x="{x}" y="{y}" dominant-baseline="hanging" font-size="{h}" font-weight="550" fill="{fill}">{escape(part.label)}</text>'
    else:
        points = " ".join(f"{p[0]},{p[1]}" for p in part.points)
        shape = (
            f'<polygon points="{points}" {style}/>'
            if part.shape == "polygon"
            else f'<polyline points="{points}" fill="none" stroke="{part.stroke}" stroke-width="{max(2, w)}" stroke-linecap="round" stroke-linejoin="round"/>'
        )
    cx, cy = x + w / 2, y + h / 2
    transform = f"translate({pose.x} {pose.y}) translate({cx} {cy}) rotate({pose.angle}) scale({pose.sx} {pose.sy}) translate({-cx} {-cy})"
    return f'<g data-graphic="{part.id}" transform="{transform}" opacity="{pose.opacity}">{shape}</g>'


def graphic_scene(spec: LessonSpec, seconds: float, scenario_id: str | None = None) -> str:
    """Return the exact graph/state used by the interactive teaching inset."""
    beat, progress = teaching_at(spec, seconds)
    scenario = scenario_for(spec, beat, scenario_id)
    changes = {c.target: c for c in beat.changes}
    if scenario:
        changes.update({c.target: c for c in scenario.changes})
    art, replaced = (
        section_asset(spec, beat.stage)
        if spec.teaching and spec.teaching.renderer == "authored-sections-v1"
        else ("", set())
    )
    return art + "".join(
        graphic_svg(p, changes.get(p.id), progress)
        for p in sorted(spec.graphics, key=lambda p: p.layer)
        if p.id in beat.graphics and p.id not in replaced
    )


def wrapped_lines(text: str, x: int, y: int, width: int = 60, size: int = 24) -> str:
    """Wrap plain text independently of provider punctuation or markup."""
    import textwrap

    return "".join(
        f'<text x="{x}" y="{y + i * (size + 8)}" font-size="{size}">{escape(line)}</text>'
        for i, line in enumerate(textwrap.wrap(text, width=width))
    )


def teaching_svg(spec: LessonSpec, seconds: float, scenario_id: str | None = None) -> str:
    """Compose shared context, causal graphic, state and authored words for export."""
    teaching = spec.teaching
    if teaching is None:
        raise ValueError("CE export requires teaching data")
    if teaching.renderer == "authored-sections-v1":
        return focused_svg(spec, seconds, scenario_id)
    if spec.canonical.endswith("-studio-1"):
        # New revision family adopts a full-size working mechanism. Historical
        # paired exports retain their bytes and original layout.
        return focused_svg(spec, seconds, scenario_id, declarative=True)
    beat, progress = teaching_at(spec, seconds)
    scenario = scenario_for(spec, beat, scenario_id)
    stage = spec.stages[beat.stage]
    if teaching.renderer == "ac-cutaway-v2":
        if teaching.renderer_fingerprint != ac_renderer_fingerprint():
            raise ValueError("This lesson uses an earlier immutable cutaway; keep its video")
        context = authored_context(scenario.context if scenario and scenario.context != "none" else "outside")
        context = context.replace("<svg ", '<svg x="10" y="125" width="470" height="310" ', 1)
    else:
        context = (
            '<svg x="10" y="125" width="470" height="310" viewBox="0 0 900 540">'
            + "".join(graphic_svg(p, None, 1) for p in sorted(spec.parts, key=lambda p: p.layer))
            + "</svg>"
        )
    graphic = (
        '<svg x="480" y="130" width="460" height="300" viewBox="0 0 900 540">'
        + graphic_scene(spec, seconds, scenario_id)
        + "</svg>"
    )
    state = " • ".join(
        f"{p.name}: {p.before if progress < 0.01 else p.after if progress > 0.99 else p.before + ' → ' + p.after}"
        for p in beat.properties
    )
    body = wrapped_lines(stage.title, 28, 62, 65, 29) + wrapped_lines(beat.bridge, 28, 101, 95, 17)
    body += context + graphic + wrapped_lines(beat.static_explanation, 28, 466, 99, 19)
    body += wrapped_lines(state, 28, 534, 105, 16)
    if scenario:
        body += wrapped_lines(f"{scenario.label}: {scenario.outcome}", 28, 590, 100, 18)
    if (beat.stage == 0 and progress < 0.15) or (beat.stage == len(spec.stages) - 1 and progress > 0.9):
        question = teaching.prediction.prompt if beat.stage == 0 else teaching.transfer.prompt
        body += '<rect x="475" y="132" width="470" height="300" rx="12" fill="#f3f2ee"/>'
        body += wrapped_lines(question, 500, 190, 32, 20)
        body += '<text x="500" y="410" font-size="16">Pause and predict. Test it in the lesson.</text>'
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 650" font-family="Inter" fill="#29383d"><rect width="960" height="650" fill="#f3f2ee"/>'
        + body
        + "</svg>"
    )


def focused_svg(spec: LessonSpec, seconds: float, scenario_id: str | None = None, *, declarative: bool = False) -> str:
    """Versioned detail-first composition; historical paired exports stay unchanged."""
    teaching = spec.teaching
    if teaching is None:
        raise ValueError("CE export requires teaching data")
    beat, progress = teaching_at(spec, seconds)
    scenario = scenario_for(spec, beat, scenario_id)
    body = wrapped_lines(spec.stages[beat.stage].title, 40, 55, 62, 30)
    body += wrapped_lines(beat.bridge, 40, 93, 100, 16)
    body += '<rect x="40" y="119" width="880" height="405" rx="14" fill="#f6f9fc"/>'
    body += '<svg x="135" y="119" width="690" height="414" viewBox="0 0 900 540">'
    whole = not declarative and beat.stage == len(teaching.beats) - 1 and progress > 0.5 and scenario_id is None
    art = section_asset(spec, -1)[0] if whole else graphic_scene(spec, seconds, scenario_id)
    body += art + "</svg>"
    body += wrapped_lines(teaching.operation_note if whole else beat.static_explanation, 40, 557, 92, 17)
    kind = "Qualitative teaching model" if declarative else "Qualitative cutaway"
    body += wrapped_lines(f"Step {beat.stage + 1} of {len(teaching.beats)} · {kind}", 40, 625, 100, 13)
    if scenario:
        body += wrapped_lines(scenario.outcome, 470, 625, 55, 13)
    if scenario_id is None and (
        (beat.stage == 0 and progress < 0.15) or (beat.stage == len(teaching.beats) - 1 and progress > 0.9)
    ):
        task = teaching.prediction if beat.stage == 0 else teaching.transfer
        body += '<rect x="140" y="159" width="680" height="324" rx="14" fill="#ffffff" stroke="#b8cbe4"/>'
        body += wrapped_lines(task.prompt, 180, 228, 48, 24)
        body += (
            '<text x="180" y="443" font-size="16">Pause and predict. Explore the change in the lesson.</text>'
        )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 650" font-family="Inter" fill="#263b55"><rect width="960" height="650" fill="#ffffff"/>'
        + body
        + "</svg>"
    )


def teaching_image(spec: LessonSpec, seconds: float, width: int, height: int) -> Image.Image:
    """Rasterize safe vector geometry at output resolution with the bundled font."""
    data = resvg_py.svg_to_bytes(
        svg_string=teaching_svg(spec, seconds),
        width=width,
        height=height,
        skip_system_fonts=True,
        font_files=[str(ROOT / "public/fonts/Inter.ttf")],
        background="#f3f2ee",
    )
    image = Image.open(io.BytesIO(data)).convert("RGB")
    # resvg preserves source aspect ratio and may prioritize width over height.
    # Raw ffmpeg input MUST contain exactly width*height*3 bytes for every frame.
    fitted = ImageOps.contain(image, (width, height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (width, height), "#f3f2ee")
    canvas.paste(fitted, ((width - fitted.width) // 2, (height - fitted.height) // 2))
    return canvas
