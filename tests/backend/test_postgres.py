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


def test_postgres_craft_import_preserves_private_history(settings: Settings, user: User) -> None:
    """A real serialized publication adds a revision without replacing private history."""
    from backend.ac_craft import CANONICAL, aircon_craft
    from backend.craft import CraftArtifact, import_craft
    from backend.seed_aircon import aircon
    from backend.starters import digest_spec

    target = urlparse(URL)
    if target.hostname != "127.0.0.1" or target.port != 55432 or target.path != "/inside_test":
        pytest.fail("Craft import tests require the disposable loopback Postgres")
    store = Store(URL, settings.data_dir)
    old, revised = aircon(), aircon_craft()

    def history(db: Database) -> None:
        db.lessons["air-conditioner"] = {"id": "air-conditioner", "spec": old.model_dump(mode="json")}
        db.chats["retained"] = {"lesson_id": "air-conditioner", "messages": [{"text": "prior question"}]}
        db.feedback["retained"] = {"value": "down", "lesson_id": "air-conditioner"}

    store.transaction(history)
    before = store.snapshot()
    artifact = CraftArtifact(
        spec=revised, spec_sha256=digest_spec(revised), video="test.mp4", video_sha256="0" * 64
    )
    assert import_craft(store, artifact)
    assert not import_craft(store, artifact)
    after = store.snapshot()
    assert after.chats == before.chats and after.feedback == before.feedback
    assert after.spent == before.spent and after.reserved == before.reserved
    assert after.lessons["air-conditioner"]["spec"] == before.lessons["air-conditioner"]["spec"]
    assert Domain(store, settings).request("How does AC work?", user) == {
        "kind": "lesson",
        "lesson_id": CANONICAL,
        "reused": True,
    }
    assert "air-conditioner" not in {item["id"] for item in Domain(store, settings).catalog()}


def test_postgres_concept_and_review_transactions_preserve_history(settings: Settings) -> None:
    """Real publication/review writes migrate an old payload without dropping private fields."""
    from backend.ac_concept import aircon_concept
    from backend.concept_publication import ConceptArtifact, import_concepts
    from backend.learning_reviews import LearningReviews, ReviewSubmission
    from backend.starters import digest_spec

    target = urlparse(URL)
    if target.hostname != "127.0.0.1" or target.port != 55432 or target.path != "/inside_test":
        pytest.fail("Concept tests require disposable loopback Postgres")
    store = Store(URL, settings.data_dir)
    before = store.snapshot()
    spec = aircon_concept()
    artifact = ConceptArtifact(
        spec=spec,
        spec_sha256=digest_spec(spec),
        video="synthetic.mp4",
        video_sha256="0" * 64,
        replaces=["air-conditioner", "air-conditioner-craft"],
    )
    assert import_concepts(store, [artifact]) == (1, 0)
    owner = User(id="synthetic-review-owner", name="Synthetic test owner", owner=True)
    record = ReviewSubmission(
        spec_sha256=digest_spec(spec),
        video_sha256="0" * 64,
        gate="engineering",
        reviewer="Synthetic agent",
        method="agent",
        decision="pass",
        evidence="Synthetic transaction test; not actual human review evidence.",
    )
    assert not LearningReviews(store).record(spec.canonical, record, owner)["ready"]
    after = store.snapshot()
    assert before.chats == after.chats and before.feedback == after.feedback and before.ledger == after.ledger
    assert before.spent == after.spent and before.reserved == after.reserved
    for id, lesson in before.lessons.items():
        assert after.lessons[id]["spec"] == lesson["spec"]
