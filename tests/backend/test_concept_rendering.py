"""Bounded local media parallelism preserves checkpoints and immutable imports."""

import hashlib
import json
import pickle
import subprocess
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

import pytest

from backend import concept_publication as publication
from backend import concept_render_worker as worker
from backend.contracts import LessonSpec
from backend.settings import Settings
from backend.store import Store


def candidates(spec: LessonSpec, count: int) -> list[tuple[LessonSpec, list[str]]]:
    """Explicit synthetic lessons remain confined to each test's temporary database."""
    results: list[tuple[LessonSpec, list[str]]] = []
    for i in range(count):
        candidate = spec.model_copy(deep=True)
        candidate.canonical = f"synthetic-render-{i}"
        candidate.title = f"Synthetic render fixture {i}"
        results.append((candidate, []))
    return results


async def test_bounded_parallel_render_verified_cache_and_immutable_source_change(
    settings: Settings, ce_spec: LessonSpec, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Four workers keep output quality; cache needs matching source AND media bytes."""
    sources = candidates(ce_spec, 6)
    manifest = tmp_path / "manifest.json"
    monkeypatch.setattr(publication, "MANIFEST", manifest)
    monkeypatch.setattr(publication, "authored_lessons", lambda: sources)
    limits: list[int] = []

    def pool(max_workers: int, **kwargs: object) -> ThreadPoolExecutor:
        limits.append(max_workers)
        assert "mp_context" in kwargs
        return ThreadPoolExecutor(max_workers=max_workers)

    monkeypatch.setattr(publication, "ProcessPoolExecutor", pool)
    guard = threading.Lock()
    calls, running, maximum = 0, 0, 0

    def render(spec: LessonSpec, local: Settings) -> tuple[LessonSpec, bytes]:
        nonlocal calls, running, maximum
        assert (local.video_width, local.video_height, local.video_fps) == (1280, 866, 24)
        assert not local.production and not local.database_url and not local.blob_token
        assert not local.openai_key and not local.anthropic_key and local.budget_usd == 0
        with guard:
            calls += 1
            running += 1
            maximum = max(maximum, running)
        time.sleep(.03)
        with guard:
            running -= 1
        return spec.model_copy(deep=True), ("SYNTHETIC TEST VIDEO " + spec.title).encode()

    monkeypatch.setattr(publication, "render_concept_media", render)
    await publication.render_concepts(settings, workers=4)
    assert calls == 6 and maximum == 4 and limits == [4]
    original = Store("", settings.data_dir).snapshot()
    assert len(original.lessons) == 6 and not original.ledger and not original.reserved
    checkpoint = json.loads(manifest.read_text())
    assert len(checkpoint) == 6
    for item in checkpoint:
        data = (settings.data_dir / "assets" / item["video"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == item["video_sha256"]
    await publication.render_concepts(settings, workers=4)
    assert calls == 6 and limits == [4]  # No worker pool is opened for valid cache hits.
    # Targeting one cached lesson must not erase the other completed checkpoints.
    await publication.render_concepts(settings, lesson=sources[0][0].canonical, workers=4)
    assert len(json.loads(manifest.read_text())) == 6
    # A changed source may not reuse matching-ID media or replace the stored revision.
    sources[0][0].title = "Synthetic changed source"
    with pytest.raises(ValueError, match="immutable"):
        await publication.render_concepts(settings, lesson=sources[0][0].canonical, workers=4)
    assert calls == 7
    assert Store("", settings.data_dir).snapshot().lessons == original.lessons


async def test_failed_worker_keeps_completed_checkpoint_without_partial_publication(
    settings: Settings, ce_spec: LessonSpec, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An interrupted batch resumes finished bytes but never claims full publication."""
    sources = candidates(ce_spec, 2)
    manifest = tmp_path / "manifest.json"
    monkeypatch.setattr(publication, "MANIFEST", manifest)
    monkeypatch.setattr(publication, "authored_lessons", lambda: sources)
    monkeypatch.setattr(publication, "ProcessPoolExecutor", lambda **kwargs: ThreadPoolExecutor(max_workers=2))

    def render(spec: LessonSpec, local: Settings) -> tuple[LessonSpec, bytes]:
        if spec.canonical.endswith("1"):
            time.sleep(.1)
            raise RuntimeError("Synthetic media worker failure")
        return spec.model_copy(deep=True), b"SYNTHETIC TEST VIDEO"

    monkeypatch.setattr(publication, "render_concept_media", render)
    with pytest.raises(RuntimeError, match="worker failure"):
        await publication.render_concepts(settings, workers=2)
    saved = [publication.ConceptArtifact.model_validate(item) for item in json.loads(manifest.read_text())]
    assert len(saved) == 1 and saved[0].spec.canonical.endswith("0")
    publication.validate_concept(saved[0])
    assert not Store("", settings.data_dir).snapshot().lessons


def test_worker_preserves_source_and_requires_local_only_settings(
    settings: Settings, ce_spec: LessonSpec, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only durations change; speech, encoding settings and actual audio inputs survive."""
    before = ce_spec.model_dump_json()
    commands: list[list[str]] = []

    def command(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        commands.append(args)
        assert kwargs["check"] and kwargs["capture_output"]
        target = Path(args[4] if args[0] == "/usr/bin/say" else args[-1])
        target.write_bytes(b"SYNTHETIC TEST AUDIO")
        return subprocess.CompletedProcess(args, 0)

    def video(spec: LessonSpec, audio: list[Path], folder: Path, local: Settings,
              heartbeat: Callable[[], None]) -> Path:
        assert len(audio) == len(spec.stages) and all(p.read_bytes() == b"SYNTHETIC TEST AUDIO" for p in audio)
        assert all(stage.duration == pytest.approx(6) for stage in spec.stages)
        result = folder / "synthetic.mp4"
        result.write_bytes(b"SYNTHETIC TEST VIDEO")
        return result

    monkeypatch.setattr("backend.concept_render_worker.subprocess.run", command)
    monkeypatch.setattr(worker, "audio_duration", lambda path: 5.3)
    monkeypatch.setattr(worker, "render_video", video)
    rendered, data = worker.render_concept_media(ce_spec, settings)
    assert data == b"SYNTHETIC TEST VIDEO" and rendered != ce_spec
    assert ce_spec.model_dump_json() == before and len(commands) == 2*len(ce_spec.stages)
    for local in (replace(settings, production=True), replace(settings, database_url="postgres://synthetic"),
                  replace(settings, blob_token="synthetic")):
        with pytest.raises(ValueError, match="isolated local"):
            worker.render_concept_media(ce_spec, local)
    # The actual spawn worker entry point and its typed payload are picklable.
    decoded = pickle.loads(pickle.dumps((worker.render_concept_media, ce_spec, settings)))
    assert decoded[0] is worker.render_concept_media and decoded[1] == ce_spec


@pytest.mark.parametrize("count", [0, 5])
async def test_worker_limit_is_bounded(settings: Settings, count: int) -> None:
    """CLI and direct callers share the same one-to-four-process cap."""
    with pytest.raises(ValueError, match="one to four"):
        await publication.render_concepts(settings, workers=count)
