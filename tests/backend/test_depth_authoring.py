"""Owner depth uses existing admission, evidence, publication and privacy contracts."""

import io
import json
import wave
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from typing import cast

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.app import create_app
from backend.assets import Assets
from backend.author_transport import author_schema, compact_author
from backend.contracts import LessonSpec, ReviewDecision
from backend.depth_authoring import DepthContext, job_depth_context
from backend.domain import Domain, User
from backend.pipeline import Pipeline
from backend.provider import receipt_context
from backend.research import ResearchSpec
from backend.settings import Settings
from backend.starters import digest_spec
from backend.store import Database, Store

OWNER = User(id="depth-owner", name="Owner", owner=True)
QUESTION = "Why does waiting for an input limit the calculation?"


def seed_core(store: Store, spec: LessonSpec) -> None:
    """A synthetic root carries private history that a branch may never replace."""
    def seed(db: Database) -> None:
        db.lessons[spec.canonical] = {
            "id": spec.canonical, "spec": spec.model_dump(mode="json"), "video": "synthetic-core.mp4",
            "video_sha256": "a"*64, "spec_sha256": digest_spec(spec), "quality": "test-fixture",
        }
        db.chats["root-private"] = {"lesson_id": spec.canonical, "messages": [{"text": "PRIVATE ROOT CHAT"}]}
        db.feedback["root-feedback"] = {"lesson_id": spec.canonical, "reason": "PRIVATE ROOT FEEDBACK"}
    store.transaction(seed)


def test_owner_endpoint_and_http_retry_keep_one_reservation(settings: Settings, ce_spec: LessonSpec) -> None:
    """A family session cannot spend; an ambiguous HTTP retry retains the same operation."""
    store = Store("", settings.data_dir)
    seed_core(store, ce_spec)
    deliveries: list[tuple[str, str]] = []

    async def enqueue(job_id: str, phase: str) -> None:
        deliveries.append((job_id, phase))

    body = {"question": QUESTION, "role": "insight", "operation": "depth-http-operation"}
    url = f"/api/v1/owner/lessons/{ce_spec.canonical}/depth-drafts"
    with TestClient(create_app(settings, enqueue=enqueue)) as client:
        client.post("/api/v1/auth/login", json={"name": "Family", "code": settings.invite_code})
        assert client.post(url, json=body).status_code == 403
        assert not store.snapshot().jobs and store.snapshot().reserved == 0
        client.post("/api/v1/auth/login", json={"name": "Owner", "code": settings.owner_code})
        first, retry = client.post(url, json=body), client.post(url, json=body)
        assert first.status_code == retry.status_code == 200
        assert first.json()["job_id"] == retry.json()["job_id"] and retry.json()["reused"]
        assert client.post(url, json={**body, "runtime_code": "untrusted"}).status_code == 422
        assert client.post(url, json={**body, "question": "A different scoped question?"}).status_code == 409
    db = store.snapshot()
    assert len(db.jobs) == 1 and db.reserved == settings.generation_reserve and not db.ledger
    assert len({job_id for job_id, _ in deliveries}) == 1
    job = next(iter(db.jobs.values()))
    context = DepthContext.model_validate(job["path_context"])
    assert context.parent_spec_sha256 == digest_spec(ce_spec)
    assert [node.role for node in context.path.nodes] == ["core", "insight"]
    assert context.path.nodes[1].prerequisites == ["core"] and job["revision_of"] is None
    assert "PRIVATE ROOT" not in context.model_dump_json()


def test_concurrent_depth_admission_and_explicit_failed_attempt(
    store: Store, settings: Settings, ce_spec: LessonSpec, user: User,
) -> None:
    """Concurrent calls share a job; failed operation identity never silently spends again."""
    seed_core(store, ce_spec)
    domain = Domain(store, settings)
    with ThreadPoolExecutor(max_workers=8) as pool:
        replies = list(pool.map(lambda _: domain.request(QUESTION, OWNER, node_parent=ce_spec.canonical,
                                                        node_role="model", operation="depth-concurrent"), range(16)))
    assert len({r["job_id"] for r in replies}) == 1
    assert len(store.snapshot().jobs) == 1 and store.snapshot().reserved == settings.generation_reserve
    job_id = str(replies[0]["job_id"])
    store.transaction(lambda db: domain.settle(db, db.jobs[job_id], "failed", "Synthetic failure"))
    for _ in range(2):
        with pytest.raises(HTTPException, match="new operation") as failure:
            domain.request(QUESTION, OWNER, node_parent=ce_spec.canonical, node_role="model", operation="depth-concurrent")
        assert failure.value.status_code == 409
    assert store.snapshot().reserved == 0
    with pytest.raises(HTTPException) as forbidden:
        domain.request(QUESTION, user, node_parent=ce_spec.canonical, node_role="model", operation="depth-family-attempt")
    assert forbidden.value.status_code == 403
    admitted = domain.request(QUESTION, OWNER, node_parent=ce_spec.canonical, node_role="model", operation="depth-new-operation")
    assert admitted["job_id"] != job_id and store.snapshot().reserved == settings.generation_reserve


async def test_actual_depth_pipeline_uses_parent_context_compact_schema_and_keeps_core(
    store: Store, settings: Settings, ce_spec: LessonSpec, evidence: ResearchSpec, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only model/audio responses are synthetic; phases, MP4, storage and publication run."""
    seed_core(store, ce_spec)
    original = store.snapshot()
    deliveries: list[tuple[str, str]] = []

    async def enqueue(job_id: str, phase: str) -> None:
        deliveries.append((job_id, phase))

    domain = Domain(store, settings)
    job_id = str(domain.request(QUESTION, OWNER, node_parent=ce_spec.canonical, node_role="insight",
                                operation="depth-full-pipeline")["job_id"])
    child = ce_spec.model_copy(deep=True)
    child.canonical = str(store.snapshot().jobs[job_id]["canonical"])
    child.title, child.question = "Synthetic scoped depth fixture", QUESTION
    calls: list[str] = []

    async def text(prompt: str, config: Settings, *, schema: dict[str, object], task: str = "authoring") -> str:
        receipt = receipt_context.get()
        assert receipt is not None
        receipt.models.append("synthetic-test-model")
        receipt.cost_usd = .001
        calls.append(task)
        if task == "research":
            assert ce_spec.question in prompt and "shared_example" in prompt
            return evidence.model_dump_json()
        if task == "authoring":
            assert schema == author_schema() and "COMPACT-1 AUTHORING TRANSPORT" in prompt
            context = json.loads(prompt.split("\nLEARNING_PATH_CONTEXT: ")[1])
            assert context["root_question"] == ce_spec.question
            assert context["node"]["question"] == QUESTION and context["node"]["role"] == "insight"
            assert context["parent_example"]["big_idea"] == ce_spec.big_idea
            assert context["parent_example"]["visible_labels"] and "PRIVATE ROOT" not in prompt
            assert context["prerequisites"][0]["lesson_id"] == ce_spec.canonical
            return json.dumps(compact_author(child))
        assert task == "review"
        return ReviewDecision(accepted=True, notes=[], spec_sha256=digest_spec(child)).model_dump_json()

    async def speech(narration: str, config: Settings) -> bytes:
        receipt = receipt_context.get()
        assert receipt is not None
        receipt.models.append("synthetic-test-speech")
        receipt.cost_usd = .001
        output = io.BytesIO()
        with wave.open(output, "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(8000)
            audio.writeframes(b"\0\0"*8000)
        return output.getvalue()

    monkeypatch.setattr("backend.pipeline.model_text", text)
    monkeypatch.setattr("backend.pipeline.model_speech", speech)
    pipeline = Pipeline(store, settings, Assets(settings), enqueue)
    await pipeline.run(job_id)
    while deliveries:
        delivered, _ = deliveries.pop(0)
        await pipeline.run(delivered)
    db = store.snapshot()
    assert calls == ["research", "authoring", "review"]
    assert db.jobs[job_id]["status"] == "complete" and db.reserved == 0
    assert db.lessons[ce_spec.canonical] == original.lessons[ce_spec.canonical]
    assert db.chats == original.chats and db.feedback == original.feedback
    assert "learning_bundle_sha256" not in db.lessons[ce_spec.canonical]
    result = db.lessons[child.canonical]
    assert result["depth_parent"] == ce_spec.canonical and result["depth_role"] == "insight"
    assert result["depth_parent_sha256"] == digest_spec(ce_spec) and result["video"]
    assert [row["id"] for row in domain.catalog()] == [ce_spec.canonical]
    assert {row["id"] for row in domain.catalog(include_depth=True)} == {ce_spec.canonical, child.canonical}
    reply = domain.request(QUESTION, OWNER, node_parent=ce_spec.canonical, node_role="insight", operation="depth-full-pipeline")
    assert reply == {"kind": "lesson", "lesson_id": child.canonical, "reused": True}
    assert store.snapshot().spent == pytest.approx(.006)


@pytest.mark.parametrize("problem", ["parent-changed", "context-changed", "parent-archived"])
async def test_stale_depth_context_fails_before_paid_call(
    store: Store, settings: Settings, ce_spec: LessonSpec, monkeypatch: pytest.MonkeyPatch, problem: str,
) -> None:
    """A bound parent is checked on every phase; malformed context does not spend."""
    seed_core(store, ce_spec)
    job_id = str(Domain(store, settings).request(QUESTION, OWNER, node_parent=ce_spec.canonical,
                                               node_role="model", operation="depth-context-guard")["job_id"])

    def corrupt(db: Database) -> None:
        if problem == "parent-changed":
            spec = LessonSpec.model_validate(db.lessons[ce_spec.canonical]["spec"])
            spec.title = "Synthetic illegal core mutation"
            db.lessons[ce_spec.canonical]["spec"] = spec.model_dump(mode="json")
        elif problem == "parent-archived":
            db.lessons[ce_spec.canonical]["archived"] = True
        else:
            context = cast(dict[str, object], db.jobs[job_id]["path_context"])
            example = cast(dict[str, object], context["parent_example"])
            example["big_idea"] = "An unbound different example"

    store.transaction(corrupt)
    called = False

    async def forbidden(prompt: str, config: Settings, **kwargs: object) -> str:
        nonlocal called
        called = True
        raise AssertionError("Paid work must not begin")

    async def enqueue(job_id: str, phase: str) -> None:
        return None

    monkeypatch.setattr("backend.pipeline.model_text", forbidden)
    await Pipeline(store, settings, Assets(settings), enqueue).run(job_id)
    db = store.snapshot()
    assert not called and not db.ledger and db.spent == db.reserved == 0
    assert db.jobs[job_id]["status"] == "failed"
    with pytest.raises(ValueError):
        job_depth_context(db.jobs[job_id], db)


def test_depth_is_not_a_core_revision_and_disabled_routes_do_not_reserve(
    store: Store, settings: Settings, ce_spec: LessonSpec, spec: LessonSpec,
) -> None:
    seed_core(store, ce_spec)
    domain = Domain(store, settings)
    with pytest.raises(HTTPException) as conflict:
        domain.request(QUESTION, OWNER, revision_of=ce_spec.canonical, node_parent=ce_spec.canonical,
                       node_role="model", operation="depth-both-protocols")
    assert conflict.value.status_code == 422
    store.transaction(lambda db: db.lessons.update({"legacy-core": {"spec": spec.model_dump(mode="json")}}))
    with pytest.raises(HTTPException) as legacy:
        domain.request(QUESTION, OWNER, node_parent="legacy-core", node_role="model", operation="depth-legacy-root")
    assert legacy.value.status_code == 422
    result = Domain(store, replace(settings, openai_key="")).request(
        QUESTION, OWNER, node_parent=ce_spec.canonical, node_role="model", operation="depth-no-provider")
    assert result["kind"] == "unavailable" and not store.snapshot().jobs and store.snapshot().reserved == 0
