"""Synthetic release evidence tests graph transactions, never real teaching quality."""

from concurrent.futures import ThreadPoolExecutor
from typing import Literal, cast

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.app import create_app
from backend.contracts import LessonSpec
from backend.domain import User
from backend.interests import Interests
from backend.learning_bundle import learning_bundle
from backend.learning_paths import LearningPath, PathNode
from backend.learning_reviews import LearningReviews, ReviewSubmission, review_state
from backend.path_publication import PathPublication, PathSubmission
from backend.settings import Settings
from backend.starters import digest_spec
from backend.store import Database, Store

OWNER = User(id="synthetic-owner", name="Synthetic owner", owner=True)


def _release(store: Store, lesson_id: str, bundle: str = "", gates: tuple[str, ...] = ("engineering", "technical", "craft", "learning", "release")) -> None:
    """Record explicit protocol fixtures, without pretending a real person reviewed them."""
    spec = LessonSpec.model_validate(store.snapshot().lessons[lesson_id]["spec"])
    for gate in gates:
        data: dict[str, object] = {
            "spec_sha256": digest_spec(spec), "video_sha256": "0" * 64, "bundle_sha256": bundle,
            "gate": gate, "reviewer": "Synthetic graph protocol fixture", "method": "human",
            "decision": "pass", "evidence": "Synthetic transaction fixture; not a real technical or beginner-learning review.",
            "independent": True, "real_device": True, "device": "Synthetic phone",
        }
        if gate == "learning":
            data["scores"] = [{"participant": f"anon-{i}", "baseline": 0, "causal": 2, "transfer": 2} for i in range(5)]
        LearningReviews(store).record(lesson_id, ReviewSubmission.model_validate(data), OWNER)


def _prepared(store: Store, ce_spec: LessonSpec) -> dict[str, LessonSpec]:
    examples = {}
    for role in ("core", "insight", "model"):
        spec = ce_spec.model_copy(deep=True)
        spec.canonical, spec.title = f"synthetic-{role}", f"Synthetic {role} fixture"
        examples[role] = spec

    def seed(db: Database) -> None:
        for spec in examples.values():
            db.lessons[spec.canonical] = {
                "id": spec.canonical, "spec": spec.model_dump(mode="json"),
                "video": "synthetic.mp4", "video_sha256": "0" * 64,
            }
        db.chats["private"] = {"messages": [{"text": "PRIVATE CHAT"}], "user_id": "PRIVATE USER"}

    store.transaction(seed)
    for spec in examples.values():
        _release(store, spec.canonical)
    return examples


def _path(examples: dict[str, LessonSpec], title: str = "Synthetic working system") -> LearningPath:
    roles: tuple[Literal["core", "insight", "model"], ...] = ("core", "insight", "model")
    return LearningPath(
        schema_version="learning-path-1", id="synthetic-path", title=title,
        example="Follow the same synthetic working system into two existing branches.", entry="core",
        nodes=[PathNode(
            id=role, role=role, label=f"The {role} explanation",
            question=f"What does the synthetic {role} explain?", outcome=f"Understand the declared {role} relationship.",
            lesson_id=examples[role].canonical, prerequisites=[roles[index-1]] if index else [],
            next=[roles[index+1]] if index+1 < len(roles) else [], queries=[role],
        ) for index, role in enumerate(roles)],
    )


def test_composition_holds_old_release_and_notifies_only_current_bundle(
    store: Store, settings: Settings, ce_spec: LessonSpec, user: User
) -> None:
    examples = _prepared(store, ce_spec)
    root_id = examples["core"].canonical
    interests = Interests(store, settings)
    topic = interests.request("Synthetic topic-interest fixture", user)
    interests.update(str(topic["interest_id"]), "working", root_id, "Synthetic binding", OWNER)
    assert len(interests.updates(user)) == 1
    before = store.snapshot()
    publisher = PathPublication(store)
    result = publisher.attach(root_id, PathSubmission(path=_path(examples)), OWNER)
    bundle = str(result["bundle_sha256"])
    state = review_state(store.snapshot(), root_id)
    assert result["review_required"] is True and len(bundle) == 64 and not state["ready"]
    assert state["records"] == [] and state["bundle_sha256"] == bundle
    assert interests.updates(user)[0]["available"] is False
    with pytest.raises(HTTPException) as stale:
        _release(store, root_id, gates=("engineering",))
    assert stale.value.status_code == 409
    _release(store, root_id, bundle)
    assert review_state(store.snapshot(), root_id)["ready"]
    notices = interests.updates(user)
    assert len(notices) == 2 and sum(bool(n["available"]) for n in notices) == 1
    _release(store, root_id, bundle, gates=("release",))
    assert len(interests.updates(user)) == 2
    envelope = learning_bundle(store.snapshot(), root_id, user)
    assert envelope["bundle_sha256"] == bundle and "PRIVATE" not in str(envelope)
    after = store.snapshot()
    assert before.chats == after.chats and before.ledger == after.ledger
    for lesson_id, record in before.lessons.items():
        assert after.lessons[lesson_id]["spec"] == record["spec"]
    assert not after.jobs and after.spent == after.reserved == 0


def test_path_history_is_immutable_and_concurrent_edits_need_current_pointer(
    store: Store, ce_spec: LessonSpec
) -> None:
    examples = _prepared(store, ce_spec)
    root_id = examples["core"].canonical
    service = PathPublication(store)
    first = service.attach(root_id, PathSubmission(path=_path(examples)), OWNER)
    first_sha = str(first["bundle_sha256"])
    _release(store, root_id, first_sha)
    saved = store.snapshot().learning_paths[first_sha]
    changed = _path(examples, "A corrected graph explanation")
    with pytest.raises(HTTPException) as stale:
        service.attach(root_id, PathSubmission(path=changed), OWNER)
    assert stale.value.status_code == 409 and len(store.snapshot().learning_paths) == 1
    second = service.attach(root_id, PathSubmission(path=changed, expected_bundle_sha256=first_sha), OWNER)
    assert second["bundle_sha256"] != first_sha and second["review_required"] is True
    assert store.snapshot().learning_paths[first_sha] == saved
    restored = service.attach(root_id, PathSubmission(path=_path(examples), expected_bundle_sha256=str(second["bundle_sha256"])), OWNER)
    assert restored["reused"] is True and restored["review_required"] is False
    assert len(cast(list[object], service.history(root_id, OWNER)["records"])) == 2
    assert "PRIVATE" not in str(service.history(root_id, OWNER)) and "created_by" not in str(service.history(root_id, OWNER))


@pytest.mark.parametrize("tamper", ["video", "path"])
def test_branch_revocation_or_artifact_change_holds_composite(
    store: Store, ce_spec: LessonSpec, user: User, tamper: str
) -> None:
    examples = _prepared(store, ce_spec)
    root_id, branch_id = examples["core"].canonical, examples["insight"].canonical
    result = PathPublication(store).attach(root_id, PathSubmission(path=_path(examples)), OWNER)
    bundle = str(result["bundle_sha256"])
    _release(store, root_id, bundle)
    rejected = ReviewSubmission(
        spec_sha256=digest_spec(examples["insight"]), video_sha256="0" * 64,
        gate="technical", reviewer="Synthetic review fixture", method="human", decision="needs-work",
        evidence="Synthetic branch rejection, not an actual domain evaluation.",
    )
    LearningReviews(store).record(branch_id, rejected, OWNER)
    assert not review_state(store.snapshot(), root_id)["ready"]
    with pytest.raises(HTTPException):
        _release(store, root_id, bundle, gates=("release",))
    _release(store, branch_id, gates=("technical", "release"))
    assert review_state(store.snapshot(), root_id)["ready"]
    def mutate(db: Database) -> None:
        if tamper == "video":
            db.lessons[branch_id]["video_sha256"] = "1" * 64
        else:
            cast(dict[str, object], db.learning_paths[bundle]["path"])["title"] = "Tampered graph content"
    store.transaction(mutate)
    assert review_state(store.snapshot(), root_id)["bundle_issues"]
    with pytest.raises(HTTPException) as held:
        learning_bundle(store.snapshot(), root_id, user)
    assert held.value.status_code == 409
    with pytest.raises(HTTPException):
        _release(store, root_id, bundle, gates=("engineering",))


def test_path_write_rejects_unreleased_unknown_duplicate_and_wrong_core(
    store: Store, ce_spec: LessonSpec, user: User
) -> None:
    examples = _prepared(store, ce_spec)
    service = PathPublication(store)
    root_id = examples["core"].canonical
    path = _path(examples)
    with pytest.raises(HTTPException):
        service.attach(root_id, PathSubmission(path=path), user)
    with pytest.raises(HTTPException):
        service.history(root_id, user)
    with pytest.raises(HTTPException) as wrong:
        service.attach(examples["insight"].canonical, PathSubmission(path=path), OWNER)
    assert wrong.value.status_code == 422
    for field, value in (("lesson_id", "unknown"), ("lesson_id", root_id)):
        data = path.model_dump(mode="json")
        nodes = cast(list[dict[str, object]], data["nodes"])
        nodes[-1][field] = value
        with pytest.raises(HTTPException) as invalid:
            service.attach(root_id, PathSubmission.model_validate({"path": data}), OWNER)
        assert invalid.value.status_code == 422
    before_reviews = store.snapshot().learning_reviews
    store.transaction(lambda db: setattr(db, "learning_reviews", [row for row in db.learning_reviews if row["lesson_id"] != examples["insight"].canonical]))
    with pytest.raises(HTTPException) as unreleased:
        service.attach(root_id, PathSubmission(path=path), OWNER)
    assert unreleased.value.status_code == 409
    store.transaction(lambda db: setattr(db, "learning_reviews", before_reviews))
    store.transaction(lambda db: db.lessons[examples["insight"].canonical].update(learning_bundle_sha256="a" * 64))
    with pytest.raises(HTTPException) as nested:
        service.attach(root_id, PathSubmission(path=path), OWNER)
    assert nested.value.status_code == 422
    store.transaction(lambda db: db.lessons[examples["insight"].canonical].pop("learning_bundle_sha256"))
    store.transaction(lambda db: db.lessons[examples["insight"].canonical].update(archived=True))
    with pytest.raises(HTTPException) as archived:
        service.attach(root_id, PathSubmission(path=path), OWNER)
    assert archived.value.status_code == 409 and not store.snapshot().learning_paths


def test_concurrent_same_composition_is_idempotent(store: Store, ce_spec: LessonSpec) -> None:
    examples = _prepared(store, ce_spec)
    root_id = examples["core"].canonical
    service, submission = PathPublication(store), PathSubmission(path=_path(examples))
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: service.attach(root_id, submission, OWNER), range(16)))
    assert len({r["bundle_sha256"] for r in results}) == 1
    db = store.snapshot()
    assert len(db.learning_paths) == 1 and not db.jobs and not db.ledger and db.spent == db.reserved == 0


def test_explicit_review_draft_can_preview_but_cannot_release_unapproved_branches(
    store: Store, ce_spec: LessonSpec, user: User
) -> None:
    """Whole-path review can precede leaf approval without fabricating that approval."""
    examples = _prepared(store, ce_spec)
    store.transaction(lambda db: db.learning_reviews.clear())
    service, root_id = PathPublication(store), examples["core"].canonical
    path = _path(examples)
    branch_id = examples["insight"].canonical
    def replace_field(field: str, value: object) -> None:
        store.transaction(lambda db: db.lessons[branch_id].update({field: value}))
    for field, value in (("video", None), ("video_sha256", "")):
        previous = store.snapshot().lessons[branch_id][field]
        replace_field(field, value)
        with pytest.raises(HTTPException) as missing_media:
            service.attach(root_id, PathSubmission(path=path, allow_review_drafts=True), OWNER)
        assert missing_media.value.status_code == 409
        replace_field(field, previous)
    broken = examples["insight"].model_copy(deep=True)
    next(part for part in broken.parts if part.id.startswith("label-")).h = 20
    store.transaction(lambda db: db.lessons[branch_id].update(spec=broken.model_dump(mode="json")))
    with pytest.raises(HTTPException) as structural:
        service.attach(root_id, PathSubmission(path=path, allow_review_drafts=True), OWNER)
    assert structural.value.status_code == 409
    store.transaction(lambda db: db.lessons[branch_id].update(spec=examples["insight"].model_dump(mode="json")))
    with pytest.raises(HTTPException):
        service.attach(root_id, PathSubmission(path=path), OWNER)
    result = service.attach(root_id, PathSubmission(path=path, allow_review_drafts=True), OWNER)
    bundle = str(result["bundle_sha256"])
    state = review_state(store.snapshot(), root_id)
    assert result["review_required"] is True and not state["can_release"] and not state["branches_ready"]
    envelope = learning_bundle(store.snapshot(), root_id, user)
    assert len(cast(list[object], envelope["lessons"])) == 3
    assert all(row["review_needed"] for row in cast(list[dict[str, object]], envelope["lessons"]))
    assert not store.snapshot().learning_reviews
    with pytest.raises(HTTPException):
        _release(store, root_id, bundle)  # The final release is held despite four bundle gates.
    assert not review_state(store.snapshot(), root_id)["ready"]
    for role in ("insight", "model"):
        _release(store, examples[role].canonical)
    _release(store, root_id, bundle, gates=("release",))
    assert review_state(store.snapshot(), root_id)["ready"]
    assert not store.snapshot().jobs and not store.snapshot().ledger


def test_legacy_embedded_path_is_preserved_but_cannot_keep_standalone_approval(
    store: Store, ce_spec: LessonSpec, user: User
) -> None:
    examples = _prepared(store, ce_spec)
    root_id, path = examples["core"].canonical, _path(examples)
    store.transaction(lambda db: db.lessons[root_id].update(learning_path=path.model_dump(mode="json")))
    assert learning_bundle(store.snapshot(), root_id, user)["path"] == path.model_dump(mode="json")
    assert not review_state(store.snapshot(), root_id)["ready"]
    PathPublication(store).attach(root_id, PathSubmission(path=path), OWNER)
    assert store.snapshot().lessons[root_id]["learning_path"] == path.model_dump(mode="json")


def test_owner_route_rejects_private_fields_and_cycles(settings: Settings, ce_spec: LessonSpec) -> None:
    app = create_app(settings)
    store = cast(Store, app.state.store)
    examples = _prepared(store, ce_spec)
    root_id, path = examples["core"].canonical, _path(examples)
    url = f"/api/v1/owner/lessons/{root_id}/learning-paths"
    with TestClient(app) as client:
        assert client.get(url).status_code == 401
        client.post("/api/v1/auth/login", json={"name": "Family", "code": settings.invite_code})
        assert client.post(url, json={"path": path.model_dump(mode="json")}).status_code == 403
        client.post("/api/v1/auth/login", json={"name": "Owner", "code": settings.owner_code})
        assert client.post(url, json={"path": path.model_dump(mode="json"), "private_chat": "PRIVATE"}).status_code == 422
        data = path.model_dump(mode="json")
        cast(list[dict[str, object]], data["nodes"])[-1]["next"] = ["core"]
        assert client.post(url, json={"path": data}).status_code == 422
        with pytest.raises(ValidationError):
            PathSubmission.model_validate({"path": path.model_dump(mode="json"), "provider_endpoint": "https://private.invalid"})
        result = client.post(url, json={"path": path.model_dump(mode="json")})
        assert result.status_code == 200 and result.json()["review_required"] is True
        history = client.get(url)
        assert history.status_code == 200 and len(history.json()["records"]) == 1
        assert "PRIVATE" not in history.text and "created_by" not in history.text
