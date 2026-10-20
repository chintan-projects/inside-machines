"""Explicit draft recovery retains original failures and never bypasses review."""

import time

from backend.contracts import LessonSpec
from backend.domain import Domain, User
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
            "canonical": "old-draft",
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
