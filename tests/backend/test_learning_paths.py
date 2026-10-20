"""Planning/schema reuse, not evidence of visual or factual teaching quality."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.contracts import LessonSpec
from backend.learning_paths import EXPLANATION_CONTRACT, LearningPath, path_prompt, validate_path
from backend.prompts import author_policy_fingerprint, lesson_prompt, path_node_prompt, review_prompt
from backend.research import ResearchSpec

PATH = Path(__file__).resolve().parents[2] / "experiments/gpu-study/path.json"
LESSONS = {"gpu-core-s3", "gpu-study-1", "gpu-memory-s3", "gpu-matrix-s3"}


def test_actual_gpu_envelope_resolves_only_registered_lessons() -> None:
    path = validate_path(PATH.read_text(), LESSONS)
    assert path.entry == "core" and len(path.nodes) == 4
    assert path.nodes[-1].role == "model"
    assert validate_path(path.model_dump_json(), LESSONS) == path
    with pytest.raises(ValueError, match="Unregistered"):
        validate_path(path.model_dump_json(), {"gpu-core-s3"})


@pytest.mark.parametrize("failure", ["version", "duplicate", "prerequisite", "edge", "cycle", "orphan", "code"])
def test_invalid_model_proposed_graphs_fail_closed(failure: str) -> None:
    data = json.loads(PATH.read_text())
    if failure == "version":
        data["schema_version"] = "learning-path-2"
    elif failure == "duplicate":
        data["nodes"][1]["id"] = "core"
    elif failure == "prerequisite":
        data["nodes"][0]["prerequisites"] = ["matrix"]
    elif failure == "edge":
        data["nodes"][0]["next"] = ["absent"]
    elif failure == "cycle":
        data["nodes"][-1]["next"] = ["core"]
    elif failure == "orphan":
        data["nodes"][0]["next"] = ["matrix"]
    else:
        data["nodes"][0]["renderer"] = "https://untrusted.invalid/code.js"
    with pytest.raises(ValidationError):
        LearningPath.model_validate(data)


def test_another_concept_uses_the_same_envelope_without_gpu_fields() -> None:
    """Structural fixture only: this does not implement or approve a new vacuum lesson."""
    path = validate_path(json.dumps({
        "schema_version": "learning-path-1", "id": "vacuum-fixture", "title": "How does a vacuum work?",
        "example": "Follow one stream of air through a nozzle and filter.", "entry": "core",
        "nodes": [
            {"id": "core", "role": "core", "label": "The core explanation",
             "question": "How does air carry dirt?", "outcome": "Trace airflow and dirt collection.",
             "lesson_id": "vacuum-core", "prerequisites": [], "next": ["filter"], "queries": ["overview"]},
            {"id": "filter", "role": "insight", "label": "Inside the filter",
             "question": "How can air pass while dirt stays?", "outcome": "Distinguish air passage from retained dirt.",
             "lesson_id": "vacuum-filter", "prerequisites": ["core"], "next": [], "queries": ["filter"]},
        ],
    }), {"vacuum-core", "vacuum-filter"})
    assert path.nodes[-1].id == "filter"


def test_provider_neutral_planning_prompt_uses_evidence_and_registered_targets(evidence: ResearchSpec) -> None:
    prompt = path_prompt("How does a GPU work?", evidence, LESSONS)
    assert EXPLANATION_CONTRACT in prompt and "gpu-computing" not in prompt  # prose guide, not provider routing
    payload = json.loads(prompt.split("\nDATA: ")[1])
    assert payload["registered_target_lessons"] == sorted(LESSONS)
    assert payload["evidence"] == evidence.model_dump(mode="json")
    assert payload["schema"] == LearningPath.model_json_schema()
    with pytest.raises(ValueError):
        path_prompt("gpu", evidence, set())
    with pytest.raises(ValueError):
        path_prompt("gpu", evidence, {"only-one"})


def test_whole_system_completeness_is_required_by_author_and_both_review_modes(ce_spec: LessonSpec) -> None:
    assert EXPLANATION_CONTRACT in lesson_prompt("gpu", "gpu")
    assert EXPLANATION_CONTRACT in review_prompt(ce_spec)
    assert EXPLANATION_CONTRACT in review_prompt(ce_spec, decision_only=True)
    assert len(author_policy_fingerprint()) == 64


def test_node_authoring_reuses_existing_lesson_contract_and_parent_example(evidence: ResearchSpec) -> None:
    path = validate_path(PATH.read_text(), LESSONS)
    prompt = path_node_prompt(path, "matrix", "gpu-matrix-draft", evidence)
    context = json.loads(prompt.split("\nLEARNING_PATH_CONTEXT: ")[1])
    assert context["shared_example"] == path.example
    assert context["node"]["question"] == path.nodes[-1].question
    assert context["prerequisites"][0]["id"] == "core"
    assert "VERSION 2 / CE-1" in prompt and "source_table" in prompt
    assert "gpu-computing-1" in prompt
    with pytest.raises(ValueError, match="Unknown"):
        path_node_prompt(path, "absent", "gpu-draft", evidence)
