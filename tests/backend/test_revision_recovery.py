"""Explicit draft recovery retains original failures and never bypasses review."""

import json
import time

import pytest

from backend.accounting import receipt_origin
from backend.assets import Assets
from backend.author_transport import compact_author
from backend.contracts import LessonSpec, ReviewDecision
from backend.domain import Domain, User
from backend.pipeline import Pipeline
from backend.prompts import AUTHOR_POLICY
from backend.provider import receipt_context
from backend.research import ResearchSpec, reusable_research
from backend.revision_recovery import reusable_draft
from backend.settings import Settings
from backend.starters import digest_spec
from backend.store import Database, Store


def test_owner_recovers_only_valid_known_draft(
    seeded: Store, settings: Settings, ce_spec: LessonSpec, evidence: ResearchSpec
) -> None:
    """Same operation dedupes; source/quality, identity, age and billing stay guarded."""
    owner = User(id="owner", name="Test owner", owner=True)
    parent = LessonSpec.model_validate(seeded.snapshot().lessons["washing-machine"]["spec"])
    sha = digest_spec(parent)

    def seed(db: Database) -> None:
        db.jobs["old"] = {
            "author_policy_sha256": AUTHOR_POLICY,
            "canonical": ce_spec.canonical,
            "status": "failed",
            "failed_phase": "review",
            "failure_type": "ModelUnavailableError",
            "revision_of": "washing-machine",
            "revision_parent_sha256": sha,
            "question": parent.question,
            "user_id": owner.id,
            "created_at": time.time(),
            "research": evidence.model_dump(mode="json"),
            "spec": ce_spec.model_dump(mode="json"),
        }
        for phase in ("research", "author", "review"):
            db.ledger[f"lesson:old:{phase}"] = {"models": ["synthetic"], "uncertain": False}

    seeded.transaction(seed)
    before = seeded.snapshot()
    result = Domain(seeded, settings).request(
        parent.question, owner, revision_of="washing-machine", operation="explicit-review"
    )
    state = seeded.snapshot()
    job = state.jobs[str(result["job_id"])]
    assert job["phase"] == "review" and job["review_protocol"] == "verdict-1"
    assert job["draft_reused_from"] == job["research_reused_from"] == "old"
    assert job["draft_reused_spec_sha256"] == digest_spec(ce_spec)
    draft = LessonSpec.model_validate(job["spec"])
    assert draft.canonical == job["canonical"] and draft.teaching == ce_spec.teaching
    assert state.jobs["old"] == before.jobs["old"] and state.ledger == before.ledger
    assert state.reserved == settings.generation_reserve and state.spent == 0
    again = Domain(seeded, settings).request(
        parent.question, owner, revision_of="washing-machine", operation="explicit-review"
    )
    assert again["job_id"] == result["job_id"] and seeded.snapshot().reserved == state.reserved
    assert reusable_draft(before, sha, parent.question, "another-member") is None
    assert reusable_draft(before, "another-parent", parent.question, owner.id) is None
    before.jobs["old"]["author_policy_sha256"] = "old-policy"
    assert reusable_draft(before, sha, parent.question, owner.id) is None
    before.jobs["old"]["author_policy_sha256"] = AUTHOR_POLICY
    before.jobs["old"]["created_at"] = 0
    assert reusable_draft(before, sha, parent.question, owner.id) is None
    before.jobs["old"]["created_at"] = time.time()
    before.ledger["lesson:old:review"]["uncertain"] = True
    assert reusable_draft(before, sha, parent.question, owner.id) is None
    before.ledger["lesson:old:review"]["uncertain"] = False
    before.jobs["old"]["failure_type"] = "ValueError"
    assert reusable_draft(before, sha, parent.question, owner.id) is None
    before.jobs["old"]["failure_type"] = "ModelUnavailableError"
    before.jobs["old"]["spec"] = {}
    assert reusable_draft(before, sha, parent.question, owner.id) is None
    assert reusable_research(before, sha, parent.question, owner.id) is not None
    before.jobs["old"]["failure_type"] = "ValueError"
    assert reusable_research(before, sha, parent.question, owner.id) is None


async def test_explicit_recovery_reviews_known_compact_output_without_reauthoring(
    seeded: Store,
    settings: Settings,
    ce_spec: LessonSpec,
    evidence: ResearchSpec,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Compiler repair reuses only validated paid output and its original provenance."""
    owner = User(id="owner", name="Test owner", owner=True)
    parent = LessonSpec.model_validate(seeded.snapshot().lessons["washing-machine"]["spec"])
    payload = compact_author(ce_spec)
    parts = payload["parts"]
    assert isinstance(parts, list)
    for part in parts:
        if part["shape"] == "text":
            part["paint"][1] = ""

    def seed(db: Database) -> None:
        db.jobs["evidence-source"] = {"canonical": "research-only", "status": "failed"}
        db.ledger["lesson:evidence-source:research"] = {"models": ["synthetic"], "uncertain": False}
        db.ledger["lesson:compact:author"] = {"models": ["synthetic"], "uncertain": False}
        db.jobs["compact"] = {
            "author_policy_sha256": AUTHOR_POLICY,
            "canonical": ce_spec.canonical,
            "status": "failed",
            "failed_phase": "author",
            "failure_type": "ValidationError",
            "revision_of": "washing-machine",
            "revision_parent_sha256": digest_spec(parent),
            "question": parent.question,
            "user_id": owner.id,
            "created_at": time.time(),
            "research": evidence.model_dump(mode="json"),
            "research_reused_from": "evidence-source",
            "author_protocol": "compact-1",
            "call_outputs": {"lesson:compact:author": {"bytes": False, "value": json.dumps(payload)}},
        }

    seeded.transaction(seed)
    before = seeded.snapshot()
    id = str(
        Domain(seeded, settings).request(
            parent.question, owner, revision_of="washing-machine", operation="explicit-compiled-recovery"
        )["job_id"]
    )
    job = seeded.snapshot().jobs[id]
    assert job["phase"] == "review" and job["draft_checkpoint_from"] == job["draft_reused_from"] == "compact"
    assert job["research_reused_from"] == "evidence-source"
    calls: list[str] = []

    async def text(
        prompt: str, config: Settings, *, schema: dict[str, object], task: str = "authoring"
    ) -> str:
        assert task == "review"
        calls.append(task)
        receipt = receipt_context.get()
        assert receipt is not None
        receipt.models.append("synthetic-review")
        receipt.cost_usd = 0.01
        return ReviewDecision(
            accepted=True, notes=[], spec_sha256=digest_spec(LessonSpec.model_validate(job["spec"]))
        ).model_dump_json()

    async def enqueue(job_id: str, phase: str) -> None:
        assert phase == "voice-0"

    monkeypatch.setattr("backend.pipeline.model_text", text)
    await Pipeline(seeded, settings, Assets(settings), enqueue).run(id)
    state = seeded.snapshot()
    assert calls == ["review"] and state.jobs[id]["phase"] == "voice-0" and state.spent == 0.01
    assert state.jobs["compact"] == before.jobs["compact"]
    for key, row in before.ledger.items():
        assert state.ledger[key] == row
    state.jobs["a"] = {"research_reused_from": "b"}
    state.jobs["b"] = {"research_reused_from": "a"}
    assert receipt_origin(state, "a", "research") is None
