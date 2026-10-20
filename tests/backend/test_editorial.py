"""Explicit revision learns from a rejection without promoting or retrying it."""

import json

import pytest
from pydantic import HttpUrl

from backend.assets import Assets
from backend.contracts import LessonSpec, ReviewDecision
from backend.domain import Domain, User
from backend.editorial import author_feedback, editorial_notes, latest_feedback
from backend.lesson_patch import LessonPatch
from backend.pipeline import Pipeline
from backend.provider import receipt_context
from backend.research import ResearchSpec
from backend.settings import Settings
from backend.starters import digest_spec
from backend.store import Store


async def test_critique_guides_fresh_authoring_without_private_data(
    seeded: Store,
    settings: Settings,
    ce_spec: LessonSpec,
    evidence: ResearchSpec,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only a fresh request pays; exact critique and paid failure stay immutable."""
    import time

    owner = User(id="owner", name="Test owner", owner=True)
    parent = LessonSpec.model_validate(seeded.snapshot().lessons["washing-machine"]["spec"])
    verdict = ReviewDecision(
        accepted=False, notes=["Start markers outside the inlet."], spec_sha256=digest_spec(ce_spec)
    )

    state = seeded.snapshot()
    state.jobs["rejected"] = {
        "canonical": ce_spec.canonical,
        "status": "failed",
        "failed_phase": "review",
        "review_protocol": "verdict-1",
        "question": parent.question,
        "user_id": owner.id,
        "revision_parent_sha256": digest_spec(parent),
        "created_at": time.time(),
        "spec": ce_spec.model_dump(mode="json"),
        "call_outputs": {"lesson:rejected:review": {"bytes": False, "value": verdict.model_dump_json()}},
        "prompt": "PRIVATE PROMPT",
    }
    for phase in ("author", "review"):
        state.ledger[f"lesson:rejected:{phase}"] = {"models": ["synthetic"], "uncertain": False}
    seeded.transaction(lambda db: (db.jobs.update(state.jobs), db.ledger.update(state.ledger)))
    feedback = latest_feedback(state, digest_spec(parent), parent.question, owner.id)
    assert editorial_notes("rejected", state.jobs["rejected"]) == verdict.notes
    assert feedback is not None and "PRIVATE" not in json.dumps(feedback)
    assert latest_feedback(state, digest_spec(parent), parent.question, "another-member") is None
    full = author_feedback(feedback, evidence)
    assert full is not None and "previous_draft" in full
    changed = evidence.model_copy(deep=True)
    changed.sources[0].url = HttpUrl("https://other.example/source")
    different = author_feedback(feedback, changed)
    assert different is not None and "previous_draft" not in different
    id = str(
        Domain(seeded, settings).request(
            parent.question, owner, revision_of="washing-machine", operation="explicit-critique-iteration"
        )["job_id"]
    )
    job = seeded.snapshot().jobs[id]
    assert job["editorial_feedback"] == feedback and job["phase"] == "queued"
    seeded.transaction(
        lambda db: db.jobs[id].update(phase="author", research=evidence.model_dump(mode="json"))
    )
    calls: list[str] = []

    async def text(
        prompt: str, config: Settings, *, schema: dict[str, object], task: str = "authoring"
    ) -> str:
        assert task == "authoring" and "Start markers outside the inlet." in prompt
        calls.append(task)
        receipt = receipt_context.get()
        assert receipt is not None
        receipt.models.append("synthetic-author")
        receipt.cost_usd = 0.01
        changed = ce_spec.graphics[0].model_copy(update={"x": ce_spec.graphics[0].x + 1})
        return LessonPatch(
            base_sha256=digest_spec(ce_spec),
            parts=[],
            graphics=[changed],
            stages=[],
            teaching=None,
            notes=["Synthetic patch for routing only."],
        ).model_dump_json()

    async def enqueue(job_id: str, phase: str) -> None:
        assert phase == "review"

    monkeypatch.setattr("backend.pipeline.model_text", text)
    await Pipeline(seeded, settings, Assets(settings), enqueue).run(id)
    after = seeded.snapshot()
    assert calls == ["authoring"] and after.jobs[id]["phase"] == "review"
    assert after.jobs["rejected"] == state.jobs["rejected"] and after.spent == 0.01
    state.ledger["lesson:rejected:review"]["uncertain"] = True
    assert latest_feedback(state, digest_spec(parent), parent.question, owner.id) is None


async def test_wrong_hash_feedback_never_drives_a_paid_call(
    store: Store,
    settings: Settings,
    user: User,
    ce_spec: LessonSpec,
    evidence: ResearchSpec,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Corrupt feedback fails before prompt dispatch."""
    feedback = {"draft": ce_spec.model_dump(mode="json"), "spec_sha256": "0" * 64}
    with pytest.raises(ValueError, match="another draft"):
        author_feedback(feedback, evidence)

    async def never(*args: object, **kwargs: object) -> str:
        raise AssertionError("Corrupt local context cannot dispatch a paid call")

    async def enqueue(job_id: str, phase: str) -> None:
        raise AssertionError("Corrupt feedback cannot advance")

    monkeypatch.setattr("backend.pipeline.model_text", never)
    id = str(Domain(store, settings).request("washer", user)["job_id"])
    store.transaction(
        lambda db: db.jobs[id].update(
            phase="author", research=evidence.model_dump(mode="json"), editorial_feedback=feedback
        )
    )
    await Pipeline(store, settings, Assets(settings), enqueue).run(id)
    state = store.snapshot()
    assert state.jobs[id]["status"] == "failed" and not state.ledger and state.spent == state.reserved == 0
