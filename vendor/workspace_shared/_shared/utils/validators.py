"""Validate config dictionaries and files before they are used."""

from collections.abc import Mapping
from pathlib import Path

import yaml

from ..services.logger import get_logger

logger = get_logger(__name__)

TypeSpec = type | tuple[type, ...]


class ValidationError(Exception):
    """Raised by callers that want a failed validation to be an exception."""


def validate_config(config: Mapping[str, object], schema: Mapping[str, TypeSpec]) -> list[str]:
    """Check that every schema key is present in ``config`` with the expected type.

    Returns:
        Human-readable problems; empty when the config is valid.
    """
    errors: list[str] = []
    for key, expected in schema.items():
        if key not in config:
            errors.append(f"Missing required config key: {key}")
            continue
        value = config[key]
        if isinstance(value, expected):
            continue
        names = (
            ", ".join(t.__name__ for t in expected)
            if isinstance(expected, tuple)
            else expected.__name__
        )
        errors.append(f"Config '{key}' must be {names}, got {type(value).__name__}")

    if errors:
        logger.warning("Configuration validation failed", error_count=len(errors), errors=errors)
    else:
        logger.debug("Configuration validation passed")
    return errors


def validate_model_path(path: str | Path) -> bool:
    """True if ``path`` (``~`` expanded) is an existing file."""
    file_path = Path(path).expanduser()
    exists = file_path.is_file()
    if exists:
        logger.debug("Model path validated", path=str(path), size_bytes=file_path.stat().st_size)
    else:
        logger.warning("Model path not found", path=str(path))
    return exists


def validate_yaml_file(path: str | Path) -> tuple[bool, str]:
    """Parse a YAML file. Returns ``(True, "")`` or ``(False, reason)``."""
    file_path = Path(path).expanduser()
    if not file_path.exists():
        return _yaml_failure(path, f"File not found: {path}")
    if not file_path.is_file():
        return _yaml_failure(path, f"Not a file: {path}")
    try:
        with file_path.open(encoding="utf-8") as handle:
            yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        return _yaml_failure(path, f"Invalid YAML: {exc}")
    except OSError as exc:
        return _yaml_failure(path, f"Failed to read YAML: {exc}")
    logger.debug("YAML file validated", path=str(path))
    return True, ""


def _yaml_failure(path: str | Path, error: str) -> tuple[bool, str]:
    logger.warning("YAML validation failed", path=str(path), error=error)
    return False, error


def validate_directory_exists(path: str | Path) -> bool:
    """True if ``path`` (``~`` expanded) is an existing directory."""
    exists = Path(path).expanduser().is_dir()
    if exists:
        logger.debug("Directory validated", path=str(path))
    else:
        logger.warning("Directory not found", path=str(path))
    return exists


def validate_file_readable(path: str | Path) -> bool:
    """True if ``path`` is a file that can be opened and read."""
    file_path = Path(path).expanduser()
    if not file_path.is_file():
        logger.warning("File not found", path=str(path))
        return False
    try:
        with file_path.open(encoding="utf-8") as handle:
            handle.read(1)
    except (OSError, UnicodeDecodeError) as exc:
        logger.warning("File not readable", path=str(path), error=str(exc))
        return False
    logger.debug("File validated as readable", path=str(path))
    return True
