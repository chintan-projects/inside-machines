"""Routing contracts use explicit test adapters, never paid provider requests."""

from dataclasses import dataclass

import pytest
from _shared.services.model_gateway import BackendOutput, ModelBackendError, ModelUnavailableError, Request

from backend.provider import configure_gateway, model_speech, model_text
from backend.routing import TASKS, ProviderPlugin, ProviderRegistry, TaskRoute
from backend.settings import Settings


@dataclass
class RecordingBackend:
    """Minimal gateway-compatible adapter records the selected model and request."""

    model_id: str
    calls: list[tuple[str, Request]]
    n_ctx: int = 32000

    def run(self, request: Request) -> BackendOutput:
        """Return unmistakably synthetic text or an encoded synthetic speech payload."""
        self.calls.append((self.model_id, request))
        return BackendOutput(text="dGVzdC1hdWRpbw==" if self.model_id == "test-speech" else "test-answer")


async def test_tasks_use_separate_plugins_models_and_limits(settings: Settings) -> None:
    """Changing composition routes author, reviewer, chat and speech independently."""
    calls: list[tuple[str, Request]] = []
    routes = {task: TaskRoute("voice" if task == "speech" else "text", "test-" + task) for task in TASKS}
    registry = ProviderRegistry(
        {
            "text": ProviderPlugin(lambda model: RecordingBackend(model, calls), frozenset(TASKS[:-1])),
            "voice": ProviderPlugin(lambda model: RecordingBackend(model, calls), frozenset({"speech"})),
        },
        routes,
    )
    configure_gateway(settings, registry)
    try:
        assert await model_text("research", settings, task="research") == "test-answer"
        assert await model_text("author", settings) == "test-answer"
        assert await model_text("review", settings, task="review") == "test-answer"
        assert await model_text("chat", settings, chat=True) == "test-answer"
        assert await model_speech("voice", settings) == b"test-audio"
        assert [model for model, _ in calls] == ["test-" + task for task in TASKS]
        assert [request.max_tokens for _, request in calls] == [
            settings.max_research_tokens,
            settings.max_output_tokens,
            settings.max_output_tokens,
            settings.max_chat_tokens,
            1,
        ]
    finally:
        configure_gateway(settings)


@pytest.mark.parametrize("failure", ["missing-task", "unknown-provider", "wrong-capability", "empty-model"])
def test_invalid_routes_fail_before_dispatch(failure: str) -> None:
    """Bad routing is rejected before loading an adapter or reserving paid work."""
    calls: list[tuple[str, Request]] = []
    routes = {task: TaskRoute("test", "test-model") for task in TASKS}
    tasks = frozenset(TASKS)
    if failure == "missing-task":
        del routes["speech"]
    elif failure == "unknown-provider":
        routes["chat"] = TaskRoute("absent", "test-model")
    elif failure == "wrong-capability":
        tasks = frozenset({"authoring"})
    else:
        routes["chat"] = TaskRoute("test", " ")
    with pytest.raises(ValueError):
        ProviderRegistry(
            {"test": ProviderPlugin(lambda model: RecordingBackend(model, calls), tasks)}, routes
        )
    assert calls == []


async def test_failed_plugin_has_no_implicit_fallback(settings: Settings) -> None:
    """A failing chat adapter cannot silently trigger another paid provider."""
    attempts: list[str] = []

    def failed(model: str) -> RecordingBackend:
        attempts.append(model)
        raise ModelBackendError("Explicit synthetic failure")

    registry = ProviderRegistry(
        {"failed": ProviderPlugin(failed, frozenset(TASKS))},
        {task: TaskRoute("failed", "test-" + task) for task in TASKS},
    )
    with pytest.raises(ModelBackendError, match="Unknown"):
        registry.backend("unknown-provider-model")
    configure_gateway(settings, registry)
    try:
        with pytest.raises(ModelUnavailableError):
            await model_text("test", settings, chat=True)
        assert attempts == ["test-chat"]
    finally:
        configure_gateway(settings)
