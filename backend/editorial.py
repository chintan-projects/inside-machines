"""Bounded editorial findings guide a fresh, explicit authoring iteration."""

import time
from typing import cast

from pydantic import ValidationError

from .accounting import receipt_origin
from .author_transport import compact_author
from .contracts import AuthorLessonSpec, ReviewDecision
from .research import ResearchSpec
from .starters import digest_spec
from .store import Database


class EditorialReviewError(ValueError):
    """A model rejection is a finding, never a publication approval."""

    def __init__(self, notes: list[str]) -> None:
        """Keep owner diagnostics bounded and separate from ordinary logs."""
        super().__init__("Automated editorial review rejected the draft")
        self.notes = [note[:400] for note in notes[:10]]


def _rejection(id: str, job: dict[str, object]) -> tuple[AuthorLessonSpec, ReviewDecision] | None:
    if (
        job.get("status") != "failed"
        or job.get("failed_phase") != "review"
        or job.get("review_protocol") != "verdict-1"
    ):
        return None
    outputs = cast(dict[str, dict[str, object]], job.get("call_outputs", {}))
    saved = outputs.get(f"lesson:{id}:review")
    if not saved or saved.get("bytes"):
        return None
    try:
        verdict = ReviewDecision.model_validate_json(str(saved["value"]))
        spec = AuthorLessonSpec.model_validate(job.get("spec"))
        if (
            spec.canonical != job.get("canonical")
            or verdict.accepted
            or not verdict.notes
            or verdict.spec_sha256 != digest_spec(spec)
        ):
            return None
    except ValidationError:
        return None
    return spec, verdict


def editorial_notes(id: str, job: dict[str, object]) -> list[str]:
    """Project bounded critique for owners without mutating historical failures."""
    rejected = _rejection(id, job)
    return [n[:400] for n in rejected[1].notes[:10]] if rejected else []


def latest_feedback(db: Database, parent_sha: str, question: str, user_id: str) -> dict[str, object] | None:
    """Read a known, SHA-bound rejection; never mix members or private chats."""
    for id, job in reversed(list(db.jobs.items())):
        if (
            job.get("status") != "failed"
            or job.get("failed_phase") != "review"
            or job.get("review_protocol") != "verdict-1"
            or job.get("revision_parent_sha256") != (parent_sha or None)
            or job.get("question") != question
            or job.get("user_id") != user_id
            or float(str(job.get("created_at", 0))) < time.time() - 7 * 86400
        ):
            continue
        receipt = db.ledger.get(f"lesson:{id}:review", {})
        if not receipt.get("models") or receipt.get("uncertain") or receipt_origin(db, id, "author") is None:
            continue
        rejected = _rejection(id, job)
        if rejected is None:
            continue
        spec, verdict = rejected
        return {
            "job_id": id,
            "spec_sha256": digest_spec(spec),
            "notes": [n[:400] for n in verdict.notes[:10]],
            "draft": spec.model_dump(mode="json"),
        }
    return None


def author_feedback(value: object, evidence: ResearchSpec | None) -> dict[str, object] | None:
    """Reuse scene context only when its evidence table still matches exactly."""
    if not isinstance(value, dict):
        return None
    spec = AuthorLessonSpec.model_validate(value.get("draft"))
    if value.get("spec_sha256") != digest_spec(spec):
        raise ValueError("Editorial feedback refers to another draft")
    output: dict[str, object] = {
        "rejected_draft_sha256": value["spec_sha256"],
        "notes": value.get("notes", []),
    }
    if evidence and [str(s.url) for s in spec.sources] == [str(s.url) for s in evidence.sources]:
        output["previous_draft"] = compact_author(spec)
    else:
        output["note"] = (
            "Evidence changed. Use critique as design constraints; ground the new scene in the current source table."
        )
    return output
