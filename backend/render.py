"""Render the declarative lesson to images and narrated MP4 without generated code."""

import math
import re
import subprocess
import textwrap
from collections.abc import Callable
from pathlib import Path

import imageio_ffmpeg  # type: ignore[import-untyped]  # package ships no py.typed
from PIL import Image, ImageDraw, ImageFont

from .contracts import LessonSpec, Part
from .settings import ROOT, Settings


def stage_at(spec: LessonSpec, seconds: float) -> tuple[int, float]:
    """Return the active stage and its normalized progress."""
    elapsed = 0.0
    for i, stage in enumerate(spec.stages):
        if seconds < elapsed + stage.duration or i == len(spec.stages) - 1:
            return i, max(0, min(1, (seconds - elapsed) / stage.duration))
        elapsed += stage.duration
    return 0, 0


def part_pose(part: Part, stage: int, progress: float) -> tuple[float, float, float]:
    """Same bounded transform calculation used by the TypeScript scene player."""
    dx, dy, angle = 0.0, 0.0, 0.0
    for motion in part.motion:
        p = 1.0 if motion.stage < stage else progress if motion.stage == stage else 0.0
        if motion.kind == "rotate":
            angle += motion.amount * p
        if motion.kind == "translate":
            if motion.axis == "x":
                dx += motion.amount * p
            else:
                dy += motion.amount * p
    return dx, dy, angle


def transformed_point(
    x: float, y: float, cx: float, cy: float, dx: float, dy: float, radians: float
) -> tuple[float, float]:
    """Apply one part's transform without capturing mutable loop variables."""
    return (
        cx + dx + (x - cx) * math.cos(radians) - (y - cy) * math.sin(radians),
        cy + dy + (x - cx) * math.sin(radians) + (y - cy) * math.cos(radians),
    )


def draw_scene(spec: LessonSpec, seconds: float, *, width: int = 900, height: int = 540) -> Image.Image:
    """Draw the shared safe scene contract, preserving aspect ratio and label positions."""
    image = Image.new("RGB", (900, 540), "#f3f6f7")
    draw = ImageDraw.Draw(image)
    if spec.canonical != "air-conditioner-craft":
        draw.ellipse((155, 435, 765, 505), fill="#e3e9eb")
    stage, progress = stage_at(spec, seconds)
    active = set(spec.stages[stage].parts)
    for part in sorted(spec.parts, key=lambda p: p.layer):
        dx, dy, angle = part_pose(part, stage, progress)
        cx, cy = part.x + part.w / 2, part.y + part.h / 2
        radians = math.radians(angle)

        def point(
            x: float,
            y: float,
            cx: float = cx,
            cy: float = cy,
            dx: float = dx,
            dy: float = dy,
            radians: float = radians,
        ) -> tuple[float, float]:
            return transformed_point(x, y, cx, cy, dx, dy, radians)

        color = part.color
        if part.shape == "box":
            points = [
                point(part.x, part.y),
                point(part.x + part.w, part.y),
                point(part.x + part.w, part.y + part.h),
                point(part.x, part.y + part.h),
            ]
            draw.polygon(points, fill=color, outline=part.stroke, width=2)
        elif part.shape in ("ellipse", "ring"):
            # Round machine parts are drawn in their own transparent layer before rotation.
            layer = Image.new("RGBA", (900, 540), (0, 0, 0, 0))
            ld = ImageDraw.Draw(layer)
            box = (part.x + dx, part.y + dy, part.x + part.w + dx, part.y + part.h + dy)
            ld.ellipse(
                box,
                fill=color if part.shape == "ellipse" else None,
                outline=part.stroke,
                width=5 if part.shape == "ring" else 2,
            )
            if angle:
                layer = layer.rotate(-angle, center=(cx + dx, cy + dy), resample=Image.Resampling.BICUBIC)
            image.paste(layer, (0, 0), layer)
            draw = ImageDraw.Draw(image)
        elif part.shape in ("path", "polygon"):
            pts = [point(p[0], p[1]) for p in part.points]
            if part.shape == "polygon":
                draw.polygon(pts, fill=color, outline=part.stroke, width=2)
            else:
                heat = part.id in ("absorbed-heat", "released-heat")
                if heat:
                    for a, b in zip(pts[:-1], pts[1:], strict=True):
                        distance = math.hypot(b[0] - a[0], b[1] - a[1])
                        if distance:
                            for offset in range(0, math.ceil(distance), 11):
                                t0, t1 = offset / distance, min(1, (offset + 4) / distance)
                                draw.line(
                                    [
                                        (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0),
                                        (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1),
                                    ],
                                    fill=part.stroke,
                                    width=max(2, round(part.w)),
                                )
                else:
                    draw.line(pts, fill=part.stroke, width=max(2, round(part.w)), joint="curve")
                if any(m.kind == "flow" and m.stage == stage for m in part.motion):
                    a, b = pts[-2:]
                    distance = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
                    ux, uy = (b[0] - a[0]) / distance, (b[1] - a[1]) / distance
                    draw.polygon(
                        [
                            b,
                            (b[0] - ux * 12 - uy * 6, b[1] - uy * 12 + ux * 6),
                            (b[0] - ux * 12 + uy * 6, b[1] - uy * 12 - ux * 6),
                        ],
                        fill=part.stroke,
                    )
                if (
                    not heat
                    and part.id in active
                    and any(m.kind == "flow" and m.stage == stage for m in part.motion)
                ):
                    for a, b in zip(pts[:-1], pts[1:], strict=True):
                        length = math.hypot(b[0] - a[0], b[1] - a[1])
                        if length < 40:
                            continue
                        count = 2 if length > 130 else 1
                        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
                        for j in range(count):
                            t = 0.12 + 0.76 * ((j / count + progress * 0.8) % 1)
                            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                            draw.line(
                                [
                                    (x - ux * 7 - uy * 5, y - uy * 7 + ux * 5),
                                    (x, y),
                                    (x - ux * 7 + uy * 5, y - uy * 7 - ux * 5),
                                ],
                                fill="white",
                                width=2,
                            )
        elif part.shape == "text":
            font = scene_font(max(12, int(part.h)))
            core_label = part.id.startswith("label-")
            if core_label:
                font.set_variation_by_name("SemiBold")  # type: ignore[no-untyped-call]  # Pillow omits this method's annotation.
            emphasized = core_label and part.id[6:] in active
            x, y = part.x + dx, part.y + dy
            if core_label:
                extent = draw.textlength(part.label, font=font)
                draw.rounded_rectangle(
                    (x - 8, y - 6, x + extent + 8, y + part.h + 8),
                    radius=5,
                    fill="white",
                    outline=spec.accent if emphasized else "#d6e1e5",
                    width=2 if emphasized else 1,
                )
            draw.text(
                (x, y), part.label, fill=spec.accent if emphasized else part.color, font=font, anchor="lt"
            )
        if (
            spec.canonical != "air-conditioner-craft"
            and part.id in active
            and part.shape not in ("path", "text")
        ):
            x, y = point(part.x + part.w, part.y)
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=spec.accent, outline="white", width=2)
    if (width, height) == (900, 540):
        return image
    scale = min(width / 900, height / 540)
    fitted = image.resize((round(900 * scale), round(540 * scale)), Image.Resampling.LANCZOS)
    output = Image.new("RGB", (width, height), "#f3f6f7")
    output.paste(fitted, ((width - fitted.width) // 2, (height - fitted.height) // 2))
    return output


def scene_font(size: int) -> ImageFont.FreeTypeFont:
    """Use the same bundled, licensed typeface for raster and SVG lettering."""
    return ImageFont.truetype(str(ROOT / "public" / "fonts" / "Inter.ttf"), size=size)


def audio_duration(path: Path) -> float:
    """Probe with the encoder we ship, avoiding a separate ffprobe dependency."""
    result = subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(path)],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    match = re.search(r"Duration: (\d+):(\d+):([\d.]+)", result.stderr)
    if not match:
        raise ValueError("Narration could not be decoded")
    return int(match[1]) * 3600 + int(match[2]) * 60 + float(match[3])


def render_video(
    spec: LessonSpec, audio: list[Path], folder: Path, settings: Settings, heartbeat: Callable[[], None]
) -> Path:
    """Encode a bounded MP4 with scene, readable captions, and synchronized narration."""
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    output = folder / "lesson.mp4"
    total = sum(s.duration for s in spec.stages)
    if total > 180 or len(audio) != len(spec.stages):
        raise ValueError("Video is outside the alpha duration or narration bounds")
    segments = []
    for i, (source, stage) in enumerate(zip(audio, spec.stages, strict=True)):
        dest = folder / f"segment-{i}.wav"
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-loglevel",
                "error",
                "-i",
                str(source),
                "-af",
                "apad",
                "-t",
                str(stage.duration),
                "-ar",
                "44100",
                "-ac",
                "1",
                str(dest),
            ],
            check=True,
            capture_output=True,
            timeout=25,
        )
        segments.append(dest)
    manifest = folder / "audio.txt"
    manifest.write_text("\n".join("file '" + p.name + "'" for p in segments))
    combined = folder / "narration.wav"
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(manifest),
            "-c",
            "copy",
            str(combined),
        ],
        cwd=folder,
        check=True,
        capture_output=True,
        timeout=25,
    )
    command = [
        ffmpeg,
        "-y",
        "-loglevel",
        "error",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{settings.video_width}x{settings.video_height}",
        "-r",
        str(settings.video_fps),
        "-i",
        "pipe:0",
        "-i",
        str(combined),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-threads",
        "2",
        "-crf",
        "24",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "96k",
        "-movflags",
        "+faststart",
        "-shortest",
        str(output),
    ]
    process = subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
    )
    try:
        if process.stdin is None:
            raise RuntimeError("Video encoder input not available")
        title_font = scene_font(21)
        caption_font = scene_font(22)
        static_frames: dict[tuple[int, float], Image.Image] = {}
        for frame in range(math.ceil(total * settings.video_fps)):
            seconds = frame / settings.video_fps
            if spec.version == 2:
                from .teaching_state import teaching_at
                from .teaching_svg import teaching_image

                beat, progress = teaching_at(spec, seconds)
                key = (beat.stage, progress)
                if progress in (0.0, 1.0) and key in static_frames:
                    canvas = static_frames[key]
                else:
                    canvas = teaching_image(spec, seconds, settings.video_width, settings.video_height)
                    if progress in (0.0, 1.0):
                        static_frames[key] = canvas
            else:
                index, _ = stage_at(spec, seconds)
                canvas = Image.new("RGB", (settings.video_width, settings.video_height), "#f3f6f7")
                scene = draw_scene(
                    spec, seconds, width=settings.video_width, height=settings.video_height - 105
                )
                canvas.paste(scene, (0, 24))
                draw = ImageDraw.Draw(canvas)
                draw.text((24, 8), spec.title, fill="#17232d", font=title_font)
                draw.rectangle(
                    (0, settings.video_height - 82, settings.video_width, settings.video_height),
                    fill="#172f37",
                )
                draw.multiline_text(
                    (24, settings.video_height - 68),
                    "\n".join(textwrap.wrap(spec.stages[index].title, width=85)[:2]),
                    fill="white",
                    font=caption_font,
                    spacing=6,
                )
                draw.text(
                    (24, settings.video_height - 26),
                    f"Chapter {index + 1} of {len(spec.stages)} · generic teaching model · schematic motion",
                    fill="#b8d2d4",
                    font=ImageFont.load_default(size=12),
                )
            process.stdin.write(canvas.tobytes())
            if frame % (settings.video_fps * 8) == 0:
                heartbeat()
        process.stdin.close()
        process.wait(timeout=30)
        if process.returncode:
            raise RuntimeError("Video encoding failed")
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        if process.stderr:
            process.stderr.close()
    return output
