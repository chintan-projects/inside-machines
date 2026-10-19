"""Optional real Postgres tests, restricted to the disposable local test container."""

import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Lock
from urllib.parse import urlparse

import psycopg
import pytest

from backend.domain import Domain, User
from backend.settings import Settings
from backend.store import Database, Store

URL = os.environ.get("INSIDE_TEST_DATABASE_URL", "")
pytestmark = pytest.mark.skipif(not URL, reason="Disposable local Postgres has not been requested")


def test_postgres_first_request_concurrency(
    settings: Settings, user: User, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Race cold-start connections, deduplicate a real job, and check rollback."""
    target = urlparse(URL)
    if target.hostname != "127.0.0.1" or target.port != 55432 or target.path != "/inside_test":
        pytest.fail("Postgres tests only run against the disposable loopback container on port 55432")
    with psycopg.connect(URL) as connection:
        connection.execute("DROP TABLE IF EXISTS inside_state")
    # Hold cold connections until all eight can enter schema initialization together.
    connect = psycopg.connect
    barrier, lock = Barrier(8), Lock()
    arrivals = 0

    def synchronized_connect(
        conninfo: str, *, connect_timeout: int
    ) -> psycopg.Connection[tuple[object, ...]]:
        nonlocal arrivals
        connection: psycopg.Connection[tuple[object, ...]] = connect(
            conninfo, connect_timeout=connect_timeout
        )
        with lock:
            arrivals += 1
            synchronize = arrivals <= 8
        if synchronize:
            barrier.wait(timeout=10)
        return connection

    monkeypatch.setattr("backend.store.psycopg.connect", synchronized_connect)
    store = Store(URL, settings.data_dir)
    domain = Domain(store, settings)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: domain.request("How does AC work?", user), range(16)))
    state = store.snapshot()
    assert len(state.jobs) == 1 and state.reserved == settings.generation_reserve
    assert len({str(result["job_id"]) for result in results}) == 1

    def fail(db: Database) -> None:
        db.spent = 100
        raise ValueError("Synthetic rollback check")

    with pytest.raises(ValueError):
        store.transaction(fail)
    assert store.snapshot().spent == 0
