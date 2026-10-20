"""Create comparable private review packets without dispatching paid model calls."""

import argparse
import json
from pathlib import Path
from typing import cast

from _shared.services.logger import get_logger
from pydantic import BaseModel, ConfigDict, Field

from .contracts import LessonSpec
from .quality import learning_issues
from .settings import ROOT, load_settings
from .starters import digest_spec
from .store import Store

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
    spec: LessonSpec
    structural_issues: list[str]
    usage: list[dict[str, object]]
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
    keys = (
        "operation",
        "models",
        "input_tokens",
        "output_tokens",
        "search_calls",
        "cost_usd",
        "charged_usd",
        "speech_estimated",
        "uncertain",
    )
    usage = [
        {key: row[key] for key in keys if key in row}
        for operation, row in db.ledger.items()
        if any(operation.startswith(f"lesson:{job}:") for job in jobs)
    ]
    return EvaluationPacket(
        case=case,
        lesson_id=lesson_id,
        spec_sha256=digest_spec(spec),
        video_sha256=str(lesson.get("video_sha256", "")),
        spec=spec,
        structural_issues=learning_issues(spec),
        usage=usage,
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
            ratings.reviewer.strip()
            and all(v is not None for v in values)
            and ratings.critical_error is not None
        )
        models = sorted({str(m) for r in candidate.usage for m in cast(list[object], r.get("models", []))})
        rows.append(
            {
                "lesson_id": candidate.lesson_id,
                "spec_sha256": candidate.spec_sha256,
                "models": models,
                "cost_recorded_usd": sum(float(str(r.get("charged_usd", 0))) for r in candidate.usage)
                if candidate.usage
                else None,
                "has_estimates": any(bool(r.get("speech_estimated")) for r in candidate.usage),
                "billing_uncertain": any(bool(r.get("uncertain")) for r in candidate.usage),
                "structural_issues": candidate.structural_issues,
                "human_review_complete": complete,
                "ratings": ratings.model_dump(),
                "quality_result": "unmeasured"
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
    export.add_argument("--lesson", required=True)
    export.add_argument("--case", required=True, choices=[c.id for c in cases()])
    export.add_argument("--output", type=Path, required=True)
    compare = sub.add_parser("compare")
    compare.add_argument("packets", type=Path, nargs="+")
    compare.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "packet":
        config = load_settings()
        result = packet(Store(config.database_url, config.data_dir), args.lesson, args.case).model_dump(
            mode="json"
        )
    else:
        result = comparison([EvaluationPacket.model_validate_json(p.read_text()) for p in args.packets])
    # Results deliberately stay outside the shared artifact and ordinary logs.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2))
    args.output.chmod(0o600)
    logger.info("Private evaluation output written", action=args.action)


if __name__ == "__main__":
    main()
