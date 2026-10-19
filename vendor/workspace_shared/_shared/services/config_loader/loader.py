"""Load YAML configuration files and resolve ``${VAR}`` placeholders.

Placeholders are resolved from the process environment, optionally supplemented by an explicit
mapping (which wins over the environment). An unresolvable placeholder is an error, never an
empty string: a config that silently loses a path is worse than one that refuses to load.
"""

import os
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal, overload

import yaml

from ..logger import get_logger

logger = get_logger(__name__)

# Parsed YAML is arbitrarily nested; callers narrow the shape they read.
ConfigDict = dict[str, Any]

_PLACEHOLDER = re.compile(r"\$\{([^}]+)\}")
_config_cache: dict[str, ConfigDict] = {}


class ConfigError(Exception):
    """Configuration could not be loaded, parsed or resolved."""


@overload
def get_env(key: str, default: str | None = None, *, required: Literal[True]) -> str: ...


@overload
def get_env(key: str, default: str | None = None, required: bool = False) -> str | None: ...


def get_env(key: str, default: str | None = None, required: bool = False) -> str | None:
    """Read an environment variable.

    Raises:
        ConfigError: ``required`` is true and the variable is unset with no default.
    """
    value = os.getenv(key, default)
    if value is None and required:
        raise ConfigError(f"Required environment variable not set: {key}")
    return value


def _resolve_placeholders(value: str, env: Mapping[str, str]) -> str:
    def replacer(match: re.Match[str]) -> str:
        name = match.group(1)
        resolved = env.get(name, os.getenv(name))
        if resolved is None:
            raise ConfigError(f"Environment variable not found for placeholder: ${{{name}}}")
        return resolved

    return _PLACEHOLDER.sub(replacer, value)


def _resolve_tree(obj: object, env: Mapping[str, str]) -> object:
    if isinstance(obj, dict):
        return {key: _resolve_tree(item, env) for key, item in obj.items()}
    if isinstance(obj, list):
        return [_resolve_tree(item, env) for item in obj]
    if isinstance(obj, str):
        return _resolve_placeholders(obj, env)
    return obj


def load_config(
    config_path: str | Path,
    *,
    env: Mapping[str, str] | None = None,
    force: bool = False,
) -> ConfigDict:
    """Load a YAML file as a dict with every ``${VAR}`` placeholder resolved.

    Args:
        config_path: Path to the YAML file.
        env: Extra variables for placeholder resolution; they take precedence over ``os.environ``.
        force: Reload even if this path is cached.

    Raises:
        ConfigError: The file is missing, is not valid YAML, is not a mapping at the top
            level, or references a variable that is not set.
    """
    cache_key = str(config_path)
    if cache_key in _config_cache and not force:
        logger.debug("Configuration loaded from cache", config_path=cache_key)
        return _config_cache[cache_key]

    path = Path(config_path)
    if not path.is_file():
        raise ConfigError(f"Configuration file not found: {cache_key}")

    try:
        with path.open(encoding="utf-8") as handle:
            raw = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise ConfigError(f"Failed to parse YAML configuration {cache_key}: {exc}") from exc

    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ConfigError(f"Configuration must be a mapping at the top level: {cache_key}")

    resolved = _resolve_tree(raw, env or {})
    assert isinstance(resolved, dict)  # _resolve_tree preserves the dict shape
    config: ConfigDict = resolved
    _config_cache[cache_key] = config
    logger.info("Configuration loaded", config_path=cache_key, keys=sorted(config))
    return config


def clear_cache() -> None:
    """Forget every cached configuration (tests and hot reloads)."""
    _config_cache.clear()
    logger.debug("Configuration cache cleared")


class ConfigLoader:
    """Named configs under one directory: ``ConfigLoader(base).load("model-gateway")``."""

    def __init__(self, base_path: str | Path, env: Mapping[str, str] | None = None) -> None:
        """Bind to a directory of ``<name>.yaml`` files.

        Args:
            base_path: Directory that holds the YAML files.
            env: Extra variables for placeholder resolution, as for :func:`load_config`.
        """
        self.base_path = Path(base_path)
        self._env = dict(env or {})
        self._current: ConfigDict = {}

    def path_for(self, name: str) -> Path:
        """Return the file that ``name`` refers to (``.yaml`` first, then ``.yml``)."""
        for suffix in (".yaml", ".yml"):
            candidate = self.base_path / f"{name}{suffix}"
            if candidate.is_file():
                return candidate
        return self.base_path / f"{name}.yaml"

    def load(self, name: str, force: bool = False) -> ConfigDict:
        """Load ``<base_path>/<name>.yaml`` and make it the current config for :meth:`get`."""
        self._current = load_config(self.path_for(name), env=self._env, force=force)
        return self._current

    def get(self, key: str, *, env_var: str | None = None, default: object = None) -> object:
        """Read a value: ``env_var`` if set, else the loaded config, else ``default``."""
        if env_var is not None:
            from_env = os.getenv(env_var)
            if from_env is not None:
                return from_env
        return self._current.get(key, default)
