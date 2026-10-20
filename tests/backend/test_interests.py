"""Demand is free; publication and member-private notification are separate."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.ac_concept import aircon_concept
from backend.app import create_app
from backend.domain import User
from backend.interests import Interests
from backend.learning_bundle import learning_bundle
from backend.learning_reviews import LearningReviews, ReviewSubmission
from backend.settings import Settings
from backend.starters import digest_spec
from backend.store import Database, Store


def test_concurrent_interest_deduplicates_without_reserving(store: Store, settings: Settings) -> None:
    """Many family requests share one topic; they do not create a paid job."""
    service = Interests(store, settings)
    with ThreadPoolExecutor(max_workers=8) as pool:
        replies = list(pool.map(lambda i: service.request("How does a car work?", User(id=f"u{i}", name="Tester", owner=False)), range(16)))
    assert len({r["interest_id"] for r in replies}) == 1
    db = store.snapshot()
    assert len(db.topic_interests) == 1 and len(next(iter(db.topic_interests.values()))["members"]) == 16  # type: ignore[arg-type] # asserted known test record
    assert not db.jobs and not db.ledger and db.spent == db.reserved == 0


def test_requests_never_dispatch_even_with_funded_provider(settings: Settings, tmp_path: Path) -> None:
    """The public route is collection-only even when production generation is enabled."""
    calls: list[str] = []
    async def dispatch(job: str, phase: str) -> None:
        calls.append(job)
    config = replace(settings, data_dir=tmp_path, openai_key="synthetic-enabled-key", budget_usd=50)
    with TestClient(create_app(config, enqueue=dispatch)) as client:
        client.post("/api/v1/auth/login", json={"name": "Family", "code": config.invite_code})
        response = client.post("/api/v1/requests", json={"question": "A dishwasher", "scope": "general"})
        assert response.status_code == 200 and response.json()["kind"] == "interest"
        assert len(client.get("/api/v1/requests").json()) == 1
        assert client.get("/api/v1/owner/requests").status_code == 403
        assert client.post(f"/api/v1/owner/requests/{response.json()['interest_id']}/build", json={}).status_code == 403
    assert not calls
    state = Store("", tmp_path).snapshot()
    assert state.spent == state.reserved == 0 and not state.jobs


def test_private_subscriptions_and_owner_queue(store: Store, settings: Settings, user: User) -> None:
    service = Interests(store, settings)
    other = User(id="other", name="Other", owner=False)
    service.request("car", user)
    service.request("sink trap", other)
    assert [r["question"] for r in service.mine(user)] == ["car"]
    with pytest.raises(HTTPException):
        service.queue(user)
    rows = service.queue(User(id="owner", name="Owner", owner=True))
    assert len(rows) == 2 and all("members" not in row for row in rows)


def test_release_is_required_and_notices_are_idempotent(store: Store, settings: Settings, user: User) -> None:
    """Synthetic human evidence exercises the protocol; it is not a real review."""
    service = Interests(store, settings)
    request = service.request("refrigerator", user)
    waiting = User(id="waiting-for-import", name="Synthetic requester", owner=False)
    service.request("air conditioner", waiting)
    key = str(request["interest_id"])
    owner = User(id="owner", name="Owner", owner=True)
    spec = aircon_concept()
    def seed(db: Database) -> None:
        db.lessons[spec.canonical] = {"id": spec.canonical, "spec": spec.model_dump(mode="json"), "video": "fixture.mp4", "video_sha256": "a" * 64}
    store.transaction(seed)
    service.update(key, "working", spec.canonical, "Synthetic test binding", owner)
    with pytest.raises(HTTPException) as held:
        service.update(key, "available", spec.canonical, "", owner)
    assert held.value.status_code == 409 and not service.updates(user)
    reviews = LearningReviews(store)
    for gate in ("engineering", "technical", "craft", "learning", "release"):
        data: dict[str, object] = dict(spec_sha256=digest_spec(spec), video_sha256="a" * 64,
            gate=gate, reviewer="Synthetic protocol fixture", method="human", decision="pass",
            evidence="Synthetic test evidence, not an actual reviewer or learner session.", independent=True, real_device=True, device="Synthetic phone")
        if gate == "learning":
            data["scores"] = [{"participant": f"anon-{i}", "baseline": 0, "causal": 2, "transfer": 2} for i in range(5)]
        reviews.record(spec.canonical, ReviewSubmission.model_validate(data), owner)
    assert len(service.updates(waiting)) == 1  # Imported core binds earlier matching demand on release.
    assert service.mine(waiting)[0]["lesson_id"] == spec.canonical
    service.update(key, "available", spec.canonical, "", owner)
    assert len(service.updates(user)) == 1
    other = User(id="later", name="Later", owner=False)
    service.request("refrigerator", other)
    assert len(service.updates(other)) == 1 and len(service.updates(user)) == 1
    notification = str(service.updates(user)[0]["id"])
    with pytest.raises(HTTPException):
        service.read(notification, other)
    service.read(notification, user)
    assert service.updates(user)[0]["read"] is True
    # A later negative review holds the previously released artifact immediately.
    held_review = dict(data, gate="technical", decision="needs-work", scores=[])
    reviews.record(spec.canonical, ReviewSubmission.model_validate(held_review), owner)
    held_notice = service.updates(user)[0]
    assert held_notice["available"] is False and held_notice["lesson_id"] is None
    assert held_notice["title"] == "This explanation is being reviewed again"
    assert service.mine(user)[0]["status"] == "working" and service.mine(user)[0]["lesson_id"] is None
    owner_request = next(row for row in service.queue(owner) if row["id"] == key)
    assert owner_request["lesson_id"] == spec.canonical  # Triage keeps the held binding for repair.
    with pytest.raises(HTTPException):
        service.update(key, "available", spec.canonical, "", owner)
    # History and read state survive; new release evidence does not duplicate delivery.
    for gate in ("technical", "release"):
        reviews.record(spec.canonical, ReviewSubmission.model_validate(dict(data, gate=gate, scores=[])), owner)
    assert len(service.updates(user)) == 1 and service.updates(user)[0]["available"] is True
    assert service.updates(user)[0]["read"] is True
    store.transaction(lambda db: db.notifications[notification].update(spec_sha256="0" * 64))
    assert service.updates(user)[0]["available"] is False  # A mismatched receipt cannot advertise the artifact.
    store.transaction(lambda db: db.notifications[notification].update(spec_sha256=digest_spec(spec)))
    store.transaction(lambda db: db.lessons[spec.canonical].update(archived=True))
    assert service.updates(user)[0]["available"] is False


def test_demand_and_reuse_events_preserve_weekly_metrics(store: Store, settings: Settings, user: User) -> None:
    """Idempotent subscriptions count people once; real library lookups remain observable."""
    service = Interests(store, settings)
    service.request("How does a car work?", user)
    service.request("car", user)
    assert len([e for e in store.snapshot().events if e["kind"] == "requested_topic"]) == 1
    spec = aircon_concept()
    store.transaction(lambda db: db.lessons.update({spec.canonical:{"id":spec.canonical,"spec":spec.model_dump(mode="json")}}))
    result = service.request("air conditioner", user)
    assert result["kind"] == "lesson"
    state = store.snapshot()
    assert len([e for e in state.events if e["kind"] == "catalog_hit"]) == 1
    assert not state.jobs and not state.ledger and state.spent == state.reserved == 0


def test_shared_path_uses_validated_core_and_no_private_history(store: Store, user: User) -> None:
    spec = aircon_concept()
    def seed(db: Database) -> None:
        db.lessons[spec.canonical] = {"id": spec.canonical, "spec": spec.model_dump(mode="json"), "video": "synthetic.mp4"}
        db.chats["private"] = {"text": "must not appear"}
    store.transaction(seed)
    result = learning_bundle(store.snapshot(), spec.canonical, user)
    assert "must not appear" not in str(result)
    assert "The complete picture" in str(result) and "learning-path-1" in str(result)
