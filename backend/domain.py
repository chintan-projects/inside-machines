"""Catalog lookup, transactional job admission, and private-session accounting."""

import hashlib
import re
import secrets
import time
from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel

from .accounting import receipt_origin
from .author_iteration import iteration_digest, reusable_iteration
from .concept_guides import guide_for
from .contracts import LessonSpec, canonicalize
from .depth_authoring import DepthRole, depth_context
from .editorial import latest_feedback
from .prompts import AUTHOR_POLICY
from .quality import learning_issues
from .research import reusable_research
from .revision_recovery import reusable_draft
from .settings import Settings
from .starters import digest_spec
from .store import Database, Store
from .stored_lessons import components_for, current_lesson, parse_stored_spec


class User(BaseModel):
    """The browser sees its own identity, never another session's bearer token."""

    id: str
    name: str
    owner: bool
    guest: bool = False


class Domain:
    """Application rules use one transaction for lookup, deduplication, and reservation."""

    def __init__(self, store: Store, settings: Settings) -> None:
        """Bind the durable domain repository."""
        self.store, self.settings = store, settings

    @staticmethod
    def event(db: Database, kind: str, user: User, **fields: object) -> None:
        """Store bounded alpha telemetry without private chat text."""
        db.events.append({"kind": kind, "user_id": user.id, "at": time.time(), **fields})

    def catalog(self, *, include_depth: bool = False, include_native_drafts: bool = False) -> list[dict[str, object]]:
        """Project public metadata only; never return owner job data or private chat."""

        def read(db: Database) -> list[dict[str, object]]:
            from .learning_reviews import review_state
            from .public_preview import public_preview_identity

            result = []
            for lesson in db.lessons.values():
                if lesson.get("archived"):
                    continue
                if lesson.get("depth_parent") and not include_depth:
                    continue
                spec = parse_stored_spec(lesson["spec"])
                if spec.version == 3 and not include_native_drafts:
                    from .stored_lessons import native_visible
                    if not native_visible(db, str(lesson["id"]), False):
                        continue
                result.append(
                    {
                        "id": lesson["id"],
                        "title": spec.title,
                        "canonical": spec.canonical,
                        "question": spec.question,
                        "summary": spec.summary,
                        "family": spec.family,
                        "depth_parent": lesson.get("depth_parent"),
                        "depth_role": lesson.get("depth_role"),
                        "category": spec.category,
                        "accent": spec.accent,
                        "duration": sum(s.duration for s in spec.stages),
                        "parts": len(components_for(spec)),
                        "quality": lesson.get("quality", "generated"),
                        "public_preview": public_preview_identity(db, str(lesson["id"])),
                        "review_needed": bool(learning_issues(spec))
                        or not review_state(db, str(lesson["id"]))["ready"],
                        "created_at": lesson.get("created_at", 0),
                        "views": lesson.get("views", 0),
                        "video_ready": bool(lesson.get("video")),
                        "preview": spec.model_dump(mode="json"),
                    }
                )
            return sorted(result, key=lambda item: float(str(item["created_at"])), reverse=True)

        return self.store.transaction(read, write=False)

    def request(
        self, question: str, user: User, *, revision_of: str | None = None, operation: str = "",
        node_parent: str | None = None, node_role: DepthRole | None = None,
        owner_build: bool = False,
    ) -> dict[str, object]:
        """Return a cached lesson, attach to a pending job, or atomically admit new work."""
        canonical = canonicalize(question)
        if user.guest:
            raise HTTPException(403, "Public visitors can request curated topics; only the owner can authorize a build")
        if owner_build and not user.owner:
            raise HTTPException(403, "Owner access is required")
        if owner_build and (revision_of or node_parent or node_role
                            or not re.fullmatch(r"[a-zA-Z0-9-]{8,80}", operation)):
            raise HTTPException(422, "A bounded, independent owner-build operation ID is required")
        if not canonical:
            raise HTTPException(422, "Tell us which concept you want to understand.")
        if node_parent is not None or node_role is not None:
            if not user.owner:
                raise HTTPException(403, "Owner access is required")
            if revision_of or not node_parent or node_role not in ("insight", "model"):
                raise HTTPException(422, "Choose one core and a valid independent depth role")
            if not re.fullmatch(r"[a-zA-Z0-9-]{8,80}", operation) or not 8 <= len(question.strip()) <= 180:
                raise HTTPException(422, "A bounded depth question and operation ID are required")
            canonical = node_parent[:55].rstrip("-") + "-depth-" + hashlib.sha256(
                (node_parent + ":" + operation).encode()
            ).hexdigest()[:12]
        if revision_of:
            if not user.owner:
                raise HTTPException(403, "Owner access is required")
            if not operation or len(operation) > 80:
                raise HTTPException(422, "A bounded revision operation ID is required")
            canonical = (
                canonical[:60].rstrip("-")
                + "-ce-"
                + hashlib.sha256((revision_of + ":" + operation).encode()).hexdigest()[:10]
            )

        def admit(db: Database) -> dict[str, object]:
            parent = db.lessons.get(revision_of) if revision_of else None
            if parent and parse_stored_spec(parent["spec"]).version == 3:
                raise HTTPException(422, "Native artwork revisions are prepared through the trusted local production workflow; request an owner-authored native revision.")
            context = None
            if owner_build:
                for previous in db.jobs.values():
                    if (not previous.get("owner_build") or previous.get("user_id") != user.id
                            or previous.get("owner_operation") != operation):
                        continue
                    if previous.get("question") != question:
                        raise HTTPException(409, "This operation already belongs to another owner-build intent")
                    if previous["status"] == "failed":
                        raise HTTPException(409, "That build attempt failed. Start a new operation explicitly to try again.")
                    if previous["status"] == "complete":
                        lesson_id = previous.get("lesson_id")
                        if lesson_id and lesson_id in db.lessons:
                            return {"kind": "lesson", "lesson_id": lesson_id, "reused": True}
                        raise HTTPException(409, "That build needs owner recovery; no new work was admitted")
                    return {"kind": "job", "job_id": previous["id"], "reused": True}
            if node_parent:
                core = db.lessons.get(node_parent)
                if core is None:
                    raise HTTPException(404, "Core lesson not found")
                if core.get("archived") or core.get("superseded_by"):
                    raise HTTPException(409, "Open the active core revision before authoring depth")
                if parse_stored_spec(core["spec"]).version == 3:
                    raise HTTPException(422, "Native depth is prepared through the trusted local production workflow; collect the follow-up request for owner curation.")
                assert node_role is not None
                try:
                    context = depth_context(node_parent, LessonSpec.model_validate(core["spec"]),
                                            question, node_role, canonical)
                except ValueError as exc:
                    raise HTTPException(422, "Depth authoring requires a compatible CE core lesson") from exc
                for depth_job in db.jobs.values():
                    if depth_job.get("node_parent") != node_parent or depth_job.get("node_operation") != operation:
                        continue
                    if depth_job.get("node_role") != node_role or depth_job.get("question") != question:
                        raise HTTPException(409, "This operation already belongs to another depth-draft intent")
                    if depth_job["status"] == "failed":
                        raise HTTPException(409, "That depth-draft attempt failed. Start a new operation explicitly to try again.")
                    if depth_job["status"] == "complete":
                        lesson_id = depth_job.get("lesson_id")
                        if lesson_id and lesson_id in db.lessons:
                            return {"kind": "lesson", "lesson_id": lesson_id, "reused": True}
                        raise HTTPException(409, "That depth draft needs owner recovery; no new work was admitted")
                    return {"kind": "job", "job_id": depth_job["id"], "reused": True}
            if revision_of:
                if parent is None:
                    raise HTTPException(404, "Lesson not found")
                if parent.get("superseded_by"):
                    existing = db.lessons.get(canonical)
                    if existing:
                        return {"kind": "lesson", "lesson_id": canonical, "reused": True}
                    raise HTTPException(409, "Open the latest revision before requesting another draft")
                for pending in db.jobs.values():
                    if pending.get("revision_of") == revision_of and pending["status"] not in (
                        "failed",
                        "complete",
                    ):
                        return {"kind": "job", "job_id": pending["id"], "reused": True}
                    if pending["canonical"] == canonical and pending["status"] == "failed":
                        raise HTTPException(
                            409, "That revision attempt failed. Explicitly start a new operation to try again"
                        )
            for lesson in db.lessons.values():
                if lesson.get("depth_parent") and not node_parent:
                    continue
                spec = parse_stored_spec(lesson["spec"])
                names = {spec.canonical, *(canonicalize(a) for a in spec.aliases)}
                if canonical in names and (not (revision_of or node_parent) or spec.canonical == canonical):
                    # Keep every old query reusable even if a revised model omits its aliases.
                    latest = current_lesson(db, str(lesson["id"]), user.owner)
                    if latest is None:
                        continue
                    self.event(db, "catalog_hit", user, question=question, lesson_id=latest["id"])
                    return {"kind": "lesson", "lesson_id": latest["id"], "reused": True}
            for job in db.jobs.values():
                if job["canonical"] == canonical and job["status"] not in ("failed", "complete"):
                    if owner_build:
                        raise HTTPException(409, "A build of this topic is already in progress. Follow the existing attempt.")
                    self.event(db, "joined_job", user, question=question, job_id=job["id"])
                    return {"kind": "job", "job_id": job["id"], "reused": True}
            if not self.settings.generation_enabled:
                self.event(db, "requested_topic", user, question=question, canonical=canonical)
                return {
                    "kind": "unavailable",
                    "message": "Your request is saved. New explanations will be available once the owner connects AI generation and sets the alpha budget. Existing lessons still work.",
                }
            recent = [
                e
                for e in db.events
                if e.get("user_id") == user.id
                and e["kind"] == "generation_requested"
                and float(str(e["at"])) > time.time() - 3600
            ]
            if len(recent) >= self.settings.hourly_requests:
                raise HTTPException(
                    429, "You've reached the hourly alpha limit. Try an existing explanation."
                )
            reserve = self.settings.generation_reserve
            if db.spent + db.reserved + reserve > self.settings.budget_usd:
                self.event(db, "budget_block", user, canonical=canonical)
                return {
                    "kind": "budget",
                    "message": "The alpha's generation budget is reserved or used. You can still explore every existing explanation.",
                }
            parent_sha = digest_spec(LessonSpec.model_validate(parent["spec"])) if parent else ""
            draft = reusable_draft(db, parent_sha, question, user.id) if parent else None
            recovered = reusable_research(db, parent_sha, question, user.id) if parent else None
            feedback = latest_feedback(db, parent_sha, question, user.id) if parent else None
            concept_guide = guide_for(context.path.title + " " + question if context else question).id
            iteration = (reusable_iteration(db, question, user.id, concept_guide, context)
                         if user.owner and not parent and (context or owner_build) else None)
            if iteration:
                recovered = iteration.evidence, iteration.evidence_origin
                feedback = iteration.feedback
            job_id = secrets.token_urlsafe(18)
            db.jobs[job_id] = {
                "id": job_id,
                "canonical": canonical,
                "question": question,
                "user_id": user.id,
                "status": "queued",
                "phase": "review" if draft else "author" if recovered else "queued",
                "pipeline_version": "evidence-first-1",
                "review_protocol": "verdict-1",
                "author_protocol": "compact-1",
                "revision_protocol": "patch-1",
                "concept_guide": concept_guide,
                "author_policy_sha256": AUTHOR_POLICY,
                "editorial_feedback": feedback,
                "iteration_from": iteration.feedback["job_id"] if iteration else None,
                "iteration_sha256": iteration_digest(iteration) if iteration else None,
                "owner_build": owner_build,
                "owner_operation": operation if owner_build else None,
                "message": "Reviewing the saved visual explanation"
                if draft
                else "Using saved evidence; building the visual explanation"
                if recovered
                else "Waiting to build your explanation",
                "created_at": time.time(),
                "updated_at": time.time(),
                "lease_until": 0,
                "lease_token": "",
                "attempts": 0,
                "receipt": {},
                "spec": draft[0].model_copy(update={"canonical": canonical}).model_dump(mode="json")
                if draft
                else None,
                "audio": [],
                "video": None,
                "cost_usd": 0,
                "error": None,
                "reservation": reserve,
                "revision_of": revision_of,
                "revision_parent_sha256": parent_sha or None,
                "node_parent": node_parent,
                "node_role": node_role,
                "node_operation": operation if context else None,
                "path_context": context.model_dump(mode="json") if context else None,
                "research": draft[1].model_dump(mode="json")
                if draft
                else recovered[0].model_dump(mode="json")
                if recovered
                else None,
                "research_reused_from": receipt_origin(db, draft[2], "research")
                if draft
                else recovered[1]
                if recovered
                else None,
                "draft_reused_from": receipt_origin(db, draft[2], "author") if draft else None,
                "draft_checkpoint_from": draft[2] if draft else None,
                "draft_reused_spec_sha256": digest_spec(draft[0]) if draft else None,
            }
            db.reserved += reserve
            self.event(
                db, "generation_requested", user, question=question, job_id=job_id, canonical=canonical
            )
            return {"kind": "job", "job_id": job_id, "reused": False}

        return self.store.transaction(admit)

    def job(self, job_id: str) -> dict[str, object]:
        """Family members may see job progress, not requester identity or private details."""

        def read(db: Database) -> dict[str, object]:
            job = db.jobs.get(job_id)
            if not job:
                raise HTTPException(404, "Explanation request not found")
            return {
                key: job.get(key)
                for key in (
                    "id",
                    "canonical",
                    "status",
                    "phase",
                    "pipeline_version",
                    "message",
                    "created_at",
                    "updated_at",
                    "error",
                    "lesson_id",
                )
            }

        return self.store.transaction(read, write=False)

    def feedback(
        self,
        lesson_id: str,
        value: Literal["up", "down"],
        reason: str,
        user: User,
        *,
        stage: int | None = None,
    ) -> None:
        """Update one family member's response without equating votes with verification."""

        def update(db: Database) -> None:
            if lesson_id not in db.lessons:
                raise HTTPException(404, "Lesson not found")
            from .stored_lessons import native_visible
            if not native_visible(db, lesson_id, user.owner):
                raise HTTPException(404, "Lesson not found")
            spec = parse_stored_spec(db.lessons[lesson_id]["spec"])
            if stage is not None and not 0 <= stage < len(spec.stages):
                raise HTTPException(422, "Feedback refers to an unknown lesson step")
            db.feedback[f"{user.id}:{lesson_id}"] = {
                "lesson_id": lesson_id,
                "user_id": user.id,
                "value": value,
                "reason": reason,
                "stage": stage,
                "version": spec.version,
                "at": time.time(),
            }
            self.event(db, "feedback", user, lesson_id=lesson_id, value=value)

        self.store.transaction(update)

    def settle(self, db: Database, job: dict[str, object], status: str, error: str | None = None) -> None:
        """Release a reservation exactly once, preserving the actual usage ledger."""
        if job["status"] in ("complete", "failed"):
            return
        db.reserved = max(0, db.reserved - float(str(job["reservation"])))
        job.update(status=status, error=error, updated_at=time.time(), lease_until=0)
