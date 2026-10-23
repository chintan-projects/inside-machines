"""Explicit owner iteration reuses evidence and findings, never a rejected result."""

import hashlib
import json
import time
from dataclasses import dataclass
from typing import cast

from pydantic import ValidationError

from .author_transport import expand_author
from .contracts import AuthorLessonSpec
from .depth_authoring import DepthContext, job_depth_context
from .editorial import author_feedback, rejected_draft
from .lesson_patch import apply_revision
from .prompts import AUTHOR_POLICY
from .quality import learning_issues
from .research import ResearchSpec, require_evidence_sources
from .starters import digest_spec
from .store import Database


@dataclass(frozen=True)
class AuthorIteration:
    """Trusted admission data; another paid author and all release gates remain required."""

    evidence: ResearchSpec
    evidence_origin: str
    feedback: dict[str, object]


def _scope_matches(job: dict[str, object], db: Database, question: str, user_id: str,
                   guide: str, context: DepthContext | None) -> bool:
    if (job.get("revision_of") or job.get("revision_parent_sha256")
            or job.get("question") != question or job.get("user_id") != user_id
            or job.get("concept_guide") != guide or job.get("author_policy_sha256") != AUTHOR_POLICY
            or float(str(job.get("created_at", 0))) < time.time() - 7 * 86400):
        return False
    old = job_depth_context(job, db)
    if context is None:
        return old is None
    return bool(old and old.parent_lesson_id == context.parent_lesson_id
                and old.parent_spec_sha256 == context.parent_spec_sha256 and old.role == context.role)


def _completed_receipt(db: Database, job_id: str, phase: str) -> bool:
    receipt = db.ledger.get(f"lesson:{job_id}:{phase}", {})
    return bool(receipt.get("models") and receipt.get("uncertain") is False
                and receipt.get("billing_complete") is not False
                and receipt.get("response_status") == "completed"
                and not receipt.get("incomplete_reason"))


def _evidence_origin(db: Database, job_id: str, evidence: ResearchSpec, question: str,
                     user_id: str, guide: str, context: DepthContext | None) -> str | None:
    seen: set[str] = set()
    while job_id and job_id not in seen:
        seen.add(job_id)
        job = db.jobs.get(job_id, {})
        if not _scope_matches(job, db, question, user_id, guide, context):
            return None
        if ResearchSpec.model_validate(job.get("research")) != evidence:
            return None
        if f"lesson:{job_id}:research" in db.ledger:
            return job_id if _completed_receipt(db, job_id, "research") else None
        job_id = str(job.get("research_reused_from") or "")
    return None


def _candidate(db: Database, job_id: str, question: str, user_id: str, guide: str,
               context: DepthContext | None) -> AuthorIteration | None:
    job = db.jobs.get(job_id, {})
    if job.get("status") != "failed" or not _scope_matches(job, db, question, user_id, guide, context):
        return None
    evidence = ResearchSpec.model_validate(job.get("research"))
    origin = _evidence_origin(db, job_id, evidence, question, user_id, guide, context)
    if origin is None or not _completed_receipt(db, job_id, "author"):
        return None
    if job.get("failed_phase") == "author" and job.get("failure_type") == "LearningQualityError":
        if job.get("author_mode") not in ("compact", "full", "patch"):
            return None
        outputs = cast(dict[str, dict[str, object]], job.get("call_outputs", {}))
        saved = outputs.get(f"lesson:{job_id}:author")
        if not saved or saved.get("bytes") or not isinstance(saved.get("value"), str):
            return None
        raw = str(saved["value"])
        if saved.get("sha256") not in (None, hashlib.sha256(raw.encode()).hexdigest()):
            return None
        if job.get("author_mode") == "patch":
            feedback = author_feedback(job.get("editorial_feedback"), evidence)
            if not feedback or "previous_draft" not in feedback:
                return None
            base = expand_author(json.dumps(feedback["previous_draft"]))
            spec = apply_revision(raw, base, str(job["canonical"]))
        else:
            spec = (expand_author(raw) if job.get("author_protocol") == "compact-1"
                    else AuthorLessonSpec.model_validate_json(raw))
        notes = learning_issues(spec)
        if not notes or job.get("rejected_spec_sha256") not in (None, digest_spec(spec)):
            return None
    elif (job.get("failed_phase") == "review" and job.get("failure_type") == "EditorialReviewError"
          and _completed_receipt(db, job_id, "review")):
        rejection = rejected_draft(job_id, job)
        if rejection is None:
            return None
        spec, verdict = rejection
        notes = [*verdict.notes, *learning_issues(spec)]
    else:
        return None
    if spec.canonical != job.get("canonical"):
        return None
    require_evidence_sources(spec, evidence)
    return AuthorIteration(evidence, origin, {
        "job_id": job_id, "spec_sha256": digest_spec(spec),
        "notes": [note[:400] for note in list(dict.fromkeys(notes))[:10]],
        "draft": spec.model_dump(mode="json"),
    })


def reusable_iteration(db: Database, question: str, user_id: str, guide: str,
                       context: DepthContext | None) -> AuthorIteration | None:
    """Select a completed, accounted rejection only for a fresh explicit owner operation.

    Stored provider checkpoints are trusted server records, never client input. New
    outputs carry a byte hash; historical records are parsed and SHA-bound at admission.
    No old job, receipt, source or published lesson is changed by selection.
    """
    for job_id in reversed(db.jobs):
        try:
            result = _candidate(db, job_id, question, user_id, guide, context)
        except (ValidationError, ValueError, KeyError, TypeError):
            continue
        if result is not None:
            return result
    return None


def validate_iteration(job: dict[str, object], db: Database, context: DepthContext | None) -> None:
    """Recheck frozen findings, source provenance and scope before the new paid author call."""
    source = job.get("iteration_from")
    if source is None and job.get("iteration_sha256") is None:
        return
    try:
        result = _candidate(db, str(source), str(job["question"]), str(job["user_id"]),
                            str(job["concept_guide"]), context)
        valid = bool(result and job.get("editorial_feedback") == result.feedback
                     and job.get("research") == result.evidence.model_dump(mode="json")
                     and job.get("research_reused_from") == result.evidence_origin
                     and job.get("iteration_sha256") == iteration_digest(result))
    except (ValidationError, ValueError, KeyError, TypeError):
        valid = False
    if not valid:
        raise ValueError("The author iteration no longer matches its completed draft, evidence and scope")


def iteration_digest(iteration: AuthorIteration) -> str:
    """Bind the rejected draft, recomputed findings and exact research checkpoint together."""
    return hashlib.sha256(json.dumps({
        "feedback": iteration.feedback, "research": iteration.evidence.model_dump(mode="json"),
        "research_reused_from": iteration.evidence_origin,
    }, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
