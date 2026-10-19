"""Explicit task routing into the workspace gateway's backend extension point."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Literal

from _shared.services.logger import get_logger
from _shared.services.model_gateway import ModelBackend, ModelBackendError

logger = get_logger(__name__)

ModelTask = Literal["authoring", "review", "chat", "speech"]
TASKS: tuple[ModelTask, ...] = ("authoring", "review", "chat", "speech")
BackendFactory = Callable[[str], ModelBackend]


@dataclass(frozen=True)
class ProviderPlugin:
    """Trusted startup registration; no dynamic imports or client-supplied endpoints."""

    factory: BackendFactory
    tasks: frozenset[ModelTask]


@dataclass(frozen=True)
class TaskRoute:
    """Bind one task to an explicitly registered provider and model."""

    provider: str
    model: str


class ProviderRegistry:
    """Validated, immutable route snapshot installed once at application startup.

    Adapters own protocol translation and usage receipts. Their configured prices
    and phase reservations must cover the selected models before enabling a route.
    Unsupported tasks fail at startup; there is no implicit paid fallback.
    """

    def __init__(self, plugins: Mapping[str, ProviderPlugin], routes: Mapping[ModelTask, TaskRoute]) -> None:
        """Reject incomplete or incompatible routing before serving requests."""
        self._plugins = dict(plugins)
        self._routes = dict(routes)
        if set(routes) != set(TASKS):
            raise ValueError("Configure exactly authoring, review, chat and speech routes")
        for task, route in self._routes.items():
            plugin = self._plugins.get(route.provider)
            if plugin is None or task not in plugin.tasks or not route.model.strip():
                raise ValueError(f"Unsupported provider route for {task}")

    def backend(self, route_id: str) -> ModelBackend:
        """Resolve only known task aliases; never treat an unknown model as OpenAI."""
        for task, route in self._routes.items():
            if route_id == gateway_id(task):
                logger.info("Loading task adapter", task=task, provider=route.provider, model=route.model)
                return self._plugins[route.provider].factory(route.model)
        raise ModelBackendError("Unknown model task route")


def gateway_id(task: ModelTask) -> str:
    """Separate gateway resident backends even when tasks use the same model."""
    if task not in TASKS:
        raise ValueError("Unknown model task")
    return "inside:" + task
