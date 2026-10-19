"""Checkpoint and restore application state as JSON files, written atomically."""

from .checkpoint import CheckpointError, StateManager

__all__ = ["CheckpointError", "StateManager"]
