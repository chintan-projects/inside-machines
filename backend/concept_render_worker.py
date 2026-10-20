"""Picklable local media worker; never owns storage, publication or paid calls."""

import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import imageio_ffmpeg  # type: ignore[import-untyped]  # Upstream has no typing marker.

from .contracts import LessonSpec
from .quality import require_learning_quality
from .render import audio_duration, render_video
from .settings import Settings


def render_concept_media(source: LessonSpec, local: Settings) -> tuple[LessonSpec, bytes]:
    """Produce the unchanged local speech/video format in an isolated process."""
    if local.production or local.database_url or local.blob_token:
        raise ValueError("A concept media worker requires isolated local settings")
    spec = source.model_copy(deep=True)
    require_learning_quality(spec)
    with TemporaryDirectory(prefix="inside-ce-") as temporary:
        folder = Path(temporary)
        audio: list[Path] = []
        for index, stage in enumerate(spec.stages):
            speech, target = folder / f"{index}.aiff", folder / f"{index}.mp3"
            subprocess.run(
                ["/usr/bin/say", "-r", "150", "-o", str(speech), stage.narration],
                check=True, capture_output=True, timeout=60,
            )
            subprocess.run(
                [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(speech), str(target)],
                check=True, capture_output=True, timeout=30,
            )
            stage.duration = max(5, audio_duration(target) + 0.7)
            audio.append(target)
        spec = LessonSpec.model_validate(spec.model_dump())
        require_learning_quality(spec)
        video = render_video(spec, audio, folder, local, lambda: None)
        return spec, video.read_bytes()
