"""Prepare, verify and import immutable CE revisions without replacing private history."""

import argparse
import asyncio
import hashlib
import json
import multiprocessing
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from typing import cast

from _shared.services.logger import get_logger
from pydantic import BaseModel, ValidationError

from .ac_concept import aircon_concept
from .assets import Assets
from .concept_render_worker import render_concept_media
from .contracts import LessonSpec
from .curated.catalog import SYSTEMS
from .quality import require_learning_quality
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
    from .curated.compiler import compile_system
    from .vacuum_concept import vacuum_concept
    from .washer_concept import washer_concept

    preserved = [
        (aircon_concept(), ["air-conditioner", "air-conditioner-craft"]),
        (washer_concept(), ["washing-machine"]),
        (cooker_concept(), ["pressure-cooker"]),
        (
            vacuum_concept(),
            [
                "household-vacuum-cleaner",
                "household-vacuum-cleaner-ce-6b5e6fa1d2",
                "bagged-vacuum-ce-2",
                "bagged-vacuum-ce-3",
                "bagged-vacuum-ce-4",
            ],
        ),
    ]
    # Retain the more developed AC/washer/cooker/vacuum artwork instead of regressing
    # it to a new generic drawing. All are consumed by the same shared CE player.
    existing = {"air-conditioner", "washing-machine", "pressure-cooker", "vacuum-cleaner"}
    return preserved + [(compile_system(key), [key]) for key in SYSTEMS if key not in existing]


def _validate_source(
    artifact: ConceptArtifact, sources: dict[str, tuple[LessonSpec, list[str]]],
) -> None:
    """Validate a completed/cached artifact against one current source snapshot."""
    source = sources.get(artifact.spec.canonical)
    if source is None or source[1] != artifact.replaces:
        raise ValueError("Unknown authored revision or replacement set")
    expected = source[0].model_copy(deep=True)
    if len(expected.stages) != len(artifact.spec.stages):
        raise ValueError("Authored storyboard changed")
    for actual, stage in zip(artifact.spec.stages, expected.stages, strict=True):
        stage.duration = actual.duration
    if digest_spec(expected) != artifact.spec_sha256 or digest_spec(artifact.spec) != artifact.spec_sha256:
        raise ValueError("Manifest does not match authored source")
    require_learning_quality(artifact.spec)


def validate_concept(artifact: ConceptArtifact) -> None:
    """Only the authored source may be published under its reserved revision ID."""
    _validate_source(artifact, {spec.canonical: (spec, replaces) for spec, replaces in authored_lessons()})


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
                "curated_system_id": next((key for key in SYSTEMS
                                           if key in a.spec.aliases or id == key + "-ce-1"), "vacuum-cleaner" if id == "bagged-vacuum-ce-5" else ""),
                "production_cost": {"mode": "local-authored", "paid_calls": 0, "speech": a.narration},
            }
            for previous in a.replaces:
                if previous in db.lessons:
                    db.lessons[previous]["archived"] = True
                    db.lessons[previous]["superseded_by"] = id
            inserted += 1
        return inserted, existing

    return store.transaction(publish)


def _checkpoint(artifacts: dict[str, ConceptArtifact]) -> None:
    """One parent writer atomically records each completed immutable artifact."""
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    temporary_manifest = MANIFEST.with_suffix(".next.json")
    temporary_manifest.write_text(json.dumps([a.model_dump(mode="json") for a in artifacts.values()], indent=2))
    temporary_manifest.replace(MANIFEST)


async def render_concepts(settings: Settings, lesson: str | None = None, *, workers: int = 1) -> None:
    """Local deterministic authoring uses computer speech, not a paid provider."""
    local = replace(
        settings,
        database_url="",
        blob_token="",
        production=False,
        video_width=1280,
        video_height=866,
        video_fps=24,
        openai_key="",
        anthropic_key="",
        invite_code="",
        owner_code="",
        session_secret="",
        budget_usd=0,
    )
    if not 1 <= workers <= 4:
        raise ValueError("Concept rendering requires one to four workers")
    sources = {spec.canonical: (spec, replaces) for spec, replaces in authored_lessons()}
    if lesson and lesson not in sources:
        raise ValueError("Unknown authored lesson")
    artifacts: list[ConceptArtifact] = []
    cached: dict[str, ConceptArtifact] = {}
    if MANIFEST.exists():
        candidates: object = json.loads(MANIFEST.read_text())
        if not isinstance(candidates, list):
            raise ValueError("The concept manifest must contain an artifact list")
        for candidate in cast(list[object], candidates):
            try:
                previous = ConceptArtifact.model_validate(candidate)
                _validate_source(previous, sources)
                if previous.video.startswith("https://"):
                    continue
                data = await Assets(local).read(previous.video)
                if hashlib.sha256(data).hexdigest() == previous.video_sha256:
                    cached[previous.spec.canonical] = previous
            except (ValueError, ValidationError, OSError):
                # Changed source or a different local asset directory needs a new render.
                continue
    pending: list[tuple[LessonSpec, list[str]]] = []
    for spec, replaces in sources.values():
        if lesson and spec.canonical != lesson:
            continue
        require_learning_quality(spec)
        if spec.canonical in cached:
            artifacts.append(cached[spec.canonical])
            logger.info("Verified concept render reused", lesson=spec.canonical)
            continue
        pending.append((spec, replaces))

    async def completed(
        spec: LessonSpec, replaces: list[str], pool: ProcessPoolExecutor,
    ) -> ConceptArtifact:
        rendered, data = await asyncio.get_running_loop().run_in_executor(pool, render_concept_media, spec, local)
        if rendered.canonical != spec.canonical:
            raise ValueError("Media worker returned another authored lesson")
        digest = hashlib.sha256(data).hexdigest()
        candidate = ConceptArtifact(
            spec=rendered, spec_sha256=digest_spec(rendered), video="pending-local-media",
            video_sha256=digest, replaces=replaces,
        )
        _validate_source(candidate, sources)
        if not data:
            raise ValueError("Media worker returned no video bytes")
        candidate.video = await Assets(local).put(
            f"concepts/{rendered.canonical}/{digest}.mp4", data, "video/mp4"
        )
        logger.info(
            "Concept lesson rendered", lesson=rendered.canonical,
            duration=round(sum(stage.duration for stage in rendered.stages)), bytes=len(data),
        )
        return candidate

    if pending:
        # Spawn avoids inheriting the parent's open storage connections or locks.
        # Media children cannot publish. Only the parent accepts each completed
        # source/hash binding, stores bytes, and advances the manifest checkpoint.
        pool = ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("spawn"))
        tasks = [asyncio.create_task(completed(spec, replaces, pool)) for spec, replaces in pending]
        try:
            for future in asyncio.as_completed(tasks):
                artifact = await future
                artifacts.append(artifact)
                cached[artifact.spec.canonical] = artifact
                _checkpoint(cached)
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            pool.shutdown(wait=True, cancel_futures=True)
    # A targeted render keeps all other verified source-compatible checkpoints.
    _checkpoint({**cached, **{a.spec.canonical: a for a in artifacts}})
    import_concepts(Store("", local.data_dir), artifacts)


async def main() -> None:
    """Separate rendering, verified private asset upload and atomic publication."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("render", "prepare", "import"))
    parser.add_argument("--lesson", choices=[s.canonical for s, _ in authored_lessons()])
    parser.add_argument("--workers", type=int, choices=range(1, 5), default=1,
                        help="Local rendering processes (1–4); output quality is unchanged")
    args = parser.parse_args()
    settings = load_settings()
    if args.action == "render":
        await render_concepts(settings, args.lesson, workers=args.workers)
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
