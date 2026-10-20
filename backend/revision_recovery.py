"""Explicit recovery of a completed draft after a failed, billed review request."""

import time

from pydantic import ValidationError

from .contracts import AuthorLessonSpec, LessonSpec
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
            or job.get("failed_phase") != "review"
            or job.get("failure_type") != "ModelUnavailableError"
            or job.get("revision_parent_sha256") != parent_sha
            or job.get("question") != question
            or job.get("user_id") != user_id
            or float(str(job.get("created_at", 0))) < time.time() - 7 * 86400
        ):
            continue
        receipts = [db.ledger.get(f"lesson:{id}:{phase}", {}) for phase in ("research", "author", "review")]
        if any(not r.get("models") or r.get("uncertain") for r in receipts):
            continue
        try:
            spec = AuthorLessonSpec.model_validate(job.get("spec"))
            evidence = ResearchSpec.model_validate(job.get("research"))
            require_evidence_sources(spec, evidence)
            require_learning_quality(spec)
        except (ValidationError, ValueError):
            continue
        return spec, evidence, id
    return None
