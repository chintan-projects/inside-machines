"""Cross-domain admission/routing checks; no model or learning-quality claims."""

import json
from dataclasses import replace

import pytest

from backend import concept_guides
from backend.assets import Assets
from backend.author_transport import compact_author
from backend.concept_guides import GENERAL, GPU, LLM, PHYSICAL, guide_for
from backend.contracts import LessonSpec, ReviewDecision, canonicalize
from backend.domain import Domain, User
from backend.evaluation import cases
from backend.pipeline import Pipeline
from backend.prompts import AUTHOR_POLICY, author_policy_fingerprint, lesson_prompt
from backend.provider import receipt_context
from backend.research import ResearchSpec
from backend.settings import Settings
from backend.starters import digest_spec
from backend.store import Store


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("How do GPUs work?", "gpu"),
        ("How does a graphics processing unit work?", "gpu"),
        ("Explain graphics processing units", "gpu"),
        ("How do LLMs work?", "llm"),
        ("How does a large language model work?", "llm"),
        ("Explain large language models", "llm"),
        ("How does GPU memory work?", "gpu-memory"),
        ("How does LLM training work?", "llm-training"),
        ("How does LLM inference work?", "llm-inference"),
        ("How does NVIDIA GPU cooling work?", "nvidia-gpu-cooling"),
    ],
)
def test_computing_aliases_preserve_subtopic_identity(question: str, expected: str) -> None:
    """Equivalent names reuse; different mechanisms/scope must not share a cache key."""
    assert canonicalize(question) == expected


@pytest.mark.parametrize(
    ("question", "id"),
    [
        ("How do GPUs work?", GPU.id),
        ("How do LLMs work?", LLM.id),
        ("How does a GPU fan work?", PHYSICAL.id),
        ("How does a refrigerator work?", PHYSICAL.id),
        ("How does GPU hardware run an LLM?", GENERAL.id),
        ("How does a compiler work?", GENERAL.id),
    ],
)
def test_trusted_guidance_matches_scope(question: str, id: str) -> None:
    """A guide specializes constraints, not a forced physical representation."""
    guide = guide_for(question)
    assert guide.id == id
    prompt = lesson_prompt(question, canonicalize(question), guide=guide)
    assert guide.id in prompt and json.dumps(guide.authoring) in prompt
    assert "Draw a real recognizable machine using" not in prompt
    if guide == LLM:
        assert guide.representation == "information" and "ordinary inference" in prompt


def test_guide_change_invalidates_author_checkpoint_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    """Recovery cannot treat a draft written under different domain rules as current."""
    assert author_policy_fingerprint() == AUTHOR_POLICY
    changed = dict(concept_guides.GUIDES)
    changed[LLM.id] = replace(LLM, authoring=LLM.authoring + " Changed trusted guidance.")
    monkeypatch.setattr(concept_guides, "GUIDES", changed)
    assert author_policy_fingerprint() != AUTHOR_POLICY
    assert {"gpu", "llm"} <= {case.id for case in cases()}


@pytest.mark.parametrize("topic", ["gpu", "llm"])
def test_two_members_reuse_equivalent_concept_without_new_spend(
    store: Store, settings: Settings, ce_spec: LessonSpec, topic: str
) -> None:
    """The existing catalog path accepts logical topics; this fixture is not a real lesson."""
    ce_spec.canonical, ce_spec.aliases = topic, [topic]
    store.transaction(
        lambda db: db.lessons.update({topic: {"id": topic, "spec": ce_spec.model_dump(mode="json")}})
    )
    for index, question in enumerate(
        [
            f"How do {topic.upper()}s work?",
            "graphics processing unit" if topic == "gpu" else "large language model",
        ]
    ):
        user = User(id=f"member-{index}", name="Test member", owner=False)
        result = Domain(store, settings).request(question, user)
        assert result == {"kind": "lesson", "lesson_id": topic, "reused": True}
    db = store.snapshot()
    assert not db.jobs and not db.ledger and db.spent == db.reserved == 0


@pytest.mark.parametrize("topic", ["gpu", "llm"])
async def test_concept_guide_is_shared_by_research_author_and_review(
    store: Store,
    settings: Settings,
    user: User,
    ce_spec: LessonSpec,
    evidence: ResearchSpec,
    monkeypatch: pytest.MonkeyPatch,
    topic: str,
) -> None:
    """Synthetic DTOs prove routing/billing only, not computing visuals or factual quality."""
    guide = guide_for(topic)
    id = str(Domain(store, settings).request(f"How does a {topic} work?", user)["job_id"])
    assert store.snapshot().jobs[id]["concept_guide"] == guide.id
    # Subsequent phases must use the recorded guide even if question-based selection changes.
    store.transaction(lambda db: db.jobs[id].update(question="An intentionally ambiguous synthetic topic"))
    ce_spec.canonical = topic
    calls: list[str] = []

    async def enqueue(job_id: str, phase: str) -> None:
        return None

    async def text(
        prompt: str, config: Settings, *, schema: dict[str, object], task: str = "authoring"
    ) -> str:
        expected = {
            "research": guide.research,
            "authoring": json.dumps(guide.authoring),
            "review": guide.review,
        }
        assert expected[task] in prompt and schema
        receipt = receipt_context.get()
        assert receipt is not None
        receipt.models.append("synthetic-routing-only")
        receipt.cost_usd = 0.01
        calls.append(task)
        if task == "research":
            return evidence.model_dump_json()
        if task == "authoring":
            return json.dumps(compact_author(ce_spec))
        return ReviewDecision(accepted=True, notes=[], spec_sha256=digest_spec(ce_spec)).model_dump_json()

    monkeypatch.setattr("backend.pipeline.model_text", text)
    pipeline = Pipeline(store, settings, Assets(settings), enqueue)
    for _ in range(3):
        await pipeline.run(id)
    db = store.snapshot()
    assert calls == ["research", "authoring", "review"]
    assert db.jobs[id]["phase"] == "voice-0" and db.spent == pytest.approx(0.03)
    assert not db.lessons  # No synthetic content is promoted as a computing lesson.


async def test_unknown_stored_guide_fails_before_any_paid_call(
    store: Store, settings: Settings, user: User, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unsupported metadata releases reservation without an uncertain provider charge."""
    id = str(Domain(store, settings).request("How does an LLM work?", user)["job_id"])
    store.transaction(lambda db: db.jobs[id].update(concept_guide="untrusted-client-guide"))

    async def never(*args: object, **kwargs: object) -> str:
        raise AssertionError("No paid work may start")

    async def enqueue(job_id: str, phase: str) -> None:
        raise AssertionError("No downstream work may start")

    monkeypatch.setattr("backend.pipeline.model_text", never)
    await Pipeline(store, settings, Assets(settings), enqueue).run(id)
    db = store.snapshot()
    assert db.jobs[id]["status"] == "failed" and db.jobs[id]["failure_type"] == "ValueError"
    assert not db.ledger and db.spent == db.reserved == 0
