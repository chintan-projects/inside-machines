"""Anonymous issuance and preview permissions share the real locked document transaction."""

import asyncio
import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from urllib.parse import urlparse

import psycopg
import pytest
from fastapi import HTTPException

from backend.auth import Auth
from backend.chat import Chats
from backend.contracts import AnswerSpec, LessonSpec
from backend.domain import User
from backend.native_publication import PreparedNative, import_native
from backend.provider import receipt_context
from backend.public_preview import PreviewSubmission, PublicPreviews, public_preview_identity
from backend.settings import Settings
from backend.starters import digest_spec
from backend.store import Database, Store

URL = os.environ.get("INSIDE_TEST_DATABASE_URL", "")
pytestmark = pytest.mark.skipif(not URL, reason="Disposable local Postgres has not been requested")


def test_postgres_public_guest_and_preview_concurrency(
    settings: Settings, native_prepared: PreparedNative,
) -> None:
    """Distinct browser identities, one permission, exact revocation, no release/budget fiction."""
    target = urlparse(URL)
    if target.hostname != "127.0.0.1" or target.port != 55432 or target.path != "/inside_test":
        pytest.fail("Public access tests require disposable loopback Postgres")
    with psycopg.connect(URL) as connection:
        connection.execute("DROP TABLE IF EXISTS inside_state")
    config = replace(settings, public_access=True)
    store = Store(URL, settings.data_dir)
    import_native(store, [native_prepared])
    store.transaction(lambda db: (db.chats.update({"private-before-public": {"messages": ["PRIVATE FIXTURE"]}}),
                                 db.ledger.update({"prior-receipt": {"charged_usd": .017}})))
    before = store.snapshot()
    auth = Auth(store, config)
    with ThreadPoolExecutor(max_workers=8) as pool:
        guests = list(pool.map(lambda _: auth.guest(None, "synthetic-shared-network"), range(16)))
    assert len({guest.id for guest, _ in guests}) == len({token for _, token in guests}) == 16
    assert len(store.snapshot().sessions) == len(store.snapshot().users) == 16
    assert all(guest.guest and not guest.owner for guest, _ in guests)
    assert "synthetic-shared-network" not in store.snapshot().model_dump_json()
    owner = User(id="synthetic-public-owner", name="Synthetic owner", owner=True)
    service = PublicPreviews(store)
    body = PreviewSubmission(spec_sha256=digest_spec(native_prepared.spec), video_sha256=native_prepared.proof.video_sha256,
                             bundle_sha256="", enabled=True)
    with ThreadPoolExecutor(max_workers=8) as pool:
        enabled = list(pool.map(lambda _: service.set(native_prepared.spec.canonical, body, owner), range(16)))
    assert sum(result["reused"] is False for result in enabled) == 1
    public = store.snapshot()
    assert public_preview_identity(public, native_prepared.spec.canonical)
    assert public.learning_reviews == before.learning_reviews and public.notifications == before.notifications
    assert public.chats == before.chats and public.ledger == before.ledger
    assert public.spent == public.reserved == 0 and not public.jobs
    with pytest.raises(HTTPException):
        service.set(native_prepared.spec.canonical, body.model_copy(update={"video_sha256": "0" * 64}), owner)
    assert store.snapshot() == public
    # A broken current artifact is hidden and still revocable by its saved exact permission.
    store.transaction(lambda db: db.lessons[native_prepared.spec.canonical].update(native_proof_sha256="0" * 64))
    assert not public_preview_identity(store.snapshot(), native_prepared.spec.canonical)
    with ThreadPoolExecutor(max_workers=8) as pool:
        disabled = list(pool.map(lambda _: service.set(native_prepared.spec.canonical, body.model_copy(update={"enabled": False}), owner), range(16)))
    assert sum(result["reused"] is False for result in disabled) == 1
    final = store.snapshot()
    assert final.chats == before.chats and final.ledger == before.ledger and not final.learning_reviews
    assert not final.notifications and final.spent == final.reserved == 0


def test_postgres_durable_public_limits_and_atomic_paid_admission(
    settings: Settings, spec: LessonSpec,
) -> None:
    """Races and 10k telemetry evictions cannot reset issuance, browser or network caps."""
    target = urlparse(URL)
    if target.hostname != "127.0.0.1" or target.port != 55432 or target.path != "/inside_test":
        pytest.fail("Public quota tests require disposable loopback Postgres")
    with psycopg.connect(URL) as connection:
        connection.execute("DROP TABLE IF EXISTS inside_state")
    config = replace(settings, public_access=True, budget_usd=50)
    store = Store(URL, settings.data_dir)
    store.transaction(lambda db: db.lessons.update({spec.canonical: {"id": spec.canonical, "spec": spec.model_dump(mode="json")}}))
    auth = Auth(store, config)

    def guest(_: int) -> User | None:
        try:
            return auth.guest(None, "pg-network")[0]
        except HTTPException as exc:
            assert exc.status_code == 429
            return None

    with ThreadPoolExecutor(max_workers=8) as pool:
        candidates = list(pool.map(guest, range(32)))
    users = [candidate for candidate in candidates if candidate is not None]
    assert len(users) == len({user.id for user in users}) == 20
    assert len(store.snapshot().sessions) == 20

    async def answer(prompt: str, current: Settings) -> str:
        await asyncio.sleep(.002)
        receipt = receipt_context.get()
        assert receipt is not None
        receipt.models.append("synthetic-pg-quota")
        receipt.cost_usd = .003
        return AnswerSpec(answer="Synthetic bounded quota answer.", stage=None, part=None, source_indices=[0], uncertain=False).model_dump_json()

    chats = Chats(store, config, answer)
    # Separate chats avoid the per-conversation pending lease masking rate races.
    sessions = [chats.create(spec.canonical, users[i % 2]) for i in range(20)]

    def independent_ask(i: int) -> bool:
        try:
            asyncio.run(chats.ask(sessions[i].id, "A synthetic concurrent quota question?", f"pg-rate-{i}", users[i % 2]))
            return True
        except HTTPException as exc:
            assert exc.status_code == 429
            return False

    with ThreadPoolExecutor(max_workers=8) as pool:
        admitted = list(pool.map(independent_ask, range(20)))
    assert sum(admitted) == 12 and len(store.snapshot().ledger) == 12
    assert store.snapshot().spent == pytest.approx(.036)
    assert store.snapshot().reserved == pytest.approx(0, abs=1e-12)

    def flood(db: Database) -> None:
        db.events.extend({"kind": "lesson_opened", "user_id": users[0].id, "at": time.time()} for _ in range(10000))

    store.transaction(flood)
    before = store.snapshot()
    assert guest(0) is None
    with pytest.raises(HTTPException) as browser_limit:
        asyncio.run(chats.ask(sessions[0].id, "Still limited after telemetry?", "pg-after-eviction", users[0]))
    unused_chat = chats.create(spec.canonical, users[2])
    after_create = store.snapshot()
    with pytest.raises(HTTPException) as network_limit:
        asyncio.run(chats.ask(unused_chat.id, "Same network must remain limited?", "pg-network-eviction", users[2]))
    assert browser_limit.value.status_code == network_limit.value.status_code == 429
    assert store.snapshot() == after_create and store.snapshot().ledger == before.ledger
