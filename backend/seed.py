"""Create original starter lessons with local computer speech, without paid AI calls."""

import asyncio
import subprocess
import time
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

import imageio_ffmpeg  # type: ignore[import-untyped]  # Upstream wheel has no type marker.
from _shared.services.logger import get_logger

from .assets import Assets
from .render import audio_duration, render_video
from .seed_aircon import aircon
from .seed_cooker import cooker
from .seed_washer import washer
from .settings import load_settings
from .store import Database, Store

logger = get_logger(__name__)


async def seed() -> None:
    """Seed a local database; production seeding is an explicit separate operation."""
    original = load_settings()
    if original.production or original.database_url:
        raise RuntimeError("This starter renderer is local-only; production import must be explicit")
    settings = replace(original, blob_token="")
    store, assets = Store("", settings.data_dir), Assets(settings)
    for spec in (washer(), cooker(), aircon()):
        if spec.canonical in store.snapshot().lessons:
            logger.info("Starter already exists", lesson=spec.canonical)
            continue
        with TemporaryDirectory(prefix="inside-starter-") as tmp:
            folder = Path(tmp)
            audio = []
            for index, stage in enumerate(spec.stages):
                source, mp3 = folder / f"voice-{index}.aiff", folder / f"voice-{index}.mp3"
                subprocess.run(
                    ["/usr/bin/say", "-r", "155", "-o", str(source), stage.narration],
                    check=True,
                    timeout=60,
                    capture_output=True,
                )
                subprocess.run(
                    [
                        imageio_ffmpeg.get_ffmpeg_exe(),
                        "-y",
                        "-loglevel",
                        "error",
                        "-i",
                        str(source),
                        str(mp3),
                    ],
                    check=True,
                    timeout=30,
                    capture_output=True,
                )
                stage.duration = min(25, max(5, audio_duration(mp3) + 0.6))
                audio.append(mp3)
            spec = type(spec).model_validate(spec.model_dump())
            video = await asyncio.to_thread(render_video, spec, audio, folder, settings, lambda: None)
            location = await assets.put(
                f"lessons/{spec.canonical}/lesson.mp4", video.read_bytes(), "video/mp4"
            )

            lesson_data: dict[str, object] = spec.model_dump(mode="json")

            def publish(
                db: Database,
                lesson_id: str = spec.canonical,
                data: dict[str, object] = lesson_data,
                video_path: str = location,
            ) -> None:
                db.lessons.setdefault(
                    lesson_id,
                    {
                        "id": lesson_id,
                        "spec": data,
                        "video": video_path,
                        "audio": [],
                        "created_at": time.time(),
                        "quality": "authored-starter",
                        "views": 0,
                        "cost_usd": 0,
                    },
                )

            store.transaction(publish)
            logger.info(
                "Starter lesson rendered",
                lesson=spec.canonical,
                duration_seconds=round(sum(stage.duration for stage in spec.stages)),
            )


if __name__ == "__main__":
    asyncio.run(seed())
