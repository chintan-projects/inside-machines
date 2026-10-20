"""Separate evidence/author phases retain budget, checkpoints and source boundaries."""

from typing import cast

import pytest
from pydantic import HttpUrl, ValidationError

from backend.assets import Assets
from backend.contracts import LessonSpec
from backend.domain import Domain, User
from backend.pipeline import Pipeline
from backend.provider import UsageReceipt
from backend.research import ResearchSpec, require_evidence_sources
from backend.settings import Settings
from backend.store import Database, Store


def test_evidence_references_and_author_sources_fail_closed(
    evidence: ResearchSpec, ce_spec: LessonSpec
) -> None:
    """A syntactically valid author cannot silently add an unresearched citation."""
    require_evidence_sources(ce_spec, evidence)
    ce_spec.sources[0].url = HttpUrl("https://unresearched.example/page")
    with pytest.raises(ValueError, match="outside"):
        require_evidence_sources(ce_spec, evidence)
    raw = evidence.model_dump(mode="json")
    raw["sources"] = raw["sources"][:2]
    raw["facts"][0]["source"] = "https://unresearched.example/page"
    with pytest.raises(ValidationError):
        ResearchSpec.model_validate(raw)


async def test_completed_pre_split_author_checkpoint_does_not_pay_for_research(
    store: Store, settings: Settings, user: User, ce_spec: LessonSpec, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Deployment migration resumes an already-paid author output without a new paid phase."""
    deliveries: list[str] = []

    async def enqueue(job_id: str, phase: str) -> None:
        deliveries.append(phase)

    async def never(*args: object, **kwargs: object) -> str:
        raise AssertionError("No paid request is allowed")

    monkeypatch.setattr("backend.pipeline.model_text", never)
    pipeline = Pipeline(store, settings, Assets(settings), enqueue)
    id = str(Domain(store, settings).request("washer", user)["job_id"])
    job = pipeline._claim(id)
    assert job is not None
    lease = str(job["lease_token"])
    key = pipeline._begin_call(id, lease, "author", settings.text_phase_reserve)
    pipeline._finish_call(
        id,
        lease,
        key,
        UsageReceipt(cost_usd=0.01, models=["synthetic-test-model"]),
        failed=False,
        result=ce_spec.model_dump_json(),
    )
    store.transaction(lambda db: db.jobs[id].update(lease_until=0, pipeline_version=None))
    await pipeline.run(id)
    state = store.snapshot()
    assert deliveries == ["review"] and state.jobs[id]["phase"] == "review"
    assert len(state.ledger) == 1 and state.spent == 0.01


async def test_invalid_research_stops_before_any_authoring(
    store: Store, settings: Settings, user: User, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A paid but malformed evidence packet cannot trigger downstream calls."""
    from backend.provider import receipt_context

    calls: list[str] = []

    async def enqueue(job_id: str, phase: str) -> None:
        raise AssertionError("No downstream phase")

    async def malformed(
        prompt: str, config: Settings, *, schema: dict[str, object], task: str = "authoring"
    ) -> str:
        calls.append(task)
        receipt = receipt_context.get()
        assert receipt is not None
        receipt.models.append("synthetic-research")
        receipt.cost_usd = 0.01
        return "{}"

    monkeypatch.setattr("backend.pipeline.model_text", malformed)
    id = str(Domain(store, settings).request("washer", user)["job_id"])
    await Pipeline(store, settings, Assets(settings), enqueue).run(id)
    state = store.snapshot()
    assert calls == ["research"] and state.jobs[id]["status"] == "failed"
    assert state.jobs[id]["validation_issues"]
    assert state.spent == 0.01 and state.reserved == 0 and not state.lessons


def test_failed_evaluation_retains_uncertain_cost_without_private_output(store: Store) -> None:
    """A timed-out candidate stays in comparison results and exports no private data."""
    from backend.evaluation import comparison, failed_packet

    def seed(db: "Database") -> None:
        db.jobs["failed"] = {
            "status": "failed",
            "failure_type": "TimeoutError",
            "failed_phase": "queued",
            "prompt": "PRIVATE PROMPT",
            "call_outputs": {"private": "PRIVATE OUTPUT"},
        }
        db.ledger["lesson:failed:research"] = {
            "operation": "lesson:failed:research",
            "charged_usd": 0.30,
            "uncertain": True,
            "models": [],
        }

    store.transaction(seed)
    candidate = failed_packet(store, "failed", "vacuum")
    assert candidate.spec is None and "PRIVATE" not in candidate.model_dump_json()
    row = cast(list[dict[str, object]], comparison([candidate])["rows"])[0]
    assert (
        row["quality_result"] == "generation_failed"
        and row["cost_recorded_usd"] == 0.30
        and row["billing_uncertain"]
    )


async def test_missing_evidence_checkpoint_fails_before_payment(
    store: Store, settings: Settings, user: User, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Corrupt new-phase state cannot quietly skip research and consume paid work."""

    async def never(*args: object, **kwargs: object) -> str:
        raise AssertionError("No paid request")

    async def enqueue(job_id: str, phase: str) -> None:
        raise AssertionError("No downstream work")

    monkeypatch.setattr("backend.pipeline.model_text", never)
    id = str(Domain(store, settings).request("washer", user)["job_id"])
    store.transaction(lambda db: db.jobs[id].update(phase="author"))
    await Pipeline(store, settings, Assets(settings), enqueue).run(id)
    state = store.snapshot()
    assert state.jobs[id]["status"] == "failed" and not state.ledger and state.reserved == state.spent == 0


def test_explicit_new_revision_can_recover_completed_evidence(
    seeded: Store, settings: Settings, evidence: ResearchSpec
) -> None:
    """Recover intact evidence, preserve the failed attempt and charge no second research call."""
    import time

    from backend.research import reusable_research
    from backend.starters import digest_spec

    owner = User(id="synthetic-owner", name="Synthetic owner", owner=True)
    parent = seeded.snapshot().lessons["washing-machine"]
    parent_spec = LessonSpec.model_validate(parent["spec"])
    sha, question = digest_spec(parent_spec), parent_spec.question
    evidence.facts[0].statement = "A complete longer evidence statement. " * 10

    def seed(db: Database) -> None:
        db.jobs["completed-research"] = {
            "id": "completed-research",
            "canonical": "previous-test-revision",
            "revision_of": "washing-machine",
            "status": "failed",
            "failed_phase": "queued",
            "failure_type": "ValidationError",
            "revision_parent_sha256": sha,
            "question": question,
            "user_id": owner.id,
            "created_at": time.time(),
            "call_outputs": {
                "lesson:completed-research:research": {"bytes": False, "value": evidence.model_dump_json()}
            },
        }
        db.ledger["lesson:completed-research:research"] = {
            "models": ["synthetic-research-model"],
            "uncertain": False,
            "charged_usd": 0.07,
        }

    seeded.transaction(seed)
    result = Domain(seeded, settings).request(
        question, owner, revision_of="washing-machine", operation="explicit-recovery"
    )
    state = seeded.snapshot()
    job = state.jobs[str(result["job_id"])]
    assert job["phase"] == "author" and job["research_reused_from"] == "completed-research"
    assert state.jobs["completed-research"]["status"] == "failed" and len(state.ledger) == 1
    assert ResearchSpec.model_validate(job["research"]).facts[0].statement == evidence.facts[0].statement
    assert reusable_research(state, sha, question, "another-member") is None
    state.ledger["lesson:completed-research:research"]["uncertain"] = True
    assert reusable_research(state, sha, question, owner.id) is None
