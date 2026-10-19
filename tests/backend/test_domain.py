"""Privacy, concurrency, accounting and admission tests against real SQLite."""

import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import pytest
from fastapi import HTTPException

from backend.accounting import charge, reserve
from backend.auth import Auth
from backend.contracts import canonicalize
from backend.domain import Domain, User
from backend.provider import UsageReceipt
from backend.settings import Settings
from backend.store import Database, Store


def test_invite_sessions_revoke_and_expire(store: Store, settings: Settings) -> None:
    """Session tokens are hashed, independently revocable and time limited."""
    auth = Auth(store, settings)
    member, token = auth.login("Ari", settings.invite_code, "127.0.0.1")
    owner, owner_token = auth.login("Owner", settings.owner_code, "127.0.0.1")
    assert not member.owner and owner.owner
    assert auth.user(token) == member
    assert token not in store.snapshot().model_dump_json()
    auth.logout(token)
    with pytest.raises(HTTPException) as revoked:
        auth.user(token)
    assert revoked.value.status_code == 401
    store.transaction(lambda db: db.sessions[auth.digest(owner_token)].update(expires=0))
    with pytest.raises(HTTPException):
        auth.user(owner_token)
    with pytest.raises(HTTPException):
        auth.user(None)


def test_bad_invites_are_persistently_throttled(store: Store, settings: Settings) -> None:
    """Failed attempts must commit even though the endpoint returns an error."""
    auth = Auth(store, settings)
    for _ in range(10):
        with pytest.raises(HTTPException) as failure:
            auth.login("Ari", "wrong", "client")
        assert failure.value.status_code == 401
    with pytest.raises(HTTPException) as limited:
        Auth(store, settings).login("Ari", settings.invite_code, "client")
    assert limited.value.status_code == 429
    assert auth.login("Ari", settings.invite_code, "different-client")[0].name == "Ari"


def test_unconfigured_auth_fails_closed(store: Store, settings: Settings) -> None:
    """A blank invite never turns into an accidental public deployment."""
    with pytest.raises(HTTPException) as failure:
        Auth(store, replace(settings, invite_code="")).login("Ari", "", "client")
    assert failure.value.status_code == 503


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("Can you explain a washer?", "washing-machine"),
        ("How does AC work?", "air-conditioner"),
        ("Tell me about a fridge", "refrigerator"),
        ("How does a pressure cooker work?", "pressure-cooker"),
        ("How does a TV work?", "television"),
        ("How does a dishwasher work?", "dishwasher"),
        ("How does a top-load washer work?", "top-load-washing-machine"),
        ("How does a window AC work?", "window-air-conditioner"),
        ("How does an AC motor work?", "ac-motor"),
        ("How does a stovetop pressure cooker work?", "stovetop-pressure-cooker"),
        ("How does an OLED TV work?", "oled-television"),
        ("How does a coffee machine work?", "coffee-machine"),
    ],
)
def test_aliases(question: str, expected: str) -> None:
    """Common aliases share the same persistent artifact identity."""
    assert canonicalize(question) == expected


def test_concurrent_missing_requests_reserve_once(store: Store, settings: Settings, user: User) -> None:
    """Independent connections race through the real transaction boundary."""
    domain = Domain(store, settings)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: domain.request("How does AC work?", user), range(16)))
    state = store.snapshot()
    assert len(state.jobs) == 1
    assert state.reserved == settings.generation_reserve
    assert sum(not result["reused"] for result in results) == 1
    assert len({str(result["job_id"]) for result in results}) == 1


def test_catalog_hit_no_paid_job(seeded: Store, settings: Settings, user: User) -> None:
    """A second person reuses a lesson with no cost or reservation."""
    domain = Domain(seeded, settings)
    assert domain.request("washer", user)["kind"] == "lesson"
    assert domain.request("washing machine", User(id="other", name="Other", owner=False))["reused"]
    assert not seeded.snapshot().jobs and seeded.snapshot().reserved == 0
    assert domain.catalog()[0]["title"] == "Washing machine"
    domain.feedback("washing-machine", "up", "Helpful", user)
    domain.feedback("washing-machine", "down", "Confusing direction", user, stage=2)
    state = seeded.snapshot()
    assert len(state.feedback) == 1 and state.feedback[f"{user.id}:washing-machine"]["value"] == "down"
    assert state.lessons["washing-machine"]["quality"] == "test-fixture"
    assert state.feedback[f"{user.id}:washing-machine"]["stage"] == 2
    assert state.feedback[f"{user.id}:washing-machine"]["version"] == 1
    with pytest.raises(HTTPException) as invalid:
        domain.feedback("washing-machine", "up", "Wrong step", user, stage=6)
    assert invalid.value.status_code == 422


def test_budget_and_disabled_generation(store: Store, settings: Settings, user: User) -> None:
    """Neither absent credentials nor a depleted ceiling can dispatch AI work."""
    assert (
        Domain(store, replace(settings, openai_key="")).request("air conditioner", user)["kind"]
        == "unavailable"
    )
    assert (
        Domain(store, replace(settings, budget_usd=0.5)).request("air conditioner", user)["kind"] == "budget"
    )
    assert not store.snapshot().jobs


def test_settlement_and_accounting_idempotent(store: Store, settings: Settings, user: User) -> None:
    """Unknown transport billing consumes its allowance; duplicate settlement is free."""
    domain = Domain(store, settings)
    job_id = str(domain.request("air conditioner", user)["job_id"])

    def settle(db: Database) -> None:
        domain.settle(db, db.jobs[job_id], "failed", "Test")
        domain.settle(db, db.jobs[job_id], "failed", "Test")
        reserve(db, 0.1, settings)
        charge(db, "test-operation", UsageReceipt(), 0.1, uncertain=True)
        charge(db, "test-operation", UsageReceipt(), 0.1, uncertain=True)

    store.transaction(settle)
    state = store.snapshot()
    assert state.reserved == 0 and state.spent == 0.1
    assert state.ledger["test-operation"]["uncertain"]
    assert domain.job(job_id)["status"] == "failed"
    assert "user_id" not in domain.job(job_id)


def test_rate_limit_and_rollback(store: Store, settings: Settings, user: User) -> None:
    """A rejected request cannot leave a partial reservation or job behind."""

    def fill(db: Database) -> None:
        db.events.extend(
            {"kind": "generation_requested", "user_id": user.id, "at": time.time()}
            for _ in range(settings.hourly_requests)
        )

    store.transaction(fill)
    with pytest.raises(HTTPException) as limited:
        Domain(store, settings).request("dishwasher", user)
    assert limited.value.status_code == 429
    assert store.snapshot().reserved == 0
    with pytest.raises(HTTPException):
        Domain(store, settings).job("missing")
