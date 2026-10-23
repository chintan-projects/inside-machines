"""Check real encoded chapter boundaries against later frames of the same beat."""

import io
import subprocess
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[2]
MEDIA = ROOT / ".vercel/vacuum-lab/rendered"


def frame(path: Path, seconds: float) -> Image.Image:
    """Decode the actual encoded frame, not a renderer's pre-encode image."""
    result = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-ss",
            str(seconds),
            "-i",
            str(path),
            "-frames:v",
            "1",
            "-f",
            "image2pipe",
            "-vcodec",
            "png",
            "-",
        ],
        capture_output=True,
        check=True,
        timeout=20,
    )
    return Image.open(io.BytesIO(result.stdout)).convert("RGB")


def check() -> None:
    """A previous-shot title at an exact chapter seek is a cross-media regression."""
    for engine in ("manim", "motion-canvas", "remotion"):
        crop = (0, 625, 960, 715) if engine == "motion-canvas" else (0, 0, 960, 125)
        for boundary, reference in ((12, 18), (23, 28), (34, 40)):
            first = frame(MEDIA / f"{engine}-core.mp4", boundary).crop(crop)
            later = Image.open(MEDIA / f"{engine}-core-at-{reference}.png").convert("RGB").crop(crop)
            difference = float(sum(ImageStat.Stat(ImageChops.difference(first, later)).mean) / 3)
            if difference > 1.0:
                raise ValueError(f"{engine} chapter at {boundary}s displays the wrong shot: {difference:.3f}")


if __name__ == "__main__":
    check()
