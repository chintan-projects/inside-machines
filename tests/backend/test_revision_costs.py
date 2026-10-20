"""A cheap repair must not conceal the paid authoring it builds on."""

import pytest

from backend.contracts import LessonSpec
from backend.evaluation import comparison, failed_packet, packet
from backend.store import Database, Store


@pytest.mark.parametrize("failed", [False, True])
def test_patch_cost_reports_prior_inputs_without_double_counting(
    store: Store, ce_spec: LessonSpec, failed: bool
) -> None:
    """Incremental, reused research and prior editorial work remain disjoint."""

    def seed(db: Database) -> None:
        db.lessons[ce_spec.canonical] = {"spec": ce_spec.model_dump(mode="json"), "video_sha256": "0" * 64}
        db.jobs["base"] = {"editorial_feedback": {"job_id": "earlier"}}
        db.jobs["earlier"] = {"editorial_feedback": {"job_id": "base"}}
        db.jobs["fresh"] = {
            "lesson_id": ce_spec.canonical,
            "author_mode": "patch",
            "editorial_feedback": {"job_id": "earlier"},
            "research_reused_from": "base",
            "status": "failed" if failed else "completed",
        }
        for op, cost in (
            ("base:research", 0.05),
            ("base:author", 0.08),
            ("earlier:author", 0.10),
            ("earlier:review", 0.02),
            ("fresh:author", 0.01),
            ("fresh:review", 0.02),
            ("fresh:voice-0", 0.005),
        ):
            db.ledger["lesson:" + op] = {
                "models": ["synthetic"],
                "charged_usd": cost,
                "uncertain": False,
                "private_prompt": "PRIVATE PROMPT",
            }

    store.transaction(seed)
    result = failed_packet(store, "fresh", "vacuum") if failed else packet(store, ce_spec.canonical, "vacuum")
    assert result.authoring_mode == "patch"
    assert sum(float(str(r["charged_usd"])) for r in result.usage) == pytest.approx(0.035)
    assert sum(float(str(r["charged_usd"])) for r in result.reused_research_usage) == pytest.approx(0.05)
    assert sum(float(str(r["charged_usd"])) for r in result.revision_input_usage) == pytest.approx(0.20)
    groups = [result.usage, result.reused_research_usage, result.revision_input_usage]
    operations = [str(r["operation"]) for group in groups for r in group]
    assert len(operations) == len(set(operations)) and "PRIVATE" not in result.model_dump_json()
    rows = comparison([result])["rows"]
    assert isinstance(rows, list)
    row = rows[0]
    assert isinstance(row, dict)
    assert row["revision_input_recorded_usd"] == pytest.approx(0.20)
