"""State checkpoints: one JSON file per snapshot, written atomically, restored by id or latest.

A checkpoint is written to a temporary file in the same directory and then renamed over its
final name with ``os.replace``, so a reader never sees a half-written file and a crash mid-write
leaves the previous checkpoint intact.
"""

import asyncio
import json
import os
import tempfile
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ..logger import get_logger

logger = get_logger(__name__)

# Checkpointed state is caller-defined JSON; the manager does not interpret it.
State = dict[str, Any]


class CheckpointError(Exception):
    """A checkpoint could not be written or read."""


class StateManager:
    """Store and recover state snapshots under one directory."""

    def __init__(self, checkpoint_dir: str | Path = ".checkpoints") -> None:
        """Create the manager and its directory if missing."""
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self._auto_task: asyncio.Task[None] | None = None
        logger.info("StateManager initialized", checkpoint_dir=str(self.checkpoint_dir))

    def _path(self, checkpoint_id: str) -> Path:
        return self.checkpoint_dir / f"{checkpoint_id}.json"

    async def checkpoint(self, state: State, label: str = "") -> str:
        """Write ``state`` as a new checkpoint and return its id.

        Raises:
            CheckpointError: The state is not JSON-serialisable or the write failed.
        """
        checkpoint_id = str(uuid.uuid4())
        record = {
            "id": checkpoint_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "label": label,
            "state": state,
        }
        try:
            payload = json.dumps(record, indent=2)
            self._write_atomically(self._path(checkpoint_id), payload)
        except (TypeError, ValueError, OSError) as exc:
            logger.error("Failed to create checkpoint", error=str(exc), label=label)
            raise CheckpointError(f"Failed to create checkpoint: {exc}") from exc

        logger.info(
            "State checkpoint created",
            checkpoint_id=checkpoint_id,
            label=label,
            size_bytes=len(payload),
        )
        return checkpoint_id

    def _write_atomically(self, target: Path, payload: str) -> None:
        fd, tmp_name = tempfile.mkstemp(dir=self.checkpoint_dir, prefix=".tmp-", suffix=".json")
        tmp_path = Path(tmp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_path, target)
        except OSError:
            tmp_path.unlink(missing_ok=True)
            raise

    async def restore(self, checkpoint_id: str | None = None) -> State | None:
        """Return the state of ``checkpoint_id``, or of the latest checkpoint when ``None``.

        A corrupted file is skipped in favour of the next most recent one. Returns ``None`` when
        there is nothing to restore.

        Raises:
            CheckpointError: Every candidate file was corrupted.
        """
        if checkpoint_id is None:
            checkpoint_id = self._find_latest_checkpoint()
            if checkpoint_id is None:
                logger.info("No checkpoints found")
                return None

        path = self._path(checkpoint_id)
        if not path.is_file():
            logger.warning("Checkpoint file not found", checkpoint_id=checkpoint_id)
            return None

        try:
            with path.open(encoding="utf-8") as handle:
                record = json.load(handle)
        except json.JSONDecodeError as exc:
            logger.warning(
                "Corrupted checkpoint file, skipping", checkpoint_id=checkpoint_id, error=str(exc)
            )
            previous = self._find_previous_checkpoint(checkpoint_id)
            if previous is not None:
                return await self.restore(previous)
            raise CheckpointError(f"Checkpoint file corrupted: {exc}") from exc

        state = record.get("state", {})
        if not isinstance(state, dict):
            raise CheckpointError(f"Checkpoint {checkpoint_id} has no state mapping")
        logger.info(
            "State checkpoint restored", checkpoint_id=checkpoint_id, label=record.get("label", "")
        )
        return state

    def start_auto_checkpoint(
        self, state_provider: Callable[[], State], interval_s: float = 30.0
    ) -> None:
        """Checkpoint ``state_provider()`` every ``interval_s`` seconds until stopped."""
        if self._auto_task is not None:
            logger.warning("Auto-checkpoint already running")
            return
        self._auto_task = asyncio.create_task(
            self._auto_checkpoint_loop(state_provider, interval_s)
        )
        logger.info("Auto-checkpoint started", interval_s=interval_s)

    def stop_auto_checkpoint(self) -> None:
        """Cancel the periodic checkpoint task, if running."""
        if self._auto_task is None:
            logger.warning("Auto-checkpoint not running")
            return
        self._auto_task.cancel()
        self._auto_task = None
        logger.info("Auto-checkpoint stopped")

    async def _auto_checkpoint_loop(
        self, state_provider: Callable[[], State], interval_s: float
    ) -> None:
        try:
            while True:
                await asyncio.sleep(interval_s)
                try:
                    await self.checkpoint(state_provider(), label="auto")
                except CheckpointError as exc:
                    logger.error("Auto-checkpoint failed", error=str(exc))
        except asyncio.CancelledError:
            logger.debug("Auto-checkpoint loop cancelled")

    def _sorted_files(self) -> list[Path]:
        """Checkpoint files, newest first by modification time."""
        return sorted(
            self.checkpoint_dir.glob("*.json"), key=lambda p: p.stat().st_mtime_ns, reverse=True
        )

    def _find_latest_checkpoint(self) -> str | None:
        files = self._sorted_files()
        return files[0].stem if files else None

    def _find_previous_checkpoint(self, current_id: str) -> str | None:
        files = self._sorted_files()
        names = [f.stem for f in files]
        if current_id not in names:
            return None
        index = names.index(current_id)
        return names[index + 1] if index + 1 < len(names) else None

    def list_checkpoints(self) -> list[dict[str, str]]:
        """``id``, ``timestamp`` and ``label`` of every readable checkpoint, newest first."""
        checkpoints: list[dict[str, str]] = []
        for path in self.checkpoint_dir.glob("*.json"):
            try:
                with path.open(encoding="utf-8") as handle:
                    record = json.load(handle)
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Skipping unreadable checkpoint", path=str(path), error=str(exc))
                continue
            checkpoints.append(
                {
                    "id": str(record.get("id", path.stem)),
                    "timestamp": str(record.get("timestamp", "")),
                    "label": str(record.get("label", "")),
                }
            )
        return sorted(checkpoints, key=lambda c: c["timestamp"], reverse=True)

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Remove one checkpoint. Returns whether a file was deleted."""
        path = self._path(checkpoint_id)
        if not path.is_file():
            logger.warning("Checkpoint not found", checkpoint_id=checkpoint_id)
            return False
        path.unlink()
        logger.info("Checkpoint deleted", checkpoint_id=checkpoint_id)
        return True
