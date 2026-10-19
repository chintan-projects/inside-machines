"""Reject the teaching failures observed in human review, before publication."""

import pytest

from backend.ac_craft import CORE, aircon_craft
from backend.contracts import LessonSpec
from backend.domain import User
from backend.quality import learning_issues, require_learning_quality
from backend.seed_aircon import aircon
from backend.settings import Settings
from backend.store import Store


def test_ac_benchmark_has_labeled_causal_and_sourced_chapters() -> None:
    """The authored benchmark satisfies the gate that the old AC lesson fails."""
    revised = aircon_craft()
    assert not learning_issues(revised)
    assert len(revised.stages) == 6
    assert {p.id[6:] for p in revised.parts if p.id.startswith("label-")} == set(CORE)
    assert learning_issues(aircon())
    assert (
        "simultaneously" in " ".join(revised.assumptions) or "run together" in revised.stages[-1].explanation
    )
    assert all("°" not in stage.input_state + stage.output_state for stage in revised.stages)


@pytest.mark.parametrize(
    "defect", ["labels", "small-label", "clipped-label", "overlap", "input", "focus", "evidence"]
)
def test_learning_failures_are_not_publishable(defect: str) -> None:
    """Independent label, clarity and evidence failures cannot masquerade as valid output."""
    spec = aircon_craft()
    labels = [p for p in spec.parts if p.id.startswith("label-")]
    if defect == "labels":
        spec.parts = [p for p in spec.parts if not p.id.startswith("label-")]
    elif defect == "small-label":
        labels[0].h = 12
    elif defect == "clipped-label":
        labels[0].x = 890
    elif defect == "overlap":
        labels[1].x, labels[1].y = labels[0].x, labels[0].y
    elif defect == "input":
        spec.stages[1].input_state = ""
    elif defect == "focus":
        spec.stages[1].focus = ""
    else:
        spec.stages[1].source_indices = []
    with pytest.raises(ValueError, match="learning-quality"):
        require_learning_quality(spec)


def test_legacy_reading_remains_compatible_without_silent_quality_approval() -> None:
    """Stored v1 lessons remain readable; new publication has a higher explicit bar."""
    payload = aircon().model_dump(mode="json")
    for stage in payload["stages"]:
        for field in ("input_state", "output_state", "focus", "source_indices"):
            stage.pop(field, None)
    legacy = LessonSpec.model_validate(payload)
    assert legacy.stages[0].input_state == ""
    assert learning_issues(legacy)


def test_publication_preserves_history_and_prevents_content_overwrite(store: Store) -> None:
    """Replacement discovery must not rewrite the content behind an existing chat."""
    from backend.ac_craft import CANONICAL
    from backend.craft import CraftArtifact, import_craft
    from backend.starters import digest_spec

    spec = aircon_craft()
    old = aircon()
    store.transaction(
        lambda db: db.lessons.update(
            {
                "air-conditioner": {
                    "id": "air-conditioner",
                    "spec": old.model_dump(mode="json"),
                    "video": "old.mp4",
                }
            }
        )
    )
    store.transaction(
        lambda db: db.chats.update(
            {
                "private-chat": {
                    "lesson_id": "air-conditioner",
                    "messages": [{"text": "original private question"}],
                }
            }
        )
    )
    before = store.snapshot().chats
    artifact = CraftArtifact(
        spec=spec, spec_sha256=digest_spec(spec), video="example.mp4", video_sha256="0" * 64
    )
    assert import_craft(store, artifact)
    assert not import_craft(store, artifact)
    assert store.snapshot().chats == before
    assert store.snapshot().lessons["air-conditioner"]["spec"] == old.model_dump(mode="json")
    assert store.snapshot().lessons["air-conditioner"]["superseded_by"] == CANONICAL
    changed = artifact.model_copy(update={"video_sha256": "1" * 64})
    with pytest.raises(ValueError, match="immutable"):
        import_craft(store, changed)


async def test_missing_labels_stop_before_review_and_speech(store: Store, settings: Settings, user: User, spec: LessonSpec, monkeypatch: pytest.MonkeyPatch) -> None:
    """A schema-valid but unlabeled lesson cannot consume more paid stages or publish."""
    from backend.assets import Assets
    from backend.domain import Domain
    from backend.pipeline import Pipeline
    from backend.provider import receipt_context

    calls: list[str] = []
    async def enqueue(job_id: str, phase: str) -> None:
        return None
    async def text(prompt: str, config: Settings, *, schema: dict[str,object]) -> str:
        calls.append("author")
        receipt = receipt_context.get()
        assert receipt is not None
        receipt.models.append("explicit-test-provider")
        receipt.cost_usd = .01
        draft = spec.model_copy(deep=True)
        draft.parts = [p for p in draft.parts if not p.id.startswith("label-")]
        return draft.model_dump_json()
    monkeypatch.setattr("backend.pipeline.model_text",text)
    job_id = str(Domain(store,settings).request("washer",user)["job_id"])
    await Pipeline(store,settings,Assets(settings),enqueue).run(job_id)
    state = store.snapshot()
    assert calls == ["author"]
    assert state.jobs[job_id]["failure_type"] == "LearningQualityError"
    assert state.jobs[job_id]["quality_issues"]
    assert state.jobs[job_id]["status"] == "failed"
    assert not state.lessons
    assert state.reserved == 0


def test_provider_schema_requires_defaulted_teaching_fields() -> None:
    """Strict structured output must request the fields legacy records can omit."""
    from backend.provider_schema import openai_schema

    original = LessonSpec.model_json_schema()
    adapted = openai_schema(original)
    assert adapted is not original

    def check(node: object) -> None:
        if isinstance(node, dict):
            if node.get("type") == "object" and "properties" in node:
                assert set(node["required"]) == set(node["properties"])
            for value in node.values():
                check(value)
        elif isinstance(node, list):
            for value in node:
                check(value)

    check(adapted)
    assert original == LessonSpec.model_json_schema()
