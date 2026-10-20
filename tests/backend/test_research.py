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
    raw["facts"][0]["source"] = 2
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
    store.transaction(lambda db: db.jobs[id].update(lease_until=0))
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
