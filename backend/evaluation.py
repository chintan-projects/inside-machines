"""Create comparable private review packets without dispatching paid model calls."""

import argparse
import json
from pathlib import Path
from typing import Literal, cast

from _shared.services.logger import get_logger
from pydantic import BaseModel, ConfigDict, Field

from .contracts import LessonSpec
from .editorial import editorial_notes
from .quality import learning_issues
from .settings import ROOT, load_settings
from .starters import digest_spec
from .store import Database, Store

logger = get_logger(__name__)


class EvalCase(BaseModel):
    """Fixed question and critical failure criteria, independent of provider."""

    id: str
    question: str
    family: str
    must_explain: list[str]
    misconception: str
    transfer: str
    critical_errors: list[str]


class HumanRatings(BaseModel):
    """Empty until a person rates the anonymized artifact; no automatic quality score."""

    model_config = ConfigDict(extra="forbid")
    reviewer: str = ""
    factual: int | None = Field(default=None, ge=0, le=2)
    causal: int | None = Field(default=None, ge=0, le=2)
    visual: int | None = Field(default=None, ge=0, le=2)
    simplicity: int | None = Field(default=None, ge=0, le=2)
    transfer: int | None = Field(default=None, ge=0, le=2)
    critical_error: bool | None = None


class EvaluationPacket(BaseModel):
    """Explicitly separate structural results, actual receipts and human judgment."""

    version: str = "ce-1"
    case: EvalCase
    lesson_id: str
    spec_sha256: str
    video_sha256: str
    spec: LessonSpec | None
    outcome: Literal["artifact", "generation_failed"] = "artifact"
    job_id: str = ""
    failure_type: str = ""
    failed_phase: str = ""
    structural_issues: list[str]
    editorial_issues: list[str] = Field(default_factory=list)
    usage: list[dict[str, object]]
    reused_research_usage: list[dict[str, object]] = Field(default_factory=list)
    reused_draft_usage: list[dict[str, object]] = Field(default_factory=list)
    authoring_mode: str = ""
    revision_input_usage: list[dict[str, object]] = Field(default_factory=list)
    ratings: HumanRatings = Field(default_factory=HumanRatings)
    limitation: str = "Structural validation is not a factual, visual or learning evaluation. Empty ratings are unmeasured. Receipts may be absent for authored lessons."


def cases() -> list[EvalCase]:
    """Load a fixed source-controlled set; never accept code/provider URLs."""
    data = json.loads((ROOT / "evals/concept-cases.json").read_text())
    return [EvalCase.model_validate(case) for case in data["cases"]]


def packet(store: Store, lesson_id: str, case_id: str) -> EvaluationPacket:
    """Export public lesson content plus whitelisted cost receipts, never chats/prompts."""
    case = next((c for c in cases() if c.id == case_id), None)
    if case is None:
        raise ValueError("Unknown evaluation case")
    db = store.snapshot()
    lesson = db.lessons.get(lesson_id)
    if lesson is None:
        raise ValueError("Lesson not found")
    spec = LessonSpec.model_validate(lesson["spec"])
    jobs = {id for id, j in db.jobs.items() if j.get("lesson_id") == lesson_id}
    usage = _usage(db, jobs)
    research_usage, draft_usage = _reused_usage(db, jobs)
    excluded = {str(r["operation"]) for r in [*usage, *research_usage, *draft_usage]}
    return EvaluationPacket(
        case=case,
        lesson_id=lesson_id,
        spec_sha256=digest_spec(spec),
        video_sha256=str(lesson.get("video_sha256", "")),
        spec=spec,
        structural_issues=learning_issues(spec),
        usage=usage,
        reused_research_usage=research_usage,
        reused_draft_usage=draft_usage,
        authoring_mode=",".join(
            sorted(
                {
                    str(db.jobs[j].get("author_mode") or db.jobs[j].get("author_protocol") or "legacy")
                    for j in jobs
                }
            )
        )
        if jobs
        else "authored",
        revision_input_usage=_revision_inputs(db, jobs, excluded),
    )


def _usage(db: Database, jobs: set[str]) -> list[dict[str, object]]:
    """Export only accounting metadata, never prompts, outputs or requester identity."""
    keys = (
        "operation",
        "models",
        "input_tokens",
        "output_tokens",
        "search_calls",
        "web_tool_calls",
        "search_estimated",
        "response_status",
        "incomplete_reason",
        "model_identity_estimated",
        "cost_usd",
        "charged_usd",
        "speech_estimated",
        "uncertain",
    )
    return [
        {**{key: row[key] for key in keys if key in row}, "operation": operation}
        for operation, row in db.ledger.items()
        if any(operation.startswith(f"lesson:{job}:") for job in jobs)
    ]


def _reused_usage(
    db: Database, jobs: set[str]
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Expose reused prerequisites separately for both successful and failed runs."""
    reused = {str(db.jobs[j]["research_reused_from"]) for j in jobs if db.jobs[j].get("research_reused_from")}
    drafts = {str(db.jobs[j]["draft_reused_from"]) for j in jobs if db.jobs[j].get("draft_reused_from")}
    return (
        [r for r in _usage(db, reused) if str(r["operation"]).endswith(":research")],
        [r for r in _usage(db, drafts) if str(r["operation"]).endswith(":author")],
    )


def _revision_inputs(db: Database, jobs: set[str], excluded: set[str]) -> list[dict[str, object]]:
    """Keep paid critique ancestors visible once, separately from incremental cost."""
    pending = list(jobs)
    inputs: set[str] = set()
    while pending:
        feedback = db.jobs.get(pending.pop(), {}).get("editorial_feedback")
        if not isinstance(feedback, dict):
            continue
        source = str(feedback.get("job_id") or "")
        if source and source not in jobs and source not in inputs:
            inputs.add(source)
            pending.append(source)
    return [r for r in _usage(db, inputs) if str(r["operation"]) not in excluded]


def failed_packet(store: Store, job_id: str, case_id: str) -> EvaluationPacket:
    """Keep failed/uncertain runs in the denominator without exporting unpublished output."""
    case = next((c for c in cases() if c.id == case_id), None)
    db = store.snapshot()
    job = db.jobs.get(job_id)
    if case is None or job is None or job.get("status") != "failed":
        raise ValueError("A failed packet needs a known case and terminal failed job")
    usage = _usage(db, {job_id})
    research_usage, draft_usage = _reused_usage(db, {job_id})
    excluded = {str(r["operation"]) for r in [*usage, *research_usage, *draft_usage]}
    return EvaluationPacket(
        case=case,
        lesson_id="",
        job_id=job_id,
        spec_sha256="",
        video_sha256="",
        spec=None,
        outcome="generation_failed",
        failure_type=str(job.get("failure_type", "unknown")),
        failed_phase=str(job.get("failed_phase", "")),
        structural_issues=cast(list[str], job.get("quality_issues", [])),
        editorial_issues=editorial_notes(job_id, job),
        usage=usage,
        reused_research_usage=research_usage,
        reused_draft_usage=draft_usage,
        authoring_mode=str(job.get("author_mode") or job.get("author_protocol") or ""),
        revision_input_usage=_revision_inputs(db, {job_id}, excluded),
    )


def comparison(packets: list[EvaluationPacket]) -> dict[str, object]:
    """Compare the same case/rubric; keep uncertainty and absent human ratings explicit."""
    if not packets or len({p.case.id for p in packets}) != 1:
        raise ValueError("A comparison needs the same evaluation case")
    rows: list[dict[str, object]] = []
    for candidate in packets:
        ratings = candidate.ratings
        values = [ratings.factual, ratings.causal, ratings.visual, ratings.simplicity, ratings.transfer]
        complete = bool(
            candidate.outcome == "artifact"
            and ratings.reviewer.strip()
            and all(v is not None for v in values)
            and ratings.critical_error is not None
        )
        models = sorted({str(m) for r in candidate.usage for m in cast(list[object], r.get("models", []))})
        rows.append(
            {
                "lesson_id": candidate.lesson_id,
                "job_id": candidate.job_id,
                "outcome": candidate.outcome,
                "failure_type": candidate.failure_type,
                "failed_phase": candidate.failed_phase,
                "spec_sha256": candidate.spec_sha256,
                "models": models,
                "authoring_mode": candidate.authoring_mode,
                "revision_input_recorded_usd": sum(
                    float(str(r.get("charged_usd", 0))) for r in candidate.revision_input_usage
                )
                if candidate.revision_input_usage
                else None,
                "model_identity_estimated": any(
                    bool(r.get("model_identity_estimated", True)) for r in candidate.usage
                ),
                "cost_recorded_usd": sum(float(str(r.get("charged_usd", 0))) for r in candidate.usage)
                if candidate.usage
                else None,
                "reused_research_recorded_usd": sum(
                    float(str(r.get("charged_usd", 0))) for r in candidate.reused_research_usage
                )
                if candidate.reused_research_usage
                else None,
                "reused_draft_recorded_usd": sum(
                    float(str(r.get("charged_usd", 0))) for r in candidate.reused_draft_usage
                )
                if candidate.reused_draft_usage
                else None,
                "has_estimates": any(
                    bool(r.get("speech_estimated") or r.get("search_estimated")) for r in candidate.usage
                ),
                "billing_uncertain": any(bool(r.get("uncertain")) for r in candidate.usage),
                "structural_issues": candidate.structural_issues,
                "editorial_issues": candidate.editorial_issues,
                "human_review_complete": complete,
                "ratings": ratings.model_dump(),
                "quality_result": "generation_failed"
                if candidate.outcome == "generation_failed"
                else "unmeasured"
                if not complete
                else "needs-work"
                if ratings.critical_error or candidate.structural_issues or any(v == 0 for v in values)
                else "reviewed candidate; learning efficacy separate",
            }
        )
    return {
        "case": packets[0].case.id,
        "rows": rows,
        "note": "No automatic provider ranking or default switch. Compare equivalent tasks, include failures/abstentions and measure user learning separately.",
    }


def main() -> None:
    """CLI performs read-only exports/comparisons; no provider can be invoked here."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    export = sub.add_parser("packet")
    target = export.add_mutually_exclusive_group(required=True)
    target.add_argument("--lesson")
    target.add_argument("--job")
    export.add_argument("--case", required=True, choices=[c.id for c in cases()])
    export.add_argument("--output", type=Path, required=True)
    compare = sub.add_parser("compare")
    compare.add_argument("packets", type=Path, nargs="+")
    compare.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "packet":
        config = load_settings()
        store = Store(config.database_url, config.data_dir)
        candidate = (
            failed_packet(store, args.job, args.case) if args.job else packet(store, args.lesson, args.case)
        )
        result = candidate.model_dump(mode="json")
    else:
        result = comparison([EvaluationPacket.model_validate_json(p.read_text()) for p in args.packets])
    # Results deliberately stay outside the shared artifact and ordinary logs.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2))
    args.output.chmod(0o600)
    logger.info("Private evaluation output written", action=args.action)


if __name__ == "__main__":
    main()
