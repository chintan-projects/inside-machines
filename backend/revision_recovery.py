"""Explicit recovery of a completed draft after a failed, billed review request."""

import time
from typing import cast

from pydantic import ValidationError

from .accounting import receipt_origin
from .author_transport import expand_author
from .contracts import AuthorLessonSpec, LessonSpec
from .prompts import AUTHOR_POLICY
from .quality import require_learning_quality
from .research import ResearchSpec, require_evidence_sources
from .store import Database


def reusable_draft(
    db: Database, parent_sha: str, question: str, user_id: str
) -> tuple[LessonSpec, ResearchSpec, str] | None:
    """A fresh owner operation can review an intact draft without paying to reauthor.

    Never recover an editorial rejection, uncertain call, another member's work or
    a mismatched parent. Old failure records and their receipts remain immutable.
    """
    for id, job in reversed(list(db.jobs.items())):
        if (
            job.get("status") != "failed"
            or job.get("author_policy_sha256") != AUTHOR_POLICY
            or not (
                job.get("failed_phase") == "review"
                and job.get("failure_type") == "ModelUnavailableError"
                or job.get("failed_phase") == "author"
                and job.get("failure_type") == "ValidationError"
            )
            or job.get("revision_parent_sha256") != parent_sha
            or job.get("question") != question
            or job.get("user_id") != user_id
            or float(str(job.get("created_at", 0))) < time.time() - 7 * 86400
        ):
            continue
        if receipt_origin(db, id, "research") is None or receipt_origin(db, id, "author") is None:
            continue
        if job.get("failed_phase") == "review":
            receipt = db.ledger.get(f"lesson:{id}:review", {})
            if not receipt.get("models") or receipt.get("uncertain"):
                continue
        try:
            if job.get("failed_phase") == "author":
                outputs = cast(dict[str, dict[str, object]], job.get("call_outputs", {}))
                saved = outputs.get(f"lesson:{id}:author")
                if not saved or saved.get("bytes"):
                    continue
                raw = str(saved["value"])
                spec = (
                    expand_author(raw)
                    if job.get("author_protocol") == "compact-1"
                    else AuthorLessonSpec.model_validate_json(raw)
                )
            else:
                spec = AuthorLessonSpec.model_validate(job.get("spec"))
            if spec.canonical != job.get("canonical"):
                continue
            evidence = ResearchSpec.model_validate(job.get("research"))
            require_evidence_sources(spec, evidence)
            require_learning_quality(spec)
        except (ValidationError, ValueError):
            continue
        return spec, evidence, id
    return None
