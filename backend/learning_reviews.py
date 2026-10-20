"""Owner-recorded evidence, separate from immutable lessons and private answers."""

import time
from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .contracts import LessonSpec
from .domain import User
from .quality import learning_issues
from .starters import digest_spec
from .store import Database, Store

Gate = Literal["engineering", "technical", "craft", "learning", "release"]


class LearnerScore(BaseModel):
    """An anonymized, human-assessed rubric result; never an answer transcript."""

    model_config = ConfigDict(extra="forbid")
    participant: str = Field(pattern=r"^anon-[a-z0-9-]{1,24}$")
    baseline: int = Field(ge=0, le=2)
    causal: int = Field(ge=0, le=2)
    transfer: int = Field(ge=0, le=2)
    retention: int | None = Field(default=None, ge=0, le=2)


class ReviewSubmission(BaseModel):
    """Explicit owner assertion binds method, evidence and decision to artifact hashes."""

    model_config = ConfigDict(extra="forbid")
    spec_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    video_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    bundle_sha256: str = Field(default="", pattern=r"^(?:|[a-f0-9]{64})$")
    gate: Gate
    reviewer: str = Field(min_length=2, max_length=100)
    method: Literal["human", "agent"]
    decision: Literal["pass", "needs-work"]
    evidence: str = Field(min_length=20, max_length=1200)
    independent: bool = False
    real_device: bool = False
    device: str = Field(default="", max_length=120)
    scores: list[LearnerScore] = Field(default_factory=list, max_length=30)

    @model_validator(mode="after")
    def honest_evidence(self) -> "ReviewSubmission":
        """Prevent automated review or existing knowledge from satisfying human gates."""
        if len({s.participant for s in self.scores}) != len(self.scores):
            raise ValueError("Learner IDs must be distinct")
        if self.gate != "learning" and self.scores:
            raise ValueError("Only the learning review accepts anonymized rubric scores")
        if self.decision == "pass":
            if self.gate != "engineering" and self.method != "human":
                raise ValueError("This gate requires human evidence")
            if self.gate == "technical" and not self.independent:
                raise ValueError("Technical approval needs an independent reviewer")
            if self.gate == "craft" and (not self.real_device or not self.device.strip()):
                raise ValueError("Craft approval needs an actual phone walkthrough and device")
            if self.gate == "learning":
                eligible = [s for s in self.scores if s.baseline < 2]
                passed = [s for s in eligible if s.causal == 2 and s.transfer == 2]
                if len(eligible) < 5 or len(passed) / len(eligible) < 0.8:
                    raise ValueError(
                        "Learning gate needs >=5 initially unfamiliar beginners and >=80% with causal and transfer scores of 2"
                    )
        return self


def _review_state(db: Database, lesson_id: str, bundle_sha256: str,
                  bundle_issues: list[str], branches_ready: bool) -> dict[str, object]:
    """Select exact artifact/bundle evidence; old approvals remain immutable history."""
    lesson = db.lessons.get(lesson_id)
    if lesson is None:
        raise HTTPException(404, "Lesson not found")
    spec = LessonSpec.model_validate(lesson["spec"])
    digest, video = digest_spec(spec), str(lesson.get("video_sha256", ""))
    records = [
        r
        for r in db.learning_reviews
        if r.get("lesson_id") == lesson_id
        and r.get("spec_sha256") == digest
        and r.get("video_sha256") == video
        and r.get("bundle_sha256", "") == bundle_sha256
    ]
    gates: dict[str, bool] = {k: False for k in ("engineering", "technical", "craft", "learning", "release")}
    latest: dict[str, dict[str, object]] = {}
    for record in records:
        latest[str(record["gate"])] = record
    for gate, record in latest.items():
        gates[gate] = record.get("decision") == "pass"
    structural = learning_issues(spec)
    prerequisites = not structural and not bundle_issues and branches_ready and all(
        gates[k] for k in ("engineering", "technical", "craft", "learning")
    )
    release = latest.get("release")
    if release and any(
        float(str(r["at"])) > float(str(release["at"])) for k, r in latest.items() if k != "release"
    ):
        gates["release"] = False
    ready = bool(spec.version == 2 and video and prerequisites and gates["release"])
    return {
        "lesson_id": lesson_id,
        "spec_sha256": digest,
        "video_sha256": video,
        "bundle_sha256": bundle_sha256,
        "bundle_issues": bundle_issues,
        "branches_ready": branches_ready,
        "spec_version": spec.version,
        "structural_issues": structural,
        "gates": gates,
        "can_release": bool(prerequisites and spec.version == 2 and video),
        "ready": ready,
        "records": records,
        "recording_note": "Evidence is recorded by the owner. The app verifies binding and rubric rules, not reviewer identity or scientific certification.",
    }


def standalone_review_state(db: Database, lesson_id: str) -> dict[str, object]:
    """Retain a core's prior artifact approval while its new graph is being reviewed."""
    return _review_state(db, lesson_id, "", [], True)


def review_state(db: Database, lesson_id: str) -> dict[str, object]:
    """Changing a path or its leaf approvals cannot retain the old release verdict."""
    from .path_publication import bundle_binding

    binding = bundle_binding(db, lesson_id)
    branches_ready = True
    if binding.path and not binding.issues:
        branches_ready = all(
            standalone_review_state(db, node.lesson_id)["ready"] for node in binding.path.nodes[1:]
        )
    return _review_state(db, lesson_id, binding.sha256, binding.issues, branches_ready)


class LearningReviews:
    """Short atomic evidence writes never invoke models or alter published content."""

    def __init__(self, store: Store) -> None:
        """Use the existing shared domain repository."""
        self.store = store

    def record(self, lesson_id: str, submission: ReviewSubmission, user: User) -> dict[str, object]:
        """Append bounded review evidence, leaving history and lesson bytes immutable."""
        if not user.owner:
            raise HTTPException(403, "Owner access is required")

        def write(db: Database) -> dict[str, object]:
            current = review_state(db, lesson_id)
            if (
                submission.spec_sha256 != current["spec_sha256"]
                or submission.video_sha256 != current["video_sha256"]
                or not current["video_sha256"]
                or submission.bundle_sha256 != current["bundle_sha256"]
            ):
                raise HTTPException(409, "Review must match this exact lesson, completed video and learning bundle")
            if current["bundle_issues"]:
                raise HTTPException(409, "Repair the learning-path artifact bindings before recording a review")
            if submission.gate == "release" and submission.decision == "pass" and not current["can_release"]:
                raise HTTPException(
                    409,
                    "Engineering, independent technical, actual-phone craft and beginner-learning evidence are required first",
                )
            count = sum(r.get("lesson_id") == lesson_id for r in db.learning_reviews)
            if count >= 100:
                raise HTTPException(
                    422, "This revision has reached its review-record limit; start a new revision"
                )
            db.learning_reviews.append(
                {
                    **submission.model_dump(mode="json"),
                    "lesson_id": lesson_id,
                    "at": time.time(),
                    "recorded_by": user.id,
                }
            )
            from .interests import notify_available
            notify_available(db, lesson_id)
            return review_state(db, lesson_id)

        return self.store.transaction(write)
