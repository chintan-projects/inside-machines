"""Render, prepare and selectively publish the immutable authored AC benchmark."""

import argparse
import asyncio
import hashlib
import subprocess
import time
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

import imageio_ffmpeg  # type: ignore[import-untyped]  # Wheel ships no typing marker.
from _shared.services.logger import get_logger
from pydantic import BaseModel

from .ac_craft import CANONICAL, aircon_craft
from .assets import Assets
from .contracts import LessonSpec
from .quality import require_learning_quality
from .render import audio_duration, render_video
from .settings import ROOT, Settings, load_settings
from .starters import digest_spec
from .store import Database, Store

logger = get_logger(__name__)
MANIFEST = ROOT / ".vercel" / "craft-manifest.json"


class CraftArtifact(BaseModel):
    """Private deployment manifest is checked again before catalog publication."""

    spec: LessonSpec
    spec_sha256: str
    video: str
    video_sha256: str
    narration: str = "macOS computer speech"


def validate_artifact(artifact: CraftArtifact) -> None:
    """Bind publication to the known authored revision and complete learning contract."""
    if artifact.spec.canonical != CANONICAL or digest_spec(artifact.spec) != artifact.spec_sha256:
        raise ValueError("Unexpected or altered authored lesson")
    expected = aircon_craft()
    # Measured narration adjusts duration only; all teaching text and geometry must match.
    for actual, chapter in zip(artifact.spec.stages, expected.stages, strict=True):
        chapter.duration = actual.duration
    if digest_spec(expected) != artifact.spec_sha256:
        raise ValueError("Manifest does not match the authored source")
    require_learning_quality(artifact.spec)


def import_craft(target: Store, artifact: CraftArtifact) -> bool:
    """Add a new immutable lesson, preserving old content and all private records."""
    validate_artifact(artifact)

    def publish(db: Database) -> bool:
        existing = db.lessons.get(CANONICAL)
        if existing:
            if (
                existing.get("spec_sha256") != artifact.spec_sha256
                or existing.get("video_sha256") != artifact.video_sha256
            ):
                raise ValueError("Published lessons are immutable; author a new revision ID")
            return False
        db.lessons[CANONICAL] = {
            "id": CANONICAL,
            "spec": artifact.spec.model_dump(mode="json"),
            "video": artifact.video,
            "audio": [],
            "quality": "authored-craft",
            "created_at": time.time(),
            "views": 0,
            "cost_usd": 0,
            "spec_sha256": artifact.spec_sha256,
            "video_sha256": artifact.video_sha256,
            "narration": artifact.narration,
        }
        # Hide the superseded teaching draft from new discovery. Its URL, chats,
        # feedback and offline snapshots remain intact; nothing is deleted.
        if old := db.lessons.get("air-conditioner"):
            old["archived"] = True
            old["superseded_by"] = CANONICAL
        return True

    return target.transaction(publish)


async def render_local(settings: Settings) -> None:
    """Use local speech for the authored iteration, with no paid provider calls."""
    local = replace(
        settings, database_url="", blob_token="", production=False, video_width=1280, video_height=900
    )
    spec = aircon_craft()
    require_learning_quality(spec)
    with TemporaryDirectory(prefix="inside-craft-") as temp:
        folder = Path(temp)
        audio: list[Path] = []
        for index, chapter in enumerate(spec.stages):
            source, mp3 = folder / f"{index}.aiff", folder / f"{index}.mp3"
            subprocess.run(
                ["/usr/bin/say", "-r", "150", "-o", str(source), chapter.narration],
                check=True,
                capture_output=True,
                timeout=60,
            )
            subprocess.run(
                [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(source), str(mp3)],
                check=True,
                capture_output=True,
                timeout=30,
            )
            chapter.duration = audio_duration(mp3) + 0.7
            audio.append(mp3)
        spec = LessonSpec.model_validate(spec.model_dump())
        video = await asyncio.to_thread(render_video, spec, audio, folder, local, lambda: None)
        data = video.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        location = await Assets(local).put(f"craft/{CANONICAL}/{digest}.mp4", data, "video/mp4")
    artifact = CraftArtifact(spec=spec, spec_sha256=digest_spec(spec), video=location, video_sha256=digest)
    # Local-only developer preview can be iterated before its first cloud publication.
    store = Store("", local.data_dir)
    store.transaction(lambda db: db.lessons.pop(CANONICAL, None))
    import_craft(store, artifact)
    logger.info(
        "Authored benchmark rendered locally",
        lesson=CANONICAL,
        seconds=sum(s.duration for s in spec.stages),
        bytes=len(data),
    )


async def main() -> None:
    """Run explicitly selected local rendering, remote preparation or import."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("render", "prepare", "import"))
    action = parser.parse_args().action
    settings = load_settings()
    if action == "render":
        if settings.production or settings.database_url:
            raise ValueError("Render into local review storage only")
        await render_local(settings)
        return
    if action == "prepare":
        if not settings.blob_token:
            raise ValueError("Private Blob storage is required for preparation")
        record = Store("", settings.data_dir).snapshot().lessons[CANONICAL]
        spec = LessonSpec.model_validate(record["spec"])
        data = await Assets(replace(settings, blob_token="", production=False)).read(str(record["video"]))
        digest = hashlib.sha256(data).hexdigest()
        location = await Assets(settings).put(f"craft/{CANONICAL}/{digest}.mp4", data, "video/mp4")
        if hashlib.sha256(await Assets(settings).read(location)).hexdigest() != digest:
            raise ValueError("Remote video integrity check failed")
        artifact = CraftArtifact(
            spec=spec, spec_sha256=digest_spec(spec), video=location, video_sha256=digest
        )
        validate_artifact(artifact)
        MANIFEST.write_text(artifact.model_dump_json(indent=2))
        MANIFEST.chmod(0o600)
        logger.info("Authored benchmark prepared", lesson=CANONICAL)
        return
    if not settings.database_url:
        raise ValueError("Explicit destination DATABASE_URL required for cloud import")
    artifact = CraftArtifact.model_validate_json(MANIFEST.read_text())
    if not artifact.video.startswith("https://"):
        raise ValueError("Cloud publication requires a private remote artifact")
    data = await Assets(settings).read(artifact.video)
    if hashlib.sha256(data).hexdigest() != artifact.video_sha256:
        raise ValueError("Remote video integrity check failed")
    inserted = import_craft(Store(settings.database_url, settings.data_dir), artifact)
    logger.info("Authored benchmark imported", lesson=CANONICAL, inserted=inserted)


if __name__ == "__main__":
    asyncio.run(main())
