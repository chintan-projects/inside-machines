"""Transactional domain storage: SQLite locally, Postgres on Vercel.

The alpha uses one locked document row for budget/deduplication atomicity.
External work is never performed while this lock is held. Data can later move
to indexed tables without changing the public lesson contract.
"""

import json
import sqlite3
from collections.abc import Callable
from contextlib import closing
from pathlib import Path
from typing import TypeVar

import psycopg
from _shared.services.logger import get_logger
from pydantic import BaseModel, Field

logger = get_logger(__name__)
T = TypeVar("T")


class Database(BaseModel):
    """Private domain records; only explicit projections may leave the server."""

    lessons: dict[str, dict[str, object]] = Field(default_factory=dict)
    jobs: dict[str, dict[str, object]] = Field(default_factory=dict)
    users: dict[str, dict[str, object]] = Field(default_factory=dict)
    sessions: dict[str, dict[str, object]] = Field(default_factory=dict)
    chats: dict[str, dict[str, object]] = Field(default_factory=dict)
    feedback: dict[str, dict[str, object]] = Field(default_factory=dict)
    events: list[dict[str, object]] = Field(default_factory=list)
    ledger: dict[str, dict[str, object]] = Field(default_factory=dict)
    spent: float = 0
    reserved: float = 0


class Store:
    """Provide short, serializable read-modify-write transactions."""

    def __init__(self, database_url: str, data_dir: Path) -> None:
        """Configure storage; use Postgres if a connection string is present."""
        self.url = database_url
        self.path = data_dir / "inside.sqlite3"
        data_dir.mkdir(parents=True, exist_ok=True)

    def transaction(self, action: Callable[[Database], T], *, write: bool = True) -> T:
        """Run a side-effect-free callback atomically; roll back on exceptions."""
        if self.url:
            return self._postgres(action, write)
        return self._sqlite(action, write)

    def _sqlite(self, action: Callable[[Database], T], write: bool) -> T:
        with closing(sqlite3.connect(self.path, timeout=20, isolation_level=None)) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS inside_state (id INTEGER PRIMARY KEY, payload TEXT NOT NULL)"
            )
            conn.execute("BEGIN IMMEDIATE")
            try:
                row = conn.execute("SELECT payload FROM inside_state WHERE id=1").fetchone()
                state = Database.model_validate_json(row[0]) if row else Database()
                result = action(state)
                if write:
                    state.events = state.events[-10000:]
                    conn.execute(
                        "INSERT INTO inside_state(id,payload) VALUES(1,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload",
                        (state.model_dump_json(),),
                    )
                conn.commit()
                return result
            except Exception:
                conn.rollback()
                raise

    def _postgres(self, action: Callable[[Database], T], write: bool) -> T:
        with psycopg.connect(self.url, connect_timeout=10) as conn:
            # IF NOT EXISTS alone cannot serialize concurrent first-time DDL.
            # This transaction-scoped lock also releases on rollback/disconnect.
            conn.execute("SELECT pg_advisory_xact_lock(hashtext('inside_state_init'))")
            conn.execute(
                "CREATE TABLE IF NOT EXISTS inside_state (id INTEGER PRIMARY KEY, payload TEXT NOT NULL)"
            )
            conn.execute(
                "INSERT INTO inside_state(id,payload) VALUES(1,%s) ON CONFLICT(id) DO NOTHING",
                (Database().model_dump_json(),),
            )
            row = conn.execute("SELECT payload FROM inside_state WHERE id=1 FOR UPDATE").fetchone()
            if not row:
                raise RuntimeError("Domain state row was not initialized")
            state = Database.model_validate_json(str(row[0]))
            result = action(state)
            if write:
                state.events = state.events[-10000:]
                conn.execute("UPDATE inside_state SET payload=%s WHERE id=1", (state.model_dump_json(),))
            return result

    def snapshot(self) -> Database:
        """Read a consistent copy for owner reports and recovery."""
        return self.transaction(
            lambda state: Database.model_validate(json.loads(state.model_dump_json())), write=False
        )
