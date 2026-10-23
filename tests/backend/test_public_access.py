"""Public demos preserve owner authority, artifact gates and per-browser private history."""

import asyncio
import json
from dataclasses import replace

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.app import create_app
from backend.assets import Assets
from backend.auth import COOKIE, Auth
from backend.chat import Chats
from backend.contracts import AnswerSpec, LessonSpec
from backend.domain import Domain, User
from backend.learning_paths import LearningPath, PathNode
from backend.learning_reviews import LearningReviews, ReviewSubmission, review_state
from backend.native_publication import PreparedNative, import_native
from backend.native_registry import canonical_digest
from backend.path_publication import PathPublication, PathSubmission
from backend.provider import receipt_context
from backend.public_preview import PreviewSubmission, PublicPreviews, public_preview_identity
from backend.rate_limits import take_rate
from backend.settings import Settings, load_settings
from backend.starters import digest_spec
from backend.store import Database, Store

OWNER = User(id="public-preview-owner", name="Synthetic owner", owner=True)


def preview_body(artifact: PreparedNative, enabled: bool = True, bundle: str = "") -> PreviewSubmission:
    return PreviewSubmission(spec_sha256=digest_spec(artifact.spec), video_sha256=artifact.proof.video_sha256,
                             bundle_sha256=bundle, enabled=enabled)


def test_public_flag_is_explicit_and_closed_mode_stays_closed(settings: Settings, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("INSIDE_PUBLIC_ACCESS", raising=False)
    assert not load_settings().public_access
    monkeypatch.setenv("INSIDE_PUBLIC_ACCESS", "true")
    assert load_settings().public_access
    # Construct only: no network or external storage calls occur at startup.
    public_production = replace(settings, public_access=True, production=True, invite_code="",
                                database_url="postgresql://unused-synthetic", blob_token="synthetic-no-access")
    assert create_app(public_production).title == "Inside Machines"
    with pytest.raises(RuntimeError, match="durable database"):
        create_app(replace(public_production, owner_code=""))
    with TestClient(create_app(settings)) as client:
        assert client.get("/api/v1/health").json()["public_access"] is False
        assert client.get("/api/v1/lessons").status_code == 401
        assert client.post("/api/v1/auth/guest").status_code == 404


def test_guest_sessions_are_unique_reusable_private_and_do_not_downgrade_owner(
    seeded: Store, settings: Settings,
) -> None:
    config = replace(settings, public_access=True, invite_code="")
    app = create_app(config)
    with TestClient(app) as one, TestClient(app) as two:
        assert one.get("/api/v1/health").json()["public_access"] is True
        assert one.get("/api/v1/lessons").status_code == 200
        # Public read identity is not a persistent shared visitor/session.
        assert not seeded.snapshot().users and not seeded.snapshot().sessions
        first = one.post("/api/v1/auth/guest")
        second = two.post("/api/v1/auth/guest")
        assert first.status_code == second.status_code == 200
        assert "HttpOnly" in first.headers["set-cookie"] and "SameSite=strict" in first.headers["set-cookie"]
        user = first.json()
        assert user["guest"] and not user["owner"] and user["id"] != second.json()["id"]
        assert set(user) == {"id", "name", "owner", "guest"}
        assert one.post("/api/v1/auth/guest").json() == user
        assert len(seeded.snapshot().sessions) == 2
        chat = one.post("/api/v1/chats", json={"lesson_id": "washing-machine"}).json()
        assert two.get(f"/api/v1/chats/{chat['id']}").status_code == 404
        assert two.post(f"/api/v1/chats/{chat['id']}/messages", json={"question": "Private question?", "operation": "private-check"}).status_code == 404
        assert one.post("/api/v1/requests", json={"question": "How does a special new engine work?"}).json()["kind"] == "interest"
        assert not seeded.snapshot().jobs and seeded.snapshot().spent == seeded.snapshot().reserved == 0
        assert two.get("/api/v1/requests").json() == []
        for route in ("/api/v1/owner/report", "/api/v1/owner/requests", "/api/v1/owner/costs"):
            assert one.get(route).status_code == 403
        owner = one.post("/api/v1/auth/login", json={"name": "Owner", "code": config.owner_code}).json()
        assert owner["owner"] and not owner["guest"]
        assert one.post("/api/v1/auth/guest").json() == owner
        assert one.get("/api/v1/owner/report").status_code == 200
        assert one.post("/api/v1/auth/logout").status_code == 200
        assert one.get("/api/v1/auth/me").status_code == 401
        assert one.get("/api/v1/lessons").status_code == 200


def test_guest_issuance_throttle_and_recovery_use_hashed_server_address(settings: Settings, store: Store) -> None:
    config = replace(settings, public_access=True)
    auth = Auth(store, config)
    guest, token = auth.guest(None, "198.51.100.20")
    assert token and auth.guest(token, "different-network")[0] == guest
    assert "198.51.100.20" not in store.snapshot().model_dump_json()
    assert "address_hash" not in guest.model_dump()
    for _ in range(19):
        auth.guest(None, "198.51.100.20")
    before = store.snapshot()
    with pytest.raises(HTTPException) as limited:
        auth.guest(None, "198.51.100.20")
    assert limited.value.status_code == 429 and store.snapshot() == before
    assert auth.guest(None, "another-network")[0].id != guest.id
    auth.logout(token)
    assert auth.guest(token, "another-network")[0].id != guest.id
    with pytest.raises(HTTPException) as missing:
        Auth(store, replace(config, session_secret="")).guest(None, "network")
    assert missing.value.status_code == 503


def test_cookie_free_reads_and_invalid_cookie_recovery_do_not_expose_private_writes(
    seeded: Store, settings: Settings, ce_spec: LessonSpec,
) -> None:
    seeded.transaction(lambda db: db.lessons.update({ce_spec.canonical: {
        "id": ce_spec.canonical, "spec": ce_spec.model_dump(mode="json"), "video": "public-fixture.mp4"}}))
    Assets(settings).root.joinpath("public-fixture.mp4").write_bytes(b"synthetic video bytes")
    before = seeded.snapshot()
    with TestClient(create_app(replace(settings, public_access=True))) as client:
        base = f"/api/v1/lessons/{ce_spec.canonical}"
        for route in ("/api/v1/lessons", base, base + "/captions", base + "/video", base + "/checkpoint",
                      f"/api/v1/learning-paths/{ce_spec.canonical}"):
            assert client.get(route).status_code == 200
        assert seeded.snapshot() == before
        assert client.post("/api/v1/chats", json={"lesson_id": ce_spec.canonical}).status_code == 401
        client.cookies.set(COOKIE, "invalid-old-cookie")
        assert client.get(base).status_code == 200
        assert client.post("/api/v1/auth/guest").status_code == 200
        assert client.post("/api/v1/auth/guest", headers={"Origin": "https://untrusted.example"}).status_code == 403


def test_public_preview_is_explicit_reversible_and_never_release_or_activation(
    seeded: Store, native_prepared: PreparedNative, settings: Settings,
) -> None:
    artifact = native_prepared.model_copy(update={"replaces": ["washing-machine"]})
    import_native(seeded, [artifact])
    media = Assets(settings).root / artifact.video
    media.write_bytes(b"Synthetic native media API bytes, not an actual video.")
    seeded.transaction(lambda db: (db.chats.update({"kept-private": {"messages": ["PRIVATE"]}}),
                                   db.ledger.update({"kept-receipt": {"charged_usd": .17}})))
    before = seeded.snapshot()
    service = PublicPreviews(seeded)
    assert not service.status(artifact.spec.canonical, OWNER)["enabled"]
    body = preview_body(artifact)
    with TestClient(create_app(replace(settings, public_access=True))) as client:
        base = f"/api/v1/lessons/{artifact.spec.canonical}"
        assert client.get(base).status_code == 404
        client.post("/api/v1/auth/guest")
        route = f"/api/v1/owner/lessons/{artifact.spec.canonical}/public-preview"
        assert client.get(route).status_code == 403
        assert client.put(route, json=body.model_dump()).status_code == 403
        client.post("/api/v1/auth/login", json={"name": "Owner", "code": settings.owner_code})
        status = client.get(route).json()
        assert status["candidate"]["spec_sha256"] == body.spec_sha256 and "Not human-approved" in status["notice"]
        assert client.put(route, json=body.model_dump()).json()["reused"] is False
        after_permission = seeded.snapshot()
        assert client.put(route, json=body.model_dump()).json()["reused"] is True
        assert seeded.snapshot() == after_permission
        client.cookies.clear()
        lesson = client.get(base).json()
        assert lesson["public_preview"] and lesson["review_needed"] and "native_proof" not in lesson
        bundle = client.get(f"/api/v1/learning-paths/{artifact.spec.canonical}").json()
        assert bundle["lessons"][0]["public_preview"] and bundle["lessons"][0]["review_needed"]
        catalog = client.get("/api/v1/lessons").json()
        assert next(row for row in catalog if row["id"] == artifact.spec.canonical)["public_preview"]
        assert client.get(base + "/captions").status_code == 200
        assert client.get(base + "/video").content == media.read_bytes()
        media.write_bytes(b"Unexpected altered bytes")
        assert client.get(base + "/video").status_code == 404
        assert client.get(base + "/checkpoint").status_code == 422  # Native checkpoint is the real player.
        client.post("/api/v1/auth/guest")
        chat = client.post("/api/v1/chats", json={"lesson_id": artifact.spec.canonical})
        assert chat.status_code == 200
    state = seeded.snapshot()
    assert state.lessons["washing-machine"] == before.lessons["washing-machine"]
    assert state.learning_reviews == before.learning_reviews and state.ledger == before.ledger
    assert state.spent == before.spent and state.reserved == before.reserved and not state.notifications
    assert state.chats["kept-private"] == before.chats["kept-private"]
    assert not review_state(state, artifact.spec.canonical)["ready"]
    assert not state.lessons[artifact.spec.canonical].get("native_activation")
    # Revocation works using saved identity after a source/media mutation makes candidate unavailable.
    seeded.transaction(lambda db: db.lessons[artifact.spec.canonical].update(video_sha256="0" * 64))
    assert not service.status(artifact.spec.canonical, OWNER)["enabled"]
    assert service.status(artifact.spec.canonical, OWNER)["candidate"] is None
    revoke = body.model_copy(update={"enabled": False})
    assert service.set(artifact.spec.canonical, revoke, OWNER)["reused"] is False
    assert service.set(artifact.spec.canonical, revoke, OWNER)["reused"] is True
    assert not public_preview_identity(seeded.snapshot(), artifact.spec.canonical)


@pytest.mark.parametrize("change", ["spec", "video", "bundle", "proof", "rejected", "branch"])
def test_preview_rejects_changed_or_rejected_artifacts_without_fabricating_approval(
    store: Store, native_prepared: PreparedNative, change: str,
) -> None:
    import_native(store, [native_prepared])
    body = preview_body(native_prepared)
    if change in ("spec", "video", "bundle"):
        body = body.model_copy(update={change + "_sha256": "0" * 64})
    elif change == "proof":
        store.transaction(lambda db: db.lessons[native_prepared.spec.canonical].update(native_proof_sha256="0" * 64))
    elif change == "branch":
        store.transaction(lambda db: db.lessons[native_prepared.spec.canonical].update(depth_parent="different-root"))
    else:
        LearningReviews(store).record(native_prepared.spec.canonical, ReviewSubmission(
            spec_sha256=body.spec_sha256, video_sha256=body.video_sha256, gate="technical", reviewer="Synthetic review",
            method="human", decision="needs-work", evidence="A synthetic current rejection must stop public permission."), OWNER)
    before = store.snapshot()
    with pytest.raises(HTTPException) as rejected:
        PublicPreviews(store).set(native_prepared.spec.canonical, body, OWNER)
    assert rejected.value.status_code == 409 and store.snapshot() == before


def native_pair(artifact: PreparedNative) -> tuple[PreparedNative, LearningPath]:
    """Add a synthetic registered leaf; never use or approve actual topic artwork."""
    import backend.native_registry as registry

    leaf = artifact.model_copy(deep=True)
    leaf.spec.canonical = "synthetic-public-insight"
    manifest = json.loads(registry.REGISTRY_FILE.read_text())
    identity = {"id": "synthetic-public-2", "lessons": [leaf.spec.canonical], "sources": manifest["renderers"][0]["sources"]}
    leaf.spec.renderer.id = str(identity["id"])
    leaf.spec.renderer.fingerprint = canonical_digest(identity)
    leaf.proof.renderer_id = leaf.spec.renderer.id
    leaf.proof.renderer_fingerprint = leaf.spec.renderer.fingerprint
    leaf.proof.spec_sha256 = digest_spec(leaf.spec)
    manifest["renderers"].append({**identity, "fingerprint": leaf.spec.renderer.fingerprint,
                                  "spec_sha256": {leaf.spec.canonical: digest_spec(leaf.spec)}})
    registry.REGISTRY_FILE.write_text(json.dumps(manifest))
    path = LearningPath(schema_version="learning-path-1", id="synthetic-public-path", title="Synthetic native public fixture",
                        example="A synthetic source-bound graph.", entry="core", nodes=[
                            PathNode(id="core", role="core", label="Core fixture", question=artifact.spec.question,
                                     outcome=artifact.spec.teaching.goal, lesson_id=artifact.spec.canonical,
                                     prerequisites=[], next=["insight"], queries=["core"]),
                            PathNode(id="insight", role="insight", label="Insight fixture", question=leaf.spec.question,
                                     outcome=leaf.spec.teaching.goal, lesson_id=leaf.spec.canonical,
                                     prerequisites=["core"], next=[], queries=["insight"]),
                        ])
    return leaf, path


@pytest.mark.parametrize("import_bound", [True, False])
def test_public_preview_pins_every_depth_artifact_and_revokes_the_entire_bundle(
    store: Store, native_prepared: PreparedNative, settings: Settings, import_bound: bool,
) -> None:
    leaf, path = native_pair(native_prepared)
    import_native(store, [native_prepared, leaf], path if import_bound else None)
    attached = PathPublication(store).attach(native_prepared.spec.canonical, PathSubmission(path=path, allow_review_drafts=True), OWNER)
    body = preview_body(native_prepared, bundle=str(attached["bundle_sha256"]))
    PublicPreviews(store).set(native_prepared.spec.canonical, body, OWNER)
    with TestClient(create_app(replace(settings, public_access=True))) as client:
        root_url = f"/api/v1/lessons/{native_prepared.spec.canonical}"
        leaf_url = f"/api/v1/lessons/{leaf.spec.canonical}"
        assert client.get(root_url).status_code == client.get(leaf_url).status_code == 200
        bundle_url = f"/api/v1/learning-paths/{native_prepared.spec.canonical}"
        assert len(client.get(bundle_url).json()["lessons"]) == 2
        store.transaction(lambda db: db.lessons[leaf.spec.canonical].update(video_sha256="0" * 64))
        assert client.get(root_url).status_code == client.get(leaf_url).status_code == client.get(bundle_url).status_code == 404
        PublicPreviews(store).set(native_prepared.spec.canonical, body.model_copy(update={"enabled": False}), OWNER)
        assert not public_preview_identity(store.snapshot(), leaf.spec.canonical)


async def test_guest_chat_budget_and_network_throttle_preserve_accounting(
    seeded: Store, settings: Settings,
) -> None:
    config = replace(settings, public_access=True, budget_usd=settings.chat_reserve)
    auth = Auth(seeded, config)
    first, _ = auth.guest(None, "same-network")
    second, _ = auth.guest(None, "same-network")
    began, finish = asyncio.Event(), asyncio.Event()
    calls = 0

    async def answer(prompt: str, current: Settings) -> str:
        nonlocal calls
        calls += 1
        began.set()
        await finish.wait()
        receipt = receipt_context.get()
        assert receipt is not None
        receipt.models.append("synthetic-guest-chat")
        receipt.cost_usd = .003
        return AnswerSpec(answer="A synthetic bounded explanation.", stage=None, part=None, source_indices=[0], uncertain=False).model_dump_json()

    chats = Chats(seeded, config, answer)
    one, two = chats.create("washing-machine", first), chats.create("washing-machine", second)
    running = asyncio.create_task(chats.ask(one.id, "Explain the input?", "guest-budget-one", first))
    await began.wait()
    assert seeded.snapshot().reserved == config.chat_reserve
    with pytest.raises(HTTPException) as budget:
        await chats.ask(two.id, "Explain this too?", "guest-budget-two", second)
    assert budget.value.status_code == 429
    finish.set()
    assert len((await running).messages) == 2 and calls == 1
    assert seeded.snapshot().spent == .003 and seeded.snapshot().reserved == 0
    before = seeded.snapshot()
    assert len((await chats.ask(one.id, "Explain the input?", "guest-budget-one", first)).messages) == 2
    assert seeded.snapshot() == before and calls == 1
    address_hash = str(seeded.snapshot().users[first.id]["address_hash"])

    def block_network(db: Database) -> None:
        # Dedicated counters, rather than disposable observation events, enforce admission.
        for _ in range(11):
            take_rate(db, "chat-network", address_hash, 12, "Synthetic network quota")

    seeded.transaction(block_network)
    with pytest.raises(HTTPException) as limited:
        await Chats(seeded, replace(config, budget_usd=50), answer).ask(two.id, "One more input?", "guest-throttled", second)
    assert limited.value.status_code == 429 and calls == 1 and seeded.snapshot().reserved == 0
    with pytest.raises(HTTPException) as build:
        Domain(seeded, config).request("How does a new machine work?", first)
    assert build.value.status_code == 403 and not seeded.snapshot().jobs


def test_public_guest_cannot_read_other_jobs_or_owner_sse(seeded: Store, settings: Settings) -> None:
    seeded.transaction(lambda db: db.jobs.update({"private-owner-job": {"id": "private-owner-job", "user_id": OWNER.id,
                                                                       "status": "complete", "phase": "done"}}))
    with TestClient(create_app(replace(settings, public_access=True))) as client:
        client.post("/api/v1/auth/guest")
        assert client.get("/api/v1/jobs/private-owner-job").status_code == 404
        assert client.get("/api/v1/jobs/private-owner-job/events").status_code == 404
        user = client.get("/api/v1/auth/me").json()
        seeded.transaction(lambda db: db.jobs["private-owner-job"].update(user_id=user["id"]))
        assert client.get("/api/v1/jobs/private-owner-job").status_code == 200
        assert "event: progress" in client.get("/api/v1/jobs/private-owner-job/events").text


@pytest.mark.parametrize("gate", ["technical", "craft"])
def test_same_artifact_rejection_survives_recomposition_and_revokes_existing_preview(
    store: Store, native_prepared: PreparedNative, gate: str,
) -> None:
    """Changing a graph cannot launder a truth/craft rejection of unchanged artwork."""
    import_native(store, [native_prepared])
    root_id = native_prepared.spec.canonical
    standalone = preview_body(native_prepared)

    def verdict(decision: str, bundle: str = "") -> None:
        LearningReviews(store).record(root_id, ReviewSubmission.model_validate({
            "spec_sha256": standalone.spec_sha256, "video_sha256": standalone.video_sha256,
            "bundle_sha256": bundle, "gate": gate, "reviewer": "Synthetic protocol reviewer",
            "method": "human", "decision": decision, "independent": True,
            "real_device": True, "device": "Synthetic test phone", "evidence": "Synthetic gate test; no real artifact review occurred.",
        }), OWNER)

    verdict("needs-work")
    path = LearningPath(schema_version="learning-path-1", id="same-artifact-path", title="Synthetic recomposition",
                        example="Same artifact, same media, new graph identity.", entry="core", nodes=[
                            PathNode(id="core", role="core", label="Core fixture", question=native_prepared.spec.question,
                                     outcome=native_prepared.spec.teaching.goal, lesson_id=root_id,
                                     prerequisites=[], next=[], queries=["core"]),
                        ])
    attached = PathPublication(store).attach(root_id, PathSubmission(path=path, allow_review_drafts=True), OWNER)
    body = preview_body(native_prepared, bundle=str(attached["bundle_sha256"]))
    before = store.snapshot()
    assert PublicPreviews(store).status(root_id, OWNER)["candidate"] is None
    with pytest.raises(HTTPException) as rejected:
        PublicPreviews(store).set(root_id, body, OWNER)
    assert rejected.value.status_code == 409 and store.snapshot() == before
    # Only an explicit later same-artifact verdict resolves the rejected gate.
    verdict("pass", body.bundle_sha256)
    PublicPreviews(store).set(root_id, body, OWNER)
    assert public_preview_identity(store.snapshot(), root_id)
    assert not review_state(store.snapshot(), root_id)["ready"]
    verdict("needs-work", body.bundle_sha256)
    assert not public_preview_identity(store.snapshot(), root_id)
    changed_path = path.model_copy(update={"id": "another-same-artifact-path"})
    next_bundle = PathPublication(store).attach(root_id, PathSubmission(
        path=changed_path, allow_review_drafts=True, expected_bundle_sha256=body.bundle_sha256), OWNER)
    with pytest.raises(HTTPException):
        PublicPreviews(store).set(root_id, preview_body(native_prepared, bundle=str(next_bundle["bundle_sha256"])), OWNER)
    assert len(store.snapshot().learning_reviews) == 3
