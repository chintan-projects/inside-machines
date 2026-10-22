"""Optional real Postgres tests, restricted to the disposable local test container."""

import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Lock
from urllib.parse import urlparse

import psycopg
import pytest

from backend.contracts import LessonSpec
from backend.domain import Domain, User
from backend.native_publication import PreparedNative
from backend.research import ResearchSpec
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


def test_postgres_native_activation_concurrency_preserves_exact_artifacts(
    settings: Settings, native_prepared: PreparedNative, spec: LessonSpec, user: User,
) -> None:
    """An explicit adoption commits once under contention; stale proof cannot partially archive."""
    from fastapi import HTTPException

    from backend.interests import Interests
    from backend.learning_reviews import LearningReviews, ReviewSubmission
    from backend.native_activation import NativeActivation, NativeActivationBody
    from backend.native_publication import import_native
    from backend.starters import digest_spec

    target = urlparse(URL)
    if target.hostname != "127.0.0.1" or target.port != 55432 or target.path != "/inside_test":
        pytest.fail("Native activation tests require disposable loopback Postgres")
    with psycopg.connect(URL) as connection:
        connection.execute("DROP TABLE IF EXISTS inside_state")
    store = Store(URL, settings.data_dir)
    store.transaction(lambda db: (db.lessons.update({spec.canonical: {"id": spec.canonical, "spec": spec.model_dump(mode="json")}}),
                                 db.chats.update({"private-old": {"lesson_id": spec.canonical, "messages": ["PRIVATE FIXTURE"]}})))
    import_native(store, [native_prepared])
    owner = User(id="synthetic-native-activation-owner", name="Synthetic owner", owner=True)
    body = NativeActivationBody(spec_sha256=digest_spec(native_prepared.spec), video_sha256=native_prepared.proof.video_sha256,
                                bundle_sha256="", expected_old_ids=[spec.canonical])
    for gate in ("engineering", "technical", "craft", "learning", "release"):
        data: dict[str, object] = {
            "spec_sha256": body.spec_sha256, "video_sha256": body.video_sha256, "gate": gate,
            "reviewer": "Synthetic protocol fixture", "method": "human", "decision": "pass",
            "evidence": "Entirely synthetic test evidence; no actual review, learners or device inspection.",
            "independent": True, "real_device": True, "device": "Synthetic fixture phone",
        }
        if gate == "learning":
            data["scores"] = [{"participant": f"anon-{i}", "baseline": 0, "causal": 2, "transfer": 2} for i in range(5)]
        LearningReviews(store).record(native_prepared.spec.canonical, ReviewSubmission.model_validate(data), owner)
    before = store.snapshot()
    with pytest.raises(HTTPException):
        NativeActivation(store).activate(native_prepared.spec.canonical, body.model_copy(
            update={"expected_old_ids": [spec.canonical, "missing-head"]}), owner)
    assert store.snapshot() == before
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: NativeActivation(store).activate(native_prepared.spec.canonical, body, owner), range(16)))
    assert sum(result["reused"] is False for result in results) == 1
    after = store.snapshot()
    assert after.lessons[spec.canonical] == {**before.lessons[spec.canonical], "archived": True,
                                            "superseded_by": native_prepared.spec.canonical}
    assert after.chats == before.chats and after.learning_reviews == before.learning_reviews
    assert after.ledger == before.ledger and after.spent == after.reserved == 0 and not after.jobs
    assert Interests(store, settings).request("How does a washer work?", user)["lesson_id"] == native_prepared.spec.canonical


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


def test_postgres_interest_release_and_notifications_are_atomic(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Race real writes; a failed release must roll back its notices and review together.

    Every reviewer/learner below is an explicit protocol fixture. These records
    exercise database semantics and do not approve a real lesson for release.
    """
    from backend.ac_concept import aircon_concept
    from backend.interests import Interests, notify_available
    from backend.learning_reviews import LearningReviews, ReviewSubmission, review_state
    from backend.starters import digest_spec

    target = urlparse(URL)
    if target.hostname != "127.0.0.1" or target.port != 55432 or target.path != "/inside_test":
        pytest.fail("Interest tests require disposable loopback Postgres")
    with psycopg.connect(URL) as connection:
        connection.execute("DROP TABLE IF EXISTS inside_state")
    store = Store(URL, settings.data_dir)
    service, reviews = Interests(store, settings), LearningReviews(store)
    owner = User(id="synthetic-owner", name="Synthetic owner", owner=True)
    members = [User(id=f"synthetic-member-{i}", name="Synthetic requester", owner=False) for i in range(16)]
    question = "Synthetic curated-release protocol fixture"
    with ThreadPoolExecutor(max_workers=8) as pool:
        requests = list(pool.map(lambda member: service.request(question, member), members * 2))
    keys = {str(result["interest_id"]) for result in requests}
    assert len(keys) == 1
    key = keys.pop()
    initial = store.snapshot()
    assert len(initial.topic_interests) == 1 and not initial.jobs and not initial.ledger
    assert initial.spent == initial.reserved == 0
    assert service.queue(owner)[0]["requesters"] == 16
    spec = aircon_concept()

    def seed(db: Database) -> None:
        db.lessons[spec.canonical] = {
            "id": spec.canonical, "spec": spec.model_dump(mode="json"),
            "video": "synthetic.mp4", "video_sha256": "a" * 64,
        }
        db.chats["retained-private"] = {"messages": [{"text": "PRIVATE fixture content"}]}

    store.transaction(seed)
    service.update(key, "working", spec.canonical, "Synthetic binding, not a real teaching release", owner)

    def submission(gate: str, decision: str = "pass") -> ReviewSubmission:
        data: dict[str, object] = {
            "spec_sha256": digest_spec(spec), "video_sha256": "a" * 64,
            "gate": gate, "reviewer": "Synthetic database protocol fixture", "method": "human",
            "decision": decision, "evidence": "Synthetic transaction evidence; no actual reviewer or learner session.",
            "independent": True, "real_device": True, "device": "Synthetic phone fixture",
        }
        if gate == "learning":
            data["scores"] = [
                {"participant": f"anon-{i}", "baseline": 0, "causal": 2, "transfer": 2} for i in range(5)
            ]
        return ReviewSubmission.model_validate(data)

    for gate in ("engineering", "technical", "craft", "learning"):
        reviews.record(spec.canonical, submission(gate), owner)
    before = store.snapshot()

    def fail_after_notifications(db: Database, lesson_id: str) -> None:
        notify_available(db, lesson_id)
        assert len(db.notifications) == 16
        raise RuntimeError("Synthetic failure after notice creation")

    monkeypatch.setattr("backend.interests.notify_available", fail_after_notifications)
    with pytest.raises(RuntimeError, match="Synthetic failure"):
        reviews.record(spec.canonical, submission("release"), owner)
    rolled_back = store.snapshot()
    assert rolled_back.learning_reviews == before.learning_reviews and not rolled_back.notifications
    assert not review_state(rolled_back, spec.canonical)["ready"]
    monkeypatch.setattr("backend.interests.notify_available", notify_available)

    def release(_iteration: int) -> None:
        reviews.record(spec.canonical, submission("release"), owner)
        observed = store.snapshot()
        assert review_state(observed, spec.canonical)["ready"]
        assert len(observed.notifications) == 16  # No connection sees a partial fan-out.

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(release, range(16)))
    released = store.snapshot()
    assert len(released.notifications) == 16
    assert all(len(service.updates(member)) == 1 for member in members)
    first = service.updates(members[0])[0]
    assert first["available"] is True and "PRIVATE" not in str(first)
    service.read(str(first["id"]), members[0])
    reviews.record(spec.canonical, submission("technical", "needs-work"), owner)
    assert all(service.updates(member)[0]["available"] is False for member in members)
    reviews.record(spec.canonical, submission("technical"), owner)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(release, range(4)))
    final = store.snapshot()
    assert len(final.notifications) == 16 and service.updates(members[0])[0]["read"] is True
    assert final.chats == before.chats and final.lessons == before.lessons
    assert not final.jobs and not final.ledger and final.spent == final.reserved == 0


def test_postgres_path_attachment_rolls_back_and_serializes_edits(
    settings: Settings, ce_spec: LessonSpec, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Real transactions pin a path and pointer together; concurrent edits cannot overwrite."""
    from backend.learning_paths import LearningPath, PathNode
    from backend.learning_reviews import LearningReviews, ReviewSubmission, review_state
    from backend.path_publication import PathPublication, PathSubmission
    from backend.starters import digest_spec

    target = urlparse(URL)
    if target.hostname != "127.0.0.1" or target.port != 55432 or target.path != "/inside_test":
        pytest.fail("Path tests require disposable loopback Postgres")
    with psycopg.connect(URL) as connection:
        connection.execute("DROP TABLE IF EXISTS inside_state")
    store = Store(URL, settings.data_dir)
    owner = User(id="synthetic-owner", name="Synthetic owner", owner=True)
    specs: list[LessonSpec] = []
    for suffix in ("core", "insight"):
        spec = ce_spec.model_copy(deep=True)
        spec.canonical = f"pg-path-{suffix}"
        specs.append(spec)
    store.transaction(lambda db: db.lessons.update({
        spec.canonical: {"id": spec.canonical, "spec": spec.model_dump(mode="json"),
                         "video": "synthetic.mp4", "video_sha256": "0" * 64} for spec in specs
    }))
    reviews = LearningReviews(store)
    for spec in specs:
        for gate in ("engineering", "technical", "craft", "learning", "release"):
            data: dict[str, object] = {
                "spec_sha256": digest_spec(spec), "video_sha256": "0" * 64, "gate": gate,
                "reviewer": "Synthetic path database fixture", "method": "human", "decision": "pass",
                "evidence": "Synthetic transaction fixture; no real technical or learning review occurred.",
                "independent": True, "real_device": True, "device": "Synthetic phone",
            }
            if gate == "learning":
                data["scores"] = [{"participant": f"anon-{i}", "baseline": 0, "causal": 2, "transfer": 2} for i in range(5)]
            reviews.record(spec.canonical, ReviewSubmission.model_validate(data), owner)
    root_id = specs[0].canonical
    path = LearningPath(
        schema_version="learning-path-1", id="pg-synthetic-path", title="Synthetic graph fixture",
        example="A synthetic core and a separately reviewed branch.", entry="core", nodes=[
            PathNode(id="core", role="core", label="Core explanation", question="What happens in the synthetic core?",
                     outcome="Understand the synthetic causal mechanism.", lesson_id=root_id,
                     prerequisites=[], next=["insight"], queries=["core"]),
            PathNode(id="insight", role="insight", label="Existing insight", question="Why does this synthetic relationship matter?",
                     outcome="Understand the existing insight relationship.", lesson_id=specs[1].canonical,
                     prerequisites=["core"], next=[], queries=["insight"]),
        ],
    )
    service = PathPublication(store)
    before = store.snapshot()

    def fail_after_attach(db: Database, lesson_id: str) -> dict[str, object]:
        if lesson_id == root_id and db.lessons[root_id].get("learning_bundle_sha256"):
            assert len(db.learning_paths) == 1
            raise RuntimeError("Synthetic failure after path and pointer write")
        return review_state(db, lesson_id)

    monkeypatch.setattr("backend.learning_reviews.review_state", fail_after_attach)
    with pytest.raises(RuntimeError, match="Synthetic failure"):
        service.attach(root_id, PathSubmission(path=path), owner)
    assert store.snapshot() == before
    monkeypatch.setattr("backend.learning_reviews.review_state", review_state)

    def attach(index: int) -> str:
        from fastapi import HTTPException
        candidate = path.model_copy(update={"title": f"Synthetic graph variant {index % 2}"})
        try:
            return str(service.attach(root_id, PathSubmission(path=candidate), owner)["bundle_sha256"])
        except HTTPException as error:
            assert error.status_code == 409
            return "held-concurrent-edit"

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(attach, range(16)))
    identities = {identity for identity in results if identity != "held-concurrent-edit"}
    assert len(identities) == 1 and "held-concurrent-edit" in results
    final = store.snapshot()
    assert len(final.learning_paths) == 1 and final.lessons[root_id]["learning_bundle_sha256"] in identities
    assert not review_state(final, root_id)["ready"]
    assert final.learning_reviews == before.learning_reviews and final.ledger == before.ledger
    assert all(final.lessons[spec.canonical]["spec"] == before.lessons[spec.canonical]["spec"] for spec in specs)
    assert not final.jobs and final.spent == final.reserved == 0


def test_postgres_depth_draft_concurrency_keeps_root_and_one_reservation(
    settings: Settings, ce_spec: LessonSpec, evidence: ResearchSpec,
) -> None:
    """A new branch atomically reserves once without changing its core/private history."""
    from fastapi import HTTPException

    from backend.depth_authoring import job_depth_context

    target = urlparse(URL)
    if target.hostname != "127.0.0.1" or target.port != 55432 or target.path != "/inside_test":
        pytest.fail("Depth tests require disposable loopback Postgres")
    with psycopg.connect(URL) as connection:
        connection.execute("DROP TABLE IF EXISTS inside_state")
    store = Store(URL, settings.data_dir)
    owner = User(id="synthetic-depth-owner", name="Owner", owner=True)

    def seed(db: Database) -> None:
        db.lessons[ce_spec.canonical] = {"id": ce_spec.canonical, "spec": ce_spec.model_dump(mode="json")}
        db.chats["synthetic-private-root"] = {"lesson_id": ce_spec.canonical, "messages": ["Private test text"]}
        db.feedback["synthetic-private-feedback"] = {"lesson_id": ce_spec.canonical, "reason": "Private test text"}

    store.transaction(seed)
    before = store.snapshot()
    domain = Domain(store, settings)
    question = "Why must this work wait for its required input?"
    with ThreadPoolExecutor(max_workers=8) as pool:
        replies = list(pool.map(lambda _: domain.request(question, owner, node_parent=ce_spec.canonical,
                                                        node_role="model", operation="pg-depth-operation"), range(16)))
    db = store.snapshot()
    assert len({r["job_id"] for r in replies}) == 1 and len(db.jobs) == 1
    assert db.reserved == settings.generation_reserve and db.spent == 0 and not db.ledger
    assert db.lessons == before.lessons and db.chats == before.chats and db.feedback == before.feedback
    job = next(iter(db.jobs.values()))
    assert job_depth_context(job, db) is not None and job["revision_of"] is None
    with pytest.raises(HTTPException) as mismatch:
        domain.request("A different branch question for that operation?", owner,
                       node_parent=ce_spec.canonical, node_role="model", operation="pg-depth-operation")
    assert mismatch.value.status_code == 409 and store.snapshot() == db
    store.transaction(lambda state: domain.settle(state, state.jobs[str(job["id"])], "failed", "Synthetic failure"))
    with pytest.raises(HTTPException) as failed:
        domain.request(question, owner, node_parent=ce_spec.canonical, node_role="model", operation="pg-depth-operation")
    assert failed.value.status_code == 409 and store.snapshot().reserved == 0
    # A completed, accounted rejection can inform one new explicit operation.
    from backend.author_transport import compact_author

    rejected = ce_spec.model_copy(deep=True)
    rejected.canonical = str(job["canonical"])
    assert rejected.teaching is not None
    missing = "label-" + rejected.teaching.core[0]
    rejected.parts = [p for p in rejected.parts if p.id != missing]

    def completed_failure(state: Database) -> None:
        import json

        state.jobs[str(job["id"])].update(
            failed_phase="author", failure_type="LearningQualityError", author_mode="compact",
            research=evidence.model_dump(mode="json"),
            call_outputs={f"lesson:{job['id']}:author": {"bytes": False, "value": json.dumps(compact_author(rejected))}},
        )
        for phase in ("research", "author"):
            state.ledger[f"lesson:{job['id']}:{phase}"] = {
                "models": ["synthetic-completed"], "uncertain": False, "response_status": "completed",
                "billing_complete": True, "charged_usd": 0.01,
            }
        state.spent = 0.02

    store.transaction(completed_failure)
    failed_state = store.snapshot()
    with ThreadPoolExecutor(max_workers=8) as pool:
        iterations = list(pool.map(lambda _: domain.request(question, owner, node_parent=ce_spec.canonical,
                                                            node_role="model", operation="pg-depth-next-operation"), range(16)))
    final = store.snapshot()
    assert len({r["job_id"] for r in iterations}) == 1 and len(final.jobs) == 2
    current = final.jobs[str(iterations[0]["job_id"])]
    assert current["phase"] == "author" and current["iteration_from"] == current["research_reused_from"] == job["id"]
    assert final.reserved == settings.generation_reserve and final.spent == failed_state.spent
    assert final.ledger == failed_state.ledger and final.jobs[str(job["id"])] == failed_state.jobs[str(job["id"])]
    assert final.lessons == before.lessons and final.chats == before.chats and final.feedback == before.feedback
    with ThreadPoolExecutor(max_workers=8) as pool:
        core_attempts = list(pool.map(lambda _: domain.request(
            "How does a synthetic standalone core work?", owner,
            owner_build=True, operation="pg-core-http-operation"), range(16)))
    assert len({r["job_id"] for r in core_attempts}) == 1
    core_id = str(core_attempts[0]["job_id"])
    assert store.snapshot().reserved == 2 * settings.generation_reserve
    store.transaction(lambda state: domain.settle(state, state.jobs[core_id], "failed", "Synthetic core failure"))
    stable = store.snapshot()
    with pytest.raises(HTTPException) as failed_core:
        domain.request("How does a synthetic standalone core work?", owner,
                       owner_build=True, operation="pg-core-http-operation")
    assert failed_core.value.status_code == 409 and store.snapshot() == stable


def test_postgres_native_import_path_and_immutable_rollback(
    settings: Settings, native_prepared: PreparedNative,
) -> None:
    """Native drafts use the same locked document without altering old media/private state."""
    import json

    import backend.native_registry as registry
    from backend.learning_bundle import learning_bundle
    from backend.learning_paths import LearningPath, PathNode
    from backend.native_publication import import_native
    from backend.native_registry import canonical_digest
    from backend.path_publication import PathPublication, PathSubmission
    from backend.starters import digest_spec

    target = urlparse(URL)
    if target.hostname != "127.0.0.1" or target.port != 55432 or target.path != "/inside_test":
        pytest.fail("Native publication tests require disposable loopback Postgres")
    with psycopg.connect(URL) as connection:
        connection.execute("DROP TABLE IF EXISTS inside_state")
    store = Store(URL, settings.data_dir)
    store.transaction(lambda db: (db.chats.update({"retained-native-private": {"messages": ["PRIVATE FIXTURE"]}}),
                                 db.ledger.update({"retained-native-ledger": {"charged_usd": .25}})))
    assert import_native(store, [native_prepared]) == (1, 0)
    assert import_native(store, [native_prepared]) == (0, 1)
    before = store.snapshot()
    manifest = json.loads(registry.REGISTRY_FILE.read_text())
    next_artifact = native_prepared.model_copy(deep=True)
    next_artifact.spec.canonical = "synthetic-native-insight"
    identity = {"id": "synthetic-native-2", "lessons": [next_artifact.spec.canonical],
                "sources": manifest["renderers"][0]["sources"]}
    next_artifact.spec.renderer.id = str(identity["id"])
    next_artifact.spec.renderer.fingerprint = canonical_digest(identity)
    next_artifact.proof.renderer_id = next_artifact.spec.renderer.id
    next_artifact.proof.renderer_fingerprint = next_artifact.spec.renderer.fingerprint
    next_artifact.proof.spec_sha256 = digest_spec(next_artifact.spec)
    manifest["renderers"].append({**identity, "fingerprint": next_artifact.spec.renderer.fingerprint,
                                  "spec_sha256": {next_artifact.spec.canonical: digest_spec(next_artifact.spec)}})
    registry.REGISTRY_FILE.write_text(json.dumps(manifest))
    conflicting = native_prepared.model_copy(deep=True)
    conflicting.proof.video_sha256 = "0" * 64
    with pytest.raises(ValueError, match="immutable"):
        import_native(store, [next_artifact, conflicting])
    assert store.snapshot() == before  # The first new record was rolled back with the conflict.
    path = LearningPath(schema_version="learning-path-1", id="synthetic-native-path",
                        title="Synthetic native graph fixture", example="Synthetic source-bound native components.",
                        entry="core", nodes=[
                            PathNode(id="core", role="core", label="Synthetic core", question=native_prepared.spec.question,
                                     outcome=native_prepared.spec.teaching.goal, lesson_id=native_prepared.spec.canonical,
                                     prerequisites=[], next=["insight"], queries=["core"]),
                            PathNode(id="insight", role="insight", label="Synthetic insight", question=next_artifact.spec.question,
                                     outcome=next_artifact.spec.teaching.goal, lesson_id=next_artifact.spec.canonical,
                                     prerequisites=["core"], next=[], queries=["insight"]),
                        ])
    assert import_native(store, [native_prepared, next_artifact], path) == (1, 1)
    owner = User(id="synthetic-native-owner", name="Synthetic owner", owner=True)
    attached = PathPublication(store).attach(native_prepared.spec.canonical,
                                             PathSubmission(path=path, allow_review_drafts=True), owner)
    after = store.snapshot()
    assert attached["bundle_sha256"] and attached["review_required"]
    assert learning_bundle(after, native_prepared.spec.canonical, owner)["path"] == path.model_dump(mode="json")
    assert after.lessons[next_artifact.spec.canonical]["depth_parent"] == native_prepared.spec.canonical
    assert after.chats == before.chats and after.ledger == before.ledger
    assert after.spent == before.spent and after.reserved == before.reserved
