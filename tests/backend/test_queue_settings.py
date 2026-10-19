"""Queue dispatch contracts and fail-closed configuration bounds."""

import asyncio
from dataclasses import replace

import pytest

from backend import tasks
from backend.settings import Settings


async def test_production_dispatch_idempotency(settings: Settings, monkeypatch: pytest.MonkeyPatch) -> None:
    """Two requesters join the same durable message identity for a phase."""
    sent: list[tuple[str, dict[str, str], str]] = []

    async def send(topic: str, payload: dict[str, str], *, idempotency_key: str) -> str:
        sent.append((topic, payload, idempotency_key))
        return "test-message"

    monkeypatch.setattr(tasks, "load_settings", lambda: replace(settings, production=True))
    monkeypatch.setattr(tasks, "send", send)
    await tasks.enqueue_job("test-job", "review")
    assert sent == [("inside-lessons", {"job_id": "test-job"}, "test-job:review")]


async def test_local_dispatch_is_explicitly_local(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A local task is observed and removed after completion, with no cloud calls."""
    seen: list[str] = []

    async def consume(payload: dict[str, str]) -> None:
        seen.append(payload["job_id"])

    monkeypatch.setattr(tasks, "load_settings", lambda: settings)
    monkeypatch.setattr(tasks, "consume", consume)
    await tasks.enqueue_job("test-job", "queued")
    running = list(tasks._local_tasks)
    assert running
    await asyncio.gather(*running)
    await asyncio.sleep(0)
    assert seen == ["test-job"] and not tasks._local_tasks


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("budget_usd", float("nan")),
        ("budget_usd", -1),
        ("generation_reserve", 0.1),
        ("text_phase_reserve", 0.01),
        ("chat_reserve", 0.0001),
        ("video_fps", 60),
        ("video_width", 321),
        ("lease_seconds", 10),
        ("lease_seconds", 220),
        ("provider_timeout_seconds", 300),
        ("provider_timeout_seconds", 0),
    ],
)
def test_unsafe_settings_rejected(settings: Settings, field: str, value: float) -> None:
    """Invalid costs, dimensions or leases cannot silently undermine safeguards."""
    values = settings.__dict__ | {field: value}
    with pytest.raises(ValueError):
        Settings(**values)
