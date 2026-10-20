"""Checkpointed lesson authoring, review, narration, and deterministic video jobs."""

import asyncio
import base64
import hashlib
import secrets
import time
from collections.abc import Awaitable, Callable
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

from _shared.services.logger import get_logger
from _shared.services.state_manager import StateManager
from pydantic import ValidationError

from .accounting import charge
from .assets import Assets
from .contracts import AuthorLessonSpec, LessonSpec, ReviewSpec, TeachingReviewSpec
from .domain import Domain
from .prompts import lesson_prompt, review_prompt
from .provider import UsageReceipt, model_speech, model_text, receipt_context
from .quality import LearningQualityError, require_learning_quality
from .render import audio_duration, render_video
from .research import ResearchSpec, require_evidence_sources, research_prompt
from .settings import Settings
from .starters import digest_spec
from .store import Database, Store

logger = get_logger(__name__)
Enqueue = Callable[[str, str], Awaitable[None]]


class Pipeline:
    """Each queue delivery runs one bounded phase, then durably schedules the next."""

    def __init__(self, store: Store, settings: Settings, assets: Assets, enqueue: Enqueue) -> None:
        """Bind portable adapters, leaving the shared services unmodified."""
        self.store, self.settings, self.assets, self.enqueue = store, settings, assets, enqueue
        self.domain = Domain(store, settings)
        self.checkpoints = StateManager(settings.data_dir / "checkpoints")

    def _claim(self, job_id: str) -> dict[str, object] | None:
        def claim(db: Database) -> dict[str, object] | None:
            job = db.jobs.get(job_id)
            if not job or job["status"] in ("failed", "complete"):
                return None
            if float(str(job["lease_until"])) > time.time():
                raise RuntimeError("This job phase is still leased; retry delivery later")
            if job.get("inflight"):
                # A killed worker may already have incurred a bill. Do not pay again.
                key = str(job["inflight"])
                allowance = float(str(job.get("allowance", 0)))
                charge(db, key, UsageReceipt(), allowance, uncertain=True)
                job["reservation"] = max(0, float(str(job["reservation"])) - allowance)
                self.domain.settle(
                    db,
                    job,
                    "failed",
                    "The previous generation step was interrupted. Its cost allowance is retained until the owner reconciles provider billing.",
                )
                return None
            job.update(
                status="running",
                lease_token=secrets.token_urlsafe(18),
                lease_until=time.time() + self.settings.lease_seconds,
                updated_at=time.time(),
            )
            if job["phase"] == "queued":
                if f"lesson:{job_id}:author" in cast(dict[str, object], job.get("call_outputs", {})):
                    job["message"] = "Resuming the completed scene authoring"
                else:
                    job["pipeline_version"] = "evidence-first-1"
                    job["message"] = "Researching the machine and its supporting evidence"
            return dict(job)

        return self.store.transaction(claim)

    def _heartbeat(self, job_id: str, lease: str) -> None:
        def update(db: Database) -> None:
            job = db.jobs[job_id]
            if job["lease_token"] != lease or job["status"] != "running":
                raise RuntimeError("Job lease was lost")
            job.update(lease_until=time.time() + self.settings.lease_seconds, updated_at=time.time())

        self.store.transaction(update)

    def _begin_call(self, job_id: str, lease: str, phase: str, allowance: float) -> str:
        key = f"lesson:{job_id}:{phase}"

        def update(db: Database) -> None:
            job = db.jobs[job_id]
            if job["lease_token"] != lease:
                raise RuntimeError("Job lease was lost")
            if float(str(job["reservation"])) < allowance:
                raise RuntimeError("This job has insufficient reserved budget")
            job.update(inflight=key, allowance=allowance)

        self.store.transaction(update)
        return key

    def _finish_call(
        self,
        job_id: str,
        lease: str,
        key: str,
        receipt: UsageReceipt,
        *,
        failed: bool,
        result: str | bytes | None,
    ) -> None:
        def settle(db: Database) -> None:
            job = db.jobs[job_id]
            if job["lease_token"] != lease:
                raise RuntimeError("Job lease was lost")
            allowance = float(str(job["allowance"]))
            cost = charge(db, key, receipt, allowance, uncertain=failed and not receipt.models)
            job.update(
                inflight="",
                allowance=0,
                reservation=max(0, float(str(job["reservation"])) - allowance),
                cost_usd=float(str(job["cost_usd"])) + cost,
            )
            if result is not None:
                outputs = cast(dict[str, dict[str, object]], job.setdefault("call_outputs", {}))
                outputs[key] = {
                    "bytes": isinstance(result, bytes),
                    "value": base64.b64encode(result).decode() if isinstance(result, bytes) else result,
                }

        self.store.transaction(settle)

    async def _paid(
        self, job: dict[str, object], phase: str, call: Callable[[], Awaitable[str | bytes]]
    ) -> str | bytes:
        allowance = (
            self.settings.research_phase_reserve
            if phase == "research"
            else self.settings.text_phase_reserve
            if phase in ("author", "review")
            else self.settings.speech_phase_reserve
        )
        job_id, lease = str(job["id"]), str(job["lease_token"])
        key = f"lesson:{job_id}:{phase}"
        outputs = cast(dict[str, dict[str, object]], job.get("call_outputs", {}))
        if key in outputs:
            saved = outputs[key]
            return base64.b64decode(str(saved["value"])) if saved["bytes"] else str(saved["value"])
        key = self._begin_call(job_id, lease, phase, allowance)
        receipt = UsageReceipt()
        token = receipt_context.set(receipt)
        failed = True
        result: str | bytes | None = None
        try:
            result = await call()
            failed = False
            return result
        finally:
            receipt_context.reset(token)
            self._finish_call(job_id, lease, key, receipt, failed=failed, result=result)

    def _advance(self, job: dict[str, object], phase: str, message: str, **fields: object) -> None:
        def update(db: Database) -> None:
            current = db.jobs[str(job["id"])]
            if current["lease_token"] != job["lease_token"]:
                raise RuntimeError("Job lease was lost")
            current.update(
                phase=phase,
                message=message,
                lease_until=0,
                lease_token="",
                updated_at=time.time(),
                call_outputs={},
                **fields,
            )

        self.store.transaction(update)

    async def run(self, job_id: str) -> None:
        """Resume a persisted phase; never publish a lesson without its video."""
        job = self._claim(job_id)
        if job is None:
            return
        phase = str(job["phase"])
        try:
            evidence = ResearchSpec.model_validate(job["research"]) if job.get("research") else None
            if job.get("pipeline_version") == "evidence-first-1" and phase != "queued" and evidence is None:
                raise ValueError("This phase requires its completed evidence checkpoint")
            if evidence and job.get("spec"):
                require_evidence_sources(LessonSpec.model_validate(job["spec"]), evidence)
            saved_author = f"lesson:{job_id}:author" in cast(dict[str, object], job.get("call_outputs", {}))
            if phase == "queued" and not saved_author:
                raw = await self._paid(
                    job,
                    "research",
                    lambda: model_text(
                        research_prompt(str(job["question"])),
                        self.settings,
                        schema=ResearchSpec.model_json_schema(),
                        task="research",
                    ),
                )
                researched = ResearchSpec.model_validate_json(raw)
                self._advance(
                    job,
                    "author",
                    "Building the visual explanation from the evidence",
                    research=researched.model_dump(mode="json"),
                )
            elif phase == "author" or (phase == "queued" and saved_author):
                raw = await self._paid(
                    job,
                    "author",
                    lambda: model_text(
                        lesson_prompt(str(job["question"]), str(job["canonical"]), evidence),
                        self.settings,
                        schema=AuthorLessonSpec.model_json_schema(),
                    ),
                )
                spec: LessonSpec = AuthorLessonSpec.model_validate_json(raw)
                if spec.canonical != job["canonical"]:
                    raise ValueError("Generated lesson changed its requested identity")
                if evidence:
                    require_evidence_sources(spec, evidence)
                require_learning_quality(spec)
                self._advance(
                    job,
                    "review",
                    "Checking the explanation and its moving parts",
                    spec=spec.model_dump(mode="json"),
                )
            elif phase == "review":
                spec = LessonSpec.model_validate(job["spec"])
                review_type = TeachingReviewSpec if spec.version == 2 else ReviewSpec
                raw = await self._paid(
                    job,
                    "review",
                    lambda: model_text(
                        review_prompt(spec),
                        self.settings,
                        schema=review_type.model_json_schema(),
                        task="review",
                    ),
                )
                review = review_type.model_validate_json(raw)
                if not review.accepted:
                    raise ValueError("Automated editorial check rejected this lesson")
                reviewed = review.lesson
                if job.get("research"):
                    require_evidence_sources(reviewed, ResearchSpec.model_validate(job["research"]))
                require_learning_quality(reviewed)
                if reviewed.canonical != job["canonical"]:
                    raise ValueError("Review changed the lesson identity")
                self._advance(
                    job,
                    "voice-0",
                    "Preparing the narrated explanation",
                    spec=reviewed.model_dump(mode="json"),
                )
            elif phase.startswith("voice-"):
                await self._voice(job, int(phase.split("-")[1]))
            elif phase == "video":
                await self._video(job)
                return
            else:
                raise ValueError("Unknown generation phase")
        except Exception as exc:
            # Queue entry boundary: preserve domain state for every adapter failure.
            logger.error("Lesson phase failed", job_id=job_id, phase=phase, error_type=type(exc).__name__)

            failure_type = type(exc).__name__
            quality_findings = list(exc.issues) if isinstance(exc, LearningQualityError) else []
            validation_findings = (
                [
                    ".".join(str(p) for p in e["loc"]) + ": " + e["type"]
                    for e in exc.errors(include_input=False, include_context=False, include_url=False)[:12]
                ]
                if isinstance(exc, ValidationError)
                else []
            )

            def fail(db: Database) -> None:
                current = db.jobs[job_id]
                if current["lease_token"] == job["lease_token"]:
                    current["failure_type"] = failure_type
                    current["failed_phase"] = phase
                    if validation_findings:
                        current["validation_issues"] = validation_findings
                    if quality_findings:
                        current["quality_issues"] = quality_findings
                    self.domain.settle(
                        db,
                        current,
                        "failed",
                        "We couldn't finish this explanation. The owner can inspect the failed step and its recorded cost.",
                    )

            self.store.transaction(fail)
            return
        await self.checkpoints.checkpoint({"job_id": job_id, "finished_phase": phase}, label="lesson-phase")
        # Outside phase error handling: dispatch failure must trigger a queue retry.
        current = self.domain.job(job_id)
        await self.enqueue(job_id, str(current["phase"]))

    async def _voice(self, job: dict[str, object], index: int) -> None:
        spec = LessonSpec.model_validate(job["spec"])
        if not 0 <= index < len(spec.stages):
            raise ValueError("Invalid narration stage")
        data = await self._paid(
            job, f"voice-{index}", lambda: model_speech(spec.stages[index].narration, self.settings)
        )
        if not isinstance(data, bytes):
            raise ValueError("Speech provider returned text")
        with TemporaryDirectory(prefix="inside-voice-") as tmp:
            audio = Path(tmp) / "voice.mp3"
            audio.write_bytes(data)
            duration = await asyncio.to_thread(audio_duration, audio)
        if duration > 24:
            raise ValueError("Narration exceeds the bounded stage duration")
        spec.stages[index].duration = max(5, duration + 0.6)
        location = await self.assets.put(f"lessons/{job['id']}/voice-{index}.mp3", data, "audio/mpeg")
        audio_locations = cast(list[str], job["audio"])
        audio_locations = [*audio_locations, location]
        next_phase = f"voice-{index + 1}" if index + 1 < len(spec.stages) else "video"
        self._advance(
            job,
            next_phase,
            "Rendering your visual explanation"
            if next_phase == "video"
            else f"Narrated {index + 1} of {len(spec.stages)} steps",
            spec=spec.model_dump(mode="json"),
            audio=audio_locations,
        )

    async def _video(self, job: dict[str, object]) -> None:
        spec = LessonSpec.model_validate(job["spec"])
        job_id, lease = str(job["id"]), str(job["lease_token"])
        with TemporaryDirectory(prefix="inside-video-") as tmp:
            folder = Path(tmp)
            audio = []
            for index, location in enumerate(cast(list[str], job["audio"])):
                path = folder / f"voice-{index}.mp3"
                path.write_bytes(await self.assets.read(location))
                audio.append(path)
            output = await asyncio.to_thread(
                render_video, spec, audio, folder, self.settings, lambda: self._heartbeat(job_id, lease)
            )
            data = output.read_bytes()
            video_digest = hashlib.sha256(data).hexdigest()
            location = await self.assets.put(f"lessons/{job_id}/lesson.mp4", data, "video/mp4")

        require_learning_quality(spec)

        def publish(db: Database) -> None:
            current = db.jobs[job_id]
            if current["lease_token"] != lease:
                raise RuntimeError("Job lease was lost")
            if spec.canonical in db.lessons:
                raise ValueError("Published lesson identities are immutable")
            previous = db.lessons.get(str(current.get("revision_of"))) if current.get("revision_of") else None
            if current.get("revision_of") and (
                previous is None
                or previous.get("superseded_by")
                or digest_spec(LessonSpec.model_validate(previous["spec"]))
                != current.get("revision_parent_sha256")
            ):
                raise ValueError("Revision parent changed or was superseded; previous history is preserved")
            db.lessons[spec.canonical] = {
                "id": spec.canonical,
                "spec": spec.model_dump(mode="json"),
                "video": location,
                "audio": current["audio"],
                "created_at": time.time(),
                "quality": "ai-reviewed",
                "views": 0,
                "cost_usd": current["cost_usd"],
                "spec_sha256": digest_spec(spec),
                "video_sha256": video_digest,
                "storyboard_version": "ce-1" if spec.version == 2 else "legacy-v1",
            }
            current.update(lesson_id=spec.canonical, message="Your explanation is ready", phase="complete")
            if previous is not None:
                previous.update(archived=True, superseded_by=spec.canonical)
            self.domain.settle(db, current, "complete")

        self.store.transaction(publish)
        await self.checkpoints.checkpoint(
            {"job_id": job_id, "lesson_id": spec.canonical}, label="lesson-published"
        )
