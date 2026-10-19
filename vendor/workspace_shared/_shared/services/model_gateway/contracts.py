"""Types shared by the gateway, the registry and the backends.

Everything a caller sees (``Message``, ``ModelResult``, the error hierarchy) and everything a
backend implements (``Request``, ``BackendOutput``, ``ModelBackend``) lives here so the modules
that use them never import each other in a cycle.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, Protocol, TypedDict


class ModelGatewayError(Exception):
    """Base class for gateway failures."""


class ModelUnavailableError(ModelGatewayError):
    """No model in the requested chain could serve the call.

    Raised when every model in ``models`` is unregistered, fails to load, errors during the call
    or exceeds ``timeout_ms``. ``reasons`` maps each tried model id to why it failed. Callers
    treat this as "use the fallback", never as a crash.
    """

    def __init__(self, message: str, reasons: dict[str, str] | None = None) -> None:
        super().__init__(message)
        self.reasons: dict[str, str] = dict(reasons or {})


class ModelBackendError(ModelGatewayError):
    """One model failed to load or errored during a call. The gateway tries the next model."""


class LabelTokenizationError(ModelGatewayError):
    """A label in ``label_tokens`` is not exactly one token after the prompt for this model.

    This is a caller contract violation, not a model outage, so the gateway raises it instead of
    moving down the chain: a weaker model silently answering would hide the bug.
    """

    def __init__(self, model_id: str, label: str, detail: str) -> None:
        super().__init__(f"label {label!r} is not a single token for {model_id!r}: {detail}")
        self.model_id = model_id
        self.label = label


class Message(TypedDict):
    """One chat turn; the backend applies the model's chat template."""

    role: Literal["system", "user", "assistant"]
    content: str


@dataclass(frozen=True)
class ModelResult:
    """What a completed call returns.

    ``label_probs`` is present only when ``label_tokens`` was given: the softmax over the label
    tokens' logits, renormalized so it sums to 1. ``label_mass`` is the raw probability those
    tokens held before renormalization (how much of the model's next-token belief the labels
    cover); a build-time test uses it to check a prompt actually elicits a label.
    """

    text: str
    model_id: str
    latency_ms: float
    label_probs: dict[str, float] | None = None
    label_mass: float | None = None


@dataclass(frozen=True)
class Request:
    """One validated call, as handed to a backend. Exactly one of ``prompt``/``messages`` is set."""

    prompt: str | None
    messages: tuple[Message, ...] | None
    grammar: str | None
    max_tokens: int
    label_tokens: tuple[str, ...] | None


@dataclass(frozen=True)
class BackendOutput:
    """What a backend returns for one ``Request``; the gateway adds model id and latency."""

    text: str
    label_probs: dict[str, float] | None = None
    label_mass: float | None = None


class ModelBackend(Protocol):
    """One loaded model. ``run`` blocks; the gateway calls it from a thread under a lock."""

    @property
    def model_id(self) -> str:
        """The registry id this backend serves."""

    @property
    def n_ctx(self) -> int:
        """The context window the model was loaded with."""

    def run(self, request: Request) -> BackendOutput:
        """Serve one request.

        Raises:
            ModelBackendError: The model errored; the gateway counts the model as failed.
            LabelTokenizationError: A label is not one token; propagated to the caller.
        """


def validate_labels(label_tokens: Sequence[str] | None) -> tuple[str, ...] | None:
    """Normalize ``label_tokens``: ``None`` stays ``None``; else non-empty, distinct, non-blank.

    Raises:
        ValueError: The list is empty, has a duplicate, or has an empty label.
    """
    if label_tokens is None:
        return None
    labels = tuple(label_tokens)
    if not labels:
        raise ValueError("label_tokens must not be empty")
    if any(not label for label in labels):
        raise ValueError("label_tokens must not contain an empty label")
    if len(set(labels)) != len(labels):
        raise ValueError("label_tokens must be distinct")
    return labels
