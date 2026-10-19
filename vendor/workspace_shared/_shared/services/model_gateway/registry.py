"""Read the model registry at ``${MODELS_DIR}/config.yaml``.

``MODELS_DIR`` defaults to ``~/Projects/_models``. The registry's own ``${MODELS_DIR}``
placeholders resolve to the same directory, so a caller never needs the variable exported.
"""

import os
from pathlib import Path
from typing import Any

from ..config_loader import ConfigError, load_config
from ..logger import get_logger
from .contracts import ModelGatewayError, ModelUnavailableError

logger = get_logger(__name__)

# One registry entry is free-form YAML (path, context_length, default_params, ...).
ModelEntry = dict[str, Any]

_DEFAULT_MODELS_DIR = "~/Projects/_models"
_DEFAULT_STATIC_MESSAGE = "The model is temporarily unavailable. Please try again shortly."


def models_dir() -> Path:
    """The directory that holds model files and ``config.yaml``."""
    return Path(os.getenv("MODELS_DIR", _DEFAULT_MODELS_DIR)).expanduser()


def registry_path() -> Path:
    """The registry file, ``<models_dir>/config.yaml``."""
    return models_dir() / "config.yaml"


def _load_config(force: bool = False) -> dict[str, Any]:
    path = registry_path()
    try:
        return load_config(path, env={"MODELS_DIR": str(models_dir())}, force=force)
    except ConfigError as exc:
        raise ModelGatewayError(f"Failed to load model registry {path}: {exc}") from exc


def _load_registry(force: bool = False) -> dict[str, ModelEntry]:
    path = registry_path()
    config = _load_config(force)
    models = config.get("models")
    if not isinstance(models, dict):
        raise ModelGatewayError(f"Model registry {path} has no 'models' mapping")
    return models


def get_available_models(force: bool = False) -> list[str]:
    """Names of every registered model, in registry order.

    Raises:
        ModelGatewayError: The registry is missing or malformed.
    """
    names = list(_load_registry(force))
    logger.debug("Registry read", model_count=len(names))
    return names


def get_model_config(model_id: str, force: bool = False) -> ModelEntry:
    """The registry entry for ``model_id`` with ``${MODELS_DIR}`` resolved.

    Raises:
        ModelUnavailableError: ``model_id`` is not registered.
        ModelGatewayError: The registry is missing or malformed.
    """
    models = _load_registry(force)
    if model_id not in models:
        raise ModelUnavailableError(
            f"Model {model_id!r} is not registered; available: {sorted(models)}"
        )
    entry = models[model_id]
    if not isinstance(entry, dict):
        raise ModelGatewayError(f"Registry entry for {model_id!r} is not a mapping")
    return entry


def get_static_response(force: bool = False) -> str:
    """The canned text served for ``static_response``: the registry's ``static_response.message``.

    Falls back to a built-in sentence when the registry cannot be read or has no such entry,
    since the static response exists for exactly the moments when nothing else works.
    """
    try:
        config = _load_config(force)
    except ModelGatewayError as exc:
        logger.warning("static_response read failed; using built-in text", reason=str(exc))
        return _DEFAULT_STATIC_MESSAGE
    entry = config.get("static_response")
    message = entry.get("message") if isinstance(entry, dict) else None
    return message if isinstance(message, str) and message else _DEFAULT_STATIC_MESSAGE
