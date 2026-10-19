"""Model gateway: the one path every project uses to call a local model.

Backend: llama-cpp-python against GGUF files named in ``${MODELS_DIR}/config.yaml``. One
resident ``Llama`` per model id, a per-model lock, calls off the event loop in a thread.
See ``~/Projects/docs/architecture-decisions/002-model-gateway-backend.md``.
"""

from .contracts import (
    BackendOutput,
    LabelTokenizationError,
    Message,
    ModelBackend,
    ModelBackendError,
    ModelGatewayError,
    ModelResult,
    ModelUnavailableError,
    Request,
)
from .gateway import (
    STATIC_RESPONSE,
    BackendFactory,
    invoke_model,
    load_model,
    load_model_async,
    loaded_models,
    reset_models,
    set_backend_factory,
)
from .registry import get_available_models, get_model_config, get_static_response, registry_path

__all__ = [
    "STATIC_RESPONSE",
    "BackendFactory",
    "BackendOutput",
    "LabelTokenizationError",
    "Message",
    "ModelBackend",
    "ModelBackendError",
    "ModelGatewayError",
    "ModelResult",
    "ModelUnavailableError",
    "Request",
    "get_available_models",
    "get_model_config",
    "get_static_response",
    "invoke_model",
    "load_model",
    "load_model_async",
    "loaded_models",
    "registry_path",
    "reset_models",
    "set_backend_factory",
]
