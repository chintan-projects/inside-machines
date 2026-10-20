"""Prepare, verify and import immutable CE revisions without replacing private history."""

import argparse
import asyncio
import hashlib
import json
import subprocess
import time
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

import imageio_ffmpeg  # type: ignore[import-untyped]  # Upstream has no typing marker.
from _shared.services.logger import get_logger
from pydantic import BaseModel, ValidationError

from .ac_concept import aircon_concept
from .assets import Assets
from .contracts import LessonSpec
from .quality import require_learning_quality
from .render import audio_duration, render_video
from .settings import ROOT, Settings, load_settings
from .starters import digest_spec
from .store import Database, Store

logger = get_logger(__name__)
MANIFEST = ROOT / ".vercel/concept-manifest.json"


class ConceptArtifact(BaseModel):
    """Bind private media bytes to the exact authored lesson and storyboard."""

    spec: LessonSpec
    spec_sha256: str
    video: str
    video_sha256: str
    replaces: list[str]
    narration: str = "macOS computer speech"


def authored_lessons() -> list[tuple[LessonSpec, list[str]]]:
    """Trusted startup composition for reviewed-in-source authoring candidates."""
    from .cooker_concept import cooker_concept
    from .washer_concept import washer_concept

    return [
        (aircon_concept(), ["air-conditioner", "air-conditioner-craft"]),
        (washer_concept(), ["washing-machine"]),
        (cooker_concept(), ["pressure-cooker"]),
    ]


def validate_concept(artifact: ConceptArtifact) -> None:
    """Only the authored source may be published under its reserved revision ID."""
    expected = next((s for s, _ in authored_lessons() if s.canonical == artifact.spec.canonical), None)
    replacements = next(
        (old for s, old in authored_lessons() if s.canonical == artifact.spec.canonical), None
    )
    if expected is None or replacements != artifact.replaces:
        raise ValueError("Unknown authored revision or replacement set")
    if len(expected.stages) != len(artifact.spec.stages):
        raise ValueError("Authored storyboard changed")
    for actual, stage in zip(artifact.spec.stages, expected.stages, strict=True):
        stage.duration = actual.duration
    if digest_spec(expected) != artifact.spec_sha256 or digest_spec(artifact.spec) != artifact.spec_sha256:
        raise ValueError("Manifest does not match authored source")
    require_learning_quality(artifact.spec)


def import_concepts(store: Store, artifacts: list[ConceptArtifact]) -> tuple[int, int]:
    """Publish new identities atomically; prior specs, chats, feedback and ledger survive."""
    if len({a.spec.canonical for a in artifacts}) != len(artifacts):
        raise ValueError("Duplicate revision identities")
    for artifact in artifacts:
        validate_concept(artifact)

    def publish(db: Database) -> tuple[int, int]:
        inserted, existing = 0, 0
        for a in artifacts:
            id = a.spec.canonical
            old = db.lessons.get(id)
            if old:
                if old.get("spec_sha256") != a.spec_sha256 or old.get("video_sha256") != a.video_sha256:
                    raise ValueError("Published revisions are immutable; use a new revision ID")
                existing += 1
                continue
            db.lessons[id] = {
                "id": id,
                "spec": a.spec.model_dump(mode="json"),
                "video": a.video,
                "audio": [],
                "quality": "authored-concept-draft",
                "created_at": time.time(),
                "views": 0,
                "cost_usd": 0,
                "spec_sha256": a.spec_sha256,
                "video_sha256": a.video_sha256,
                "narration": a.narration,
                "storyboard_version": "ce-1",
            }
            for previous in a.replaces:
                if previous in db.lessons:
                    db.lessons[previous]["archived"] = True
                    db.lessons[previous]["superseded_by"] = id
            inserted += 1
        return inserted, existing

    return store.transaction(publish)


async def render_concepts(settings: Settings) -> None:
    """Local deterministic authoring uses computer speech, not a paid provider."""
    local = replace(
        settings,
        database_url="",
        blob_token="",
        production=False,
        video_width=1280,
        video_height=866,
        video_fps=8,
    )
    artifacts: list[ConceptArtifact] = []
    cached: dict[str, ConceptArtifact] = {}
    if MANIFEST.exists():
        for candidate in json.loads(MANIFEST.read_text()):
            try:
                previous = ConceptArtifact.model_validate(candidate)
                validate_concept(previous)
                if previous.video.startswith("https://"):
                    continue
                data = await Assets(local).read(previous.video)
                if hashlib.sha256(data).hexdigest() == previous.video_sha256:
                    cached[previous.spec.canonical] = previous
            except (ValueError, ValidationError, OSError):
                # Changed source or a different local asset directory needs a new render.
                continue
    for spec, replaces in authored_lessons():
        require_learning_quality(spec)
        if spec.canonical in cached:
            artifacts.append(cached[spec.canonical])
            logger.info("Verified concept render reused", lesson=spec.canonical)
            continue
        with TemporaryDirectory(prefix="inside-ce-") as temporary:
            folder = Path(temporary)
            audio: list[Path] = []
            for index, stage in enumerate(spec.stages):
                source, target = folder / f"{index}.aiff", folder / f"{index}.mp3"
                subprocess.run(
                    ["/usr/bin/say", "-r", "150", "-o", str(source), stage.narration],
                    check=True,
                    capture_output=True,
                    timeout=60,
                )
                subprocess.run(
                    [
                        imageio_ffmpeg.get_ffmpeg_exe(),
                        "-y",
                        "-loglevel",
                        "error",
                        "-i",
                        str(source),
                        str(target),
                    ],
                    check=True,
                    capture_output=True,
                    timeout=30,
                )
                stage.duration = max(5, audio_duration(target) + 0.7)
                audio.append(target)
            spec = LessonSpec.model_validate(spec.model_dump())
            video = await asyncio.to_thread(render_video, spec, audio, folder, local, lambda: None)
            data = video.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            location = await Assets(local).put(f"concepts/{spec.canonical}/{digest}.mp4", data, "video/mp4")
        artifacts.append(
            ConceptArtifact(
                spec=spec,
                spec_sha256=digest_spec(spec),
                video=location,
                video_sha256=digest,
                replaces=replaces,
            )
        )
        logger.info(
            "Concept lesson rendered",
            lesson=spec.canonical,
            duration=round(sum(s.duration for s in spec.stages)),
            bytes=len(data),
        )
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps([a.model_dump(mode="json") for a in artifacts], indent=2))
    import_concepts(Store("", local.data_dir), artifacts)


async def main() -> None:
    """Separate rendering, verified private asset upload and atomic publication."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("render", "prepare", "import"))
    args = parser.parse_args()
    settings = load_settings()
    if args.action == "render":
        await render_concepts(settings)
        return
    artifacts = [ConceptArtifact.model_validate(a) for a in json.loads(MANIFEST.read_text())]
    local_assets = Assets(replace(settings, database_url="", blob_token="", production=False))
    remote_assets = Assets(settings)
    # Verify every referenced byte before either uploading or mutating the database.
    for artifact in artifacts:
        validate_concept(artifact)
        data = await (local_assets if args.action == "prepare" else remote_assets).read(artifact.video)
        if hashlib.sha256(data).hexdigest() != artifact.video_sha256:
            raise ValueError("Video digest mismatch")
        if args.action == "prepare":
            if not settings.blob_token:
                raise ValueError("Private asset storage is required for preparation")
            artifact.video = await remote_assets.put(
                f"concepts/{artifact.spec.canonical}/{artifact.video_sha256}.mp4", data, "video/mp4"
            )
            if hashlib.sha256(await remote_assets.read(artifact.video)).hexdigest() != artifact.video_sha256:
                raise ValueError("Uploaded media verification failed")
    if args.action == "prepare":
        MANIFEST.write_text(json.dumps([a.model_dump(mode="json") for a in artifacts], indent=2))
        logger.info("Concept assets uploaded and verified", count=len(artifacts))
    else:
        if not settings.database_url:
            raise ValueError("Import requires the intended managed DATABASE_URL")
        inserted, existing = import_concepts(Store(settings.database_url, settings.data_dir), artifacts)
        logger.info("Concept revisions imported", inserted=inserted, existing=existing)


if __name__ == "__main__":
    asyncio.run(main())
