"""Durable admission survives telemetry eviction, restarts, migration and concurrency."""

import time
from dataclasses import replace

import pytest
from fastapi import HTTPException

from backend.auth import Auth
from backend.chat import Chats
from backend.contracts import AnswerSpec
from backend.provider import receipt_context
from backend.rate_limits import rate_key, take_rate
from backend.settings import Settings
from backend.store import Database, Store


def flood_telemetry(db: Database) -> None:
    """Reproduce the exact Store eviction caused by ordinary signed-in lesson reads."""
    db.events.extend({"kind": "lesson_opened", "user_id": "synthetic-reader", "at": time.time(),
                      "lesson_id": "washing-machine"} for _ in range(10000))


def test_guest_and_conversation_limits_survive_telemetry_eviction_and_store_restart(
    seeded: Store, settings: Settings,
) -> None:
    config = replace(settings, public_access=True)
    auth = Auth(seeded, config)
    guest, _ = auth.guest(None, "synthetic-network")
    for _ in range(19):
        auth.guest(None, "synthetic-network")
    chats = Chats(seeded, config)
    for _ in range(20):
        chats.create("washing-machine", guest)
    seeded.transaction(flood_telemetry)
    db = seeded.snapshot()
    assert len(db.events) == 10000 and all(e["kind"] == "lesson_opened" for e in db.events)
    assert len(db.rate_limits[rate_key("guest", auth.digest("synthetic-network"))]) == 20
    assert len(db.rate_limits[rate_key("conversation", guest.id)]) == 20
    restarted = Store("", settings.data_dir)
    with pytest.raises(HTTPException) as issuance:
        Auth(restarted, config).guest(None, "synthetic-network")
    with pytest.raises(HTTPException) as conversation:
        Chats(restarted, config).create("washing-machine", guest)
    assert issuance.value.status_code == conversation.value.status_code == 429
    assert restarted.snapshot() == db


def test_active_legacy_limits_migrate_before_any_store_telemetry_trimming(
    store: Store, settings: Settings,
) -> None:
    config = replace(settings, public_access=True)
    auth = Auth(store, config)
    address = auth.digest("legacy-network")

    def legacy(db: Database) -> None:
        db.rate_limits_version = 0
        db.rate_limits = {}
        db.events = [{"kind": "guest_started", "address": address, "at": time.time()} for _ in range(20)]

    store.transaction(legacy)
    before = store.snapshot()
    with pytest.raises(HTTPException) as limited:
        auth.guest(None, "legacy-network")
    assert limited.value.status_code == 429 and store.snapshot() == before
    # Even if rejected admission rolled back its migration, the next successful
    # telemetry write migrates before deleting any older quota observations.
    store.transaction(flood_telemetry)
    migrated = store.snapshot()
    assert migrated.rate_limits_version == 1
    assert len(migrated.rate_limits[rate_key("guest", address)]) == 20
    assert all(e["kind"] == "lesson_opened" for e in migrated.events)
    with pytest.raises(HTTPException):
        auth.guest(None, "legacy-network")
    assert store.snapshot() == migrated


async def test_paid_browser_and_network_limits_survive_eviction_without_extra_calls(
    seeded: Store, settings: Settings,
) -> None:
    config = replace(settings, public_access=True, budget_usd=50)
    auth = Auth(seeded, config)
    first, _ = auth.guest(None, "paid-network")
    second, _ = auth.guest(None, "paid-network")
    third, _ = auth.guest(None, "paid-network")
    calls = 0

    async def answer(prompt: str, current: Settings) -> str:
        nonlocal calls
        calls += 1
        receipt = receipt_context.get()
        assert receipt is not None
        receipt.models.append("synthetic-rate-test")
        receipt.cost_usd = .003
        return AnswerSpec(answer="A synthetic bounded answer.", stage=None, part=None, source_indices=[0], uncertain=False).model_dump_json()

    chats = Chats(seeded, config, answer)
    one, two, three = [chats.create("washing-machine", guest) for guest in (first, second, third)]
    for i in range(6):
        await chats.ask(one.id, "Synthetic first browser question?", f"first-browser-{i}", first)
        await chats.ask(two.id, "Synthetic second browser question?", f"second-browser-{i}", second)
    seeded.transaction(flood_telemetry)
    before = seeded.snapshot()
    for chat, user in ((one, first), (three, third)):
        with pytest.raises(HTTPException) as rejected:
            await chats.ask(chat.id, "Should remain limited after reads?", "after-eviction", user)
        assert rejected.value.status_code == 429
    assert calls == 12 and seeded.snapshot() == before and seeded.snapshot().reserved == 0
    assert seeded.snapshot().spent == pytest.approx(.036)
    # Retrying the exact already-accounted operation consumes neither rate nor budget.
    await chats.ask(one.id, "Synthetic first browser question?", "first-browser-0", first)
    assert seeded.snapshot() == before and calls == 12
    other, _ = auth.guest(None, "another-paid-network")
    other_chat = chats.create("washing-machine", other)
    before_budget = seeded.snapshot()
    with pytest.raises(HTTPException) as budget:
        await Chats(seeded, replace(config, budget_usd=.036), answer).ask(
            other_chat.id, "Budget rejected operations must not consume quota?", "rate-reserve-rollback", other)
    assert budget.value.status_code == 429 and seeded.snapshot() == before_budget and calls == 12


def test_login_failures_cannot_be_erased_by_public_telemetry(seeded: Store, settings: Settings) -> None:
    auth = Auth(seeded, replace(settings, public_access=True))
    for _ in range(10):
        with pytest.raises(HTTPException) as rejected:
            auth.login("Synthetic intruder", "wrong-code", "login-network")
        assert rejected.value.status_code == 401
    seeded.transaction(flood_telemetry)
    before = seeded.snapshot()
    with pytest.raises(HTTPException) as throttled:
        auth.login("Owner", settings.owner_code, "login-network")
    assert throttled.value.status_code == 429 and seeded.snapshot() == before


def test_rate_windows_expire_and_active_buckets_are_never_evicted(
    store: Store, monkeypatch: pytest.MonkeyPatch,
) -> None:
    now = [10000.0]
    monkeypatch.setattr("backend.rate_limits.time.time", lambda: now[0])
    monkeypatch.setattr("backend.rate_limits.MAX_BUCKETS", 2)
    for subject in ("one", "two"):
        def consume(db: Database, subject: str = subject) -> None:
            take_rate(db, "guest", subject, 1, "Synthetic limit")
        store.transaction(consume)
    before = store.snapshot()
    with pytest.raises(HTTPException):
        store.transaction(lambda db: take_rate(db, "guest", "three", 1, "Synthetic limit"))
    assert store.snapshot() == before
    now[0] += 3599
    with pytest.raises(HTTPException):
        store.transaction(lambda db: take_rate(db, "guest", "one", 1, "Synthetic limit"))
    now[0] += 2
    store.transaction(lambda db: take_rate(db, "guest", "three", 1, "Synthetic limit"))
    assert store.snapshot().rate_limits == {rate_key("guest", "three"): [now[0]]}


def test_legacy_capacity_overflow_fails_closed_for_omitted_active_subjects(
    store: Store, monkeypatch: pytest.MonkeyPatch,
) -> None:
    now = [20000.0]
    monkeypatch.setattr("backend.rate_limits.time.time", lambda: now[0])
    monkeypatch.setattr("backend.rate_limits.MAX_BUCKETS", 2)

    def legacy(db: Database) -> None:
        db.rate_limits_version = 0
        db.events = [{"kind": "guest_started", "address": f"legacy-{i}", "at": now[0]} for i in range(3)]

    store.transaction(legacy)
    store.transaction(flood_telemetry)
    assert len(store.snapshot().rate_limits) == 2
    with pytest.raises(HTTPException):
        store.transaction(lambda db: take_rate(db, "guest", "legacy-2", 20, "Synthetic limit"))
    now[0] += 3601
    store.transaction(lambda db: take_rate(db, "guest", "legacy-2", 20, "Synthetic limit"))
    assert len(store.snapshot().rate_limits) == 1
