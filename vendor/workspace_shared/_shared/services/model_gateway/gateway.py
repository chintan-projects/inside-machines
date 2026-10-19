"""Gateway entry points: ``invoke_model``, ``load_model`` and the resident-model table.

One backend object per model id lives here for the process lifetime, each behind its own
``threading.Lock`` because a ``Llama`` is not thread-safe and every call blocks. ``invoke_model``
walks the caller's ``models`` chain in order and runs each attempt in ``asyncio.to_thread`` under
that model's lock.

``timeout_ms`` is observed, not enforced (plan Amendment 1): a blocking llama call cannot be
cancelled, so on timeout the caller sees ``TimeoutError`` folded into the chain, counts the model
as failed and moves on, while the abandoned call finishes in its thread and releases the lock
when it does. With ``max_tokens=1`` or ``label_tokens`` an abandoned call is bounded by one
prompt evaluation. Load the first model of a profile at startup with ``load_model`` so a cold
load never counts against a request budget.
"""

import asyncio
import threading
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from ..logger import get_logger
from .contracts import (
    BackendOutput,
    LabelTokenizationError,
    Message,
    ModelBackend,
    ModelGatewayError,
    ModelResult,
    ModelUnavailableError,
    Request,
    validate_labels,
)
from .registry import get_static_response

logger = get_logger(__name__)

STATIC_RESPONSE = "static_response"

BackendFactory = Callable[[str], ModelBackend]
"""Builds (loads) the backend for a model id. Blocking; called under the model's lock."""


@dataclass
class _Slot:
    lock: threading.Lock = field(default_factory=threading.Lock)
    backend: ModelBackend | None = None


_slots: dict[str, _Slot] = {}
_slots_guard = threading.Lock()
_factory: BackendFactory | None = None


LOCAL_EXTRA_INSTALL = 'pip install "workspace-shared[local]"'
"""The install line that brings in the llama-cpp backend (an optional extra since 2026-09-30)."""


def _default_factory(model_id: str) -> ModelBackend:
    try:
        from .backend_llamacpp import LlamaCppBackend
    except ModuleNotFoundError as exc:
        if (exc.name or "").partition(".")[0] != "llama_cpp":
            raise
        raise ModelUnavailableError(
            f"llama-cpp-python is not installed, so {model_id!r} cannot load; "
            f"install the local backend with: {LOCAL_EXTRA_INSTALL}"
        ) from exc
    return LlamaCppBackend(model_id)


def set_backend_factory(factory: BackendFactory | None) -> None:
    """Replace how models are built (``None`` restores llama-cpp). Drops every resident model."""
    global _factory
    _factory = factory
    reset_models()


def reset_models() -> None:
    """Forget every resident model; the next call reloads. In-flight calls keep their object."""
    with _slots_guard:
        _slots.clear()


def loaded_models() -> list[str]:
    """Ids of the models resident right now."""
    with _slots_guard:
        return [model_id for model_id, slot in _slots.items() if slot.backend is not None]


def _slot(model_id: str) -> _Slot:
    with _slots_guard:
        return _slots.setdefault(model_id, _Slot())


def _load_locked(model_id: str, slot: _Slot) -> ModelBackend:
    """Build the backend if absent. Caller holds ``slot.lock``."""
    if slot.backend is None:
        factory = _factory if _factory is not None else _default_factory
        slot.backend = factory(model_id)
    return slot.backend


def load_model(model_id: str) -> ModelBackend:
    """Load ``model_id`` now (blocking) and keep it resident; a no-op if already loaded.

    Safe to call from any thread: it takes the model's lock, so a concurrent call waits for the
    load instead of loading twice.

    Raises:
        ModelUnavailableError: ``model_id`` is not registered or no backend is installed.
        ModelBackendError: The load failed.
    """
    slot = _slot(model_id)
    with slot.lock:
        return _load_locked(model_id, slot)


async def load_model_async(model_id: str) -> ModelBackend:
    """``load_model`` off the event loop, in a worker thread."""
    return await asyncio.to_thread(load_model, model_id)


def _run_blocking(model_id: str, request: Request) -> BackendOutput:
    slot = _slot(model_id)
    with slot.lock:
        backend = _load_locked(model_id, slot)
        return backend.run(request)


def _static_result(started: float) -> ModelResult:
    logger.warning("chain reached static_response; serving canned text")
    return ModelResult(
        text=get_static_response(),
        model_id=STATIC_RESPONSE,
        latency_ms=(time.perf_counter() - started) * 1000,
    )


async def invoke_model(
    prompt: str | None = None,
    messages: Sequence[Message] | None = None,
    *,
    models: Sequence[str],
    grammar: str | None = None,
    max_tokens: int = 64,
    timeout_ms: int = 3000,
    label_tokens: Sequence[str] | None = None,
) -> ModelResult:
    """Run one call against the first model in ``models`` that serves it.

    Exactly one of ``prompt`` (raw completion text) or ``messages`` (chat turns, formatted with
    the model's own template) is given. With ``label_tokens``, the result carries
    ``label_probs`` (renormalized over the labels) and ``text`` is the argmax label; without it,
    the model generates up to ``max_tokens`` at temperature 0, constrained by ``grammar`` (GBNF)
    when given. ``static_response`` is served only when it appears in ``models``.

    Raises:
        ValueError: Malformed arguments (both or neither prompt source, empty ``models``,
            non-positive ``max_tokens`` or ``timeout_ms``, bad ``label_tokens``).
        LabelTokenizationError: A label is not one token for the model that reached it. Not a
            fallback trigger: it names a bug in the caller's labels for that model.
        ModelUnavailableError: Every model failed to load, errored, or timed out; ``reasons``
            says why per model.
    """
    if (prompt is None) == (messages is None):
        raise ValueError("invoke_model needs exactly one of prompt or messages")
    if not models:
        raise ValueError("invoke_model needs at least one model id")
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")
    if timeout_ms <= 0:
        raise ValueError("timeout_ms must be positive")
    request = Request(
        prompt=prompt,
        messages=tuple(messages) if messages is not None else None,
        grammar=grammar,
        max_tokens=max_tokens,
        label_tokens=validate_labels(label_tokens),
    )

    reasons: dict[str, str] = {}
    for model_id in models:
        started = time.perf_counter()
        if model_id == STATIC_RESPONSE:
            return _static_result(started)
        try:
            output = await asyncio.wait_for(
                asyncio.to_thread(_run_blocking, model_id, request), timeout=timeout_ms / 1000
            )
        except LabelTokenizationError:
            raise
        except TimeoutError:
            reasons[model_id] = f"timed out after {timeout_ms} ms; the call finishes in its thread"
            logger.warning("model timed out", model_id=model_id, timeout_ms=timeout_ms)
            continue
        except ModelGatewayError as exc:
            reasons[model_id] = str(exc)
            logger.warning("model failed; trying next", model_id=model_id, reason=str(exc))
            continue
        latency_ms = (time.perf_counter() - started) * 1000
        logger.debug("model call served", model_id=model_id, latency_ms=round(latency_ms, 1))
        return ModelResult(
            text=output.text,
            model_id=model_id,
            latency_ms=latency_ms,
            label_probs=output.label_probs,
            label_mass=output.label_mass,
        )

    detail = "; ".join(f"{model_id}: {reason}" for model_id, reason in reasons.items())
    logger.error("no model in chain could serve the call", models=list(models), reasons=reasons)
    raise ModelUnavailableError(
        f"no model in {list(models)} could serve the call: {detail}", reasons=reasons
    )
