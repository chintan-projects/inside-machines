"""Exercise checkpoint/replay safety and real video encoding without paid models."""

import subprocess
from pathlib import Path

import imageio_ffmpeg  # type: ignore[import-untyped]  # Upstream package has no type marker.
import pytest

from backend.assets import Assets
from backend.contracts import LessonSpec, ReviewSpec
from backend.domain import Domain, User
from backend.pipeline import Pipeline
from backend.provider import UsageReceipt, receipt_context
from backend.render import audio_duration, draw_scene, part_pose, stage_at
from backend.settings import Settings
from backend.store import Database, Store


@pytest.fixture
def sound(tmp_path: Path) -> bytes:
    """An audible synthetic tone tests the encoder, never represented as narration."""
    output = tmp_path / "test-tone.mp3"
    subprocess.run(
        [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-y",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=1",
            str(output),
        ],
        check=True,
        timeout=15,
    )
    return output.read_bytes()


@pytest.mark.parametrize("revision", [False, True])
async def test_full_phase_pipeline_real_mp4(
    store: Store,
    settings: Settings,
    user: User,
    ce_spec: LessonSpec,
    sound: bytes,
    monkeypatch: pytest.MonkeyPatch,
    revision: bool,
) -> None:
    """Only provider output is synthetic; jobs, storage and ffmpeg run for real."""
    spec = ce_spec
    calls: list[str] = []
    deliveries: list[tuple[str, str]] = []

    async def enqueue(job_id: str, phase: str) -> None:
        deliveries.append((job_id, phase))

    async def text(
        prompt: str, config: Settings, *, schema: dict[str, object], task: str = "authoring"
    ) -> str:
        assert config == settings and schema
        assert task == ("review" if prompt.startswith("Review") else "authoring")
        receipt = receipt_context.get()
        assert receipt is not None
        receipt.models.append("synthetic-test-provider")
        receipt.cost_usd = 0.01
        calls.append("review" if prompt.startswith("Review") else "author")
        return (
            ReviewSpec(accepted=True, notes=[], lesson=spec).model_dump_json()
            if prompt.startswith("Review")
            else spec.model_dump_json()
        )

    async def speech(narration: str, config: Settings) -> bytes:
        assert narration and config == settings
        receipt = receipt_context.get()
        assert receipt is not None
        receipt.models.append("synthetic-test-speech")
        receipt.cost_usd = 0.001
        calls.append("voice")
        return sound

    monkeypatch.setattr("backend.pipeline.model_text", text)
    monkeypatch.setattr("backend.pipeline.model_speech", speech)
    pipeline = Pipeline(store, settings, Assets(settings), enqueue)
    domain = Domain(store, settings)
    if revision:
        old = spec.model_copy(deep=True)

        def preserve(db: Database) -> None:
            db.lessons[old.canonical] = {"id": old.canonical, "spec": old.model_dump(mode="json")}
            db.chats["private-parent"] = {"lesson_id": old.canonical, "messages": []}

        store.transaction(preserve)
        job_id = str(
            domain.request(
                "washer",
                User(id="owner", name="Test owner", owner=True),
                revision_of=old.canonical,
                operation="explicit-test-operation",
            )["job_id"]
        )
        spec.canonical = str(store.snapshot().jobs[job_id]["canonical"])
    else:
        job_id = str(domain.request("washer", user)["job_id"])
    await pipeline.run(job_id)
    while deliveries:
        delivered_id, _ = deliveries.pop(0)
        await pipeline.run(delivered_id)
    state = store.snapshot()
    assert state.jobs[job_id]["status"] == "complete"
    assert calls == ["author", "review", "voice", "voice", "voice"]
    assert state.spent == pytest.approx(0.023) and state.reserved == pytest.approx(0)
    lesson = state.lessons[spec.canonical]
    if revision:
        assert state.lessons[old.canonical]["spec"] == old.model_dump(mode="json")
        assert state.lessons[old.canonical]["superseded_by"] == spec.canonical
        assert state.chats["private-parent"]["lesson_id"] == old.canonical
    video = settings.data_dir / "assets" / str(lesson["video"])
    assert video.stat().st_size > 1000
    assert audio_duration(video) == pytest.approx(15, abs=0.3)
    assert domain.request("washing machine", user)["kind"] == "lesson"
    await pipeline.run(job_id)
    assert len(calls) == 5 and store.snapshot().spent == pytest.approx(0.023)
    assert list((settings.data_dir / "checkpoints").glob("*.json"))


async def test_paid_output_replayed_after_worker_interruption(
    store: Store, settings: Settings, user: User
) -> None:
    """A saved paid result is reused if the worker died before advancing its phase."""

    async def enqueue(job_id: str, phase: str) -> None:
        return None

    pipeline = Pipeline(store, settings, Assets(settings), enqueue)
    job_id = str(Domain(store, settings).request("air conditioner", user)["job_id"])
    job = pipeline._claim(job_id)
    assert job is not None
    key = pipeline._begin_call(job_id, str(job["lease_token"]), "author", 0.65)
    pipeline._finish_call(
        job_id,
        str(job["lease_token"]),
        key,
        UsageReceipt(cost_usd=0.07, models=["test-provider"]),
        failed=False,
        result="saved-output",
    )
    store.transaction(lambda db: db.jobs[job_id].update(lease_until=0))
    claimed = pipeline._claim(job_id)
    assert claimed is not None

    async def never_call() -> str:
        raise AssertionError("A completed provider request must not be repeated")

    assert await pipeline._paid(claimed, "author", never_call) == "saved-output"
    assert store.snapshot().spent == 0.07


async def test_expired_unknown_call_fails_without_spending_twice(
    store: Store, settings: Settings, user: User
) -> None:
    """The owner sees an interrupted cost allowance instead of an unbounded retry."""

    async def enqueue(job_id: str, phase: str) -> None:
        raise AssertionError("Failed work must not be enqueued")

    pipeline = Pipeline(store, settings, Assets(settings), enqueue)
    job_id = str(Domain(store, settings).request("air conditioner", user)["job_id"])
    job = pipeline._claim(job_id)
    assert job is not None
    pipeline._begin_call(job_id, str(job["lease_token"]), "author", 0.65)
    with pytest.raises(RuntimeError, match="leased"):
        await pipeline.run(job_id)
    store.transaction(lambda db: db.jobs[job_id].update(lease_until=0))
    await pipeline.run(job_id)
    state = store.snapshot()
    assert state.jobs[job_id]["status"] == "failed"
    assert state.spent == 0.65 and state.reserved == pytest.approx(0)
    assert state.ledger[f"lesson:{job_id}:author"]["uncertain"]


async def test_rejected_review_never_published(
    store: Store, settings: Settings, user: User, spec: LessonSpec, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Schema validity alone does not make an editorially rejected lesson public."""

    async def enqueue(job_id: str, phase: str) -> None:
        return None

    async def rejected(
        prompt: str, config: Settings, *, schema: dict[str, object], task: str = "authoring"
    ) -> str:
        receipt = receipt_context.get()
        assert receipt is not None
        receipt.models.append("test-provider")
        receipt.cost_usd = 0.01
        return ReviewSpec(accepted=False, notes=["Wrong flow direction"], lesson=spec).model_dump_json()

    monkeypatch.setattr("backend.pipeline.model_text", rejected)
    job_id = str(Domain(store, settings).request("washer", user)["job_id"])
    store.transaction(lambda db: db.jobs[job_id].update(phase="review", spec=spec.model_dump(mode="json")))
    await Pipeline(store, settings, Assets(settings), enqueue).run(job_id)
    state = store.snapshot()
    assert not state.lessons and state.jobs[job_id]["status"] == "failed"
    assert state.spent == 0.01 and state.reserved == pytest.approx(0)


def test_scene_stage_bounds_and_transforms(spec: LessonSpec) -> None:
    """Scrubbing is deterministic, with no nonfinite or disconnected transforms."""
    assert stage_at(spec, -1) == (0, 0)
    assert stage_at(spec, 100) == (2, 1)
    assert part_pose(spec.parts[0], 1, 0.5) == (0, 0, 90)
    assert part_pose(spec.parts[1], 1, 0.5) == (45, 0, 0)
    for seconds in (0, 6, 12, 15):
        assert draw_scene(spec, seconds, width=300, height=180).size == (300, 180)


async def test_local_assets_reject_path_traversal(settings: Settings) -> None:
    """Artifact delivery never accepts arbitrary paths or remote hosts."""
    assets = Assets(settings)
    key = await assets.put("lessons/test/video.mp4", b"test", "video/mp4")
    assert await assets.read(key) == b"test"
    for bad in ("../secret", "/absolute", "folder/../../secret", "folder\\secret"):
        with pytest.raises(ValueError):
            await assets.put(bad, b"test", "video/mp4")
    with pytest.raises(ValueError):
        await assets.read("https://attacker.example/secret")


def test_transaction_exception_rolls_back(store: Store) -> None:
    """Budget changes disappear if a callback cannot commit its complete operation."""

    def fail(db: Database) -> None:
        db.spent = 100
        raise ValueError("synthetic callback failure")

    with pytest.raises(ValueError):
        store.transaction(fail)
    assert store.snapshot().spent == 0
