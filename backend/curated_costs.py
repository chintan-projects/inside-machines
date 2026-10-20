"""Owner-only cost attribution for curated scopes; never dispatch or infer a bill."""

from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel, Field

from .contracts import LessonSpec, canonicalize
from .curated.catalog import SYSTEMS
from .domain import User
from .learning_reviews import review_state
from .settings import Settings
from .store import Database


class CostTotals(BaseModel):
    """Disjoint accounting buckets; receipt rates are not a provider invoice."""

    recorded_usd: float = 0
    receipt_based_usd: float = 0
    estimated_usd: float = 0
    uncertain_usd: float = 0
    input_tokens: int = 0
    output_tokens: int = 0
    operations: int = 0

    def include(self, receipt: Mapping[str, object]) -> None:
        """Account once from the existing ledger, retaining uncertainty explicitly."""
        amount = float(str(receipt.get("charged_usd", 0)))
        self.recorded_usd += amount
        if receipt.get("uncertain"):
            self.uncertain_usd += amount
        elif receipt.get("speech_estimated") or receipt.get("search_estimated") or not receipt.get("models"):
            self.estimated_usd += amount
        else:
            self.receipt_based_usd += amount
        self.input_tokens += int(str(receipt.get("input_tokens", 0)))
        self.output_tokens += int(str(receipt.get("output_tokens", 0)))
        self.operations += 1


class RevisionCost(BaseModel):
    """Artifact identity and direct build operations, without chats or prompts."""

    lesson_id: str
    archived: bool
    released: bool
    narration: str
    production_mode: str
    declared_paid_calls: int | None = None
    build: CostTotals = Field(default_factory=CostTotals)


class SystemCost(BaseModel):
    """One registered system can retain many immutable revisions and failed jobs."""

    system_id: str
    title: str
    category: str
    build: CostTotals = Field(default_factory=CostTotals)
    chat: CostTotals = Field(default_factory=CostTotals)
    revisions: list[RevisionCost] = Field(default_factory=list)
    jobs: int = 0
    active_reserved_usd: float = 0
    owner_draft_reservation_usd: float
    expected_generation_usd: None = None
    optional_hosted_speech_estimate_usd: float | None = None
    speech_script_words: int | None = None
    speech_estimate_lesson_id: str | None = None
    speech_estimate_basis: Literal["active-lesson", "authored-source", "unmeasured"] = "unmeasured"


class CuratedCostReport(BaseModel):
    """A reconciled projection of the shared ledger, not a second accounting store."""

    systems: list[SystemCost]
    attributed: CostTotals
    unallocated: CostTotals
    ledger_total: CostTotals
    stored_spent_usd: float
    spent_ledger_difference_usd: float
    stored_reserved_usd: float
    unallocated_reserved_usd: float
    budget_usd: float
    generation_reserve_usd: float
    speech_rate_usd_per_minute: float
    assumptions: list[str]


def _system_id(record: Mapping[str, object], names: Mapping[str, str]) -> str | None:
    """Use trusted metadata or exact normalized public scope, never prefix guesses."""
    explicit = record.get("curated_system_id")
    if isinstance(explicit, str) and explicit in SYSTEMS:
        return explicit
    spec_data = record.get("spec")
    if spec_data:
        spec = LessonSpec.model_validate(spec_data)
        candidates = {canonicalize(spec.question), canonicalize(spec.title), spec.canonical,
                      *(canonicalize(alias) for alias in spec.aliases)}
    else:
        candidates = {canonicalize(str(record.get("question", ""))), str(record.get("canonical", ""))}
    matches = {names[name] for name in candidates if name in names}
    return next(iter(matches)) if len(matches) == 1 else None


def _system_names() -> dict[str, str]:
    return {canonicalize(name): plan.id for plan in SYSTEMS.values() for name in (plan.id, *plan.aliases)}


def _lesson_system_id(db: Database, lesson_id: str, names: Mapping[str, str]) -> str | None:
    """Attribute scoped depth work to its exact parent, including unrecognized questions."""
    seen: set[str] = set()
    while lesson_id not in seen:
        seen.add(lesson_id)
        record = db.lessons.get(lesson_id)
        if record is None:
            return None
        if record.get("depth_parent"):
            lesson_id = str(record["depth_parent"])
        else:
            return _system_id(record, names)
    return None


@dataclass(frozen=True)
class _SpeechScript:
    system_id: str
    lesson_id: str
    words: int


@lru_cache(maxsize=1)
def _authored_scripts() -> tuple[_SpeechScript, ...]:
    """Count complete source revisions once per process, including reunion narration."""
    from .concept_publication import authored_lessons

    names = _system_names()
    scripts = []
    for spec, _replaces in authored_lessons():
        system_id = _system_id({"spec": spec.model_dump(mode="json")}, names)
        if system_id:
            scripts.append(_SpeechScript(system_id, spec.canonical, sum(len(stage.narration.split()) for stage in spec.stages)))
    return tuple(scripts)


def _set_speech_estimate(row: SystemCost, script: _SpeechScript, rate: float,
                         basis: Literal["active-lesson", "authored-source"]) -> None:
    row.speech_script_words = script.words
    row.speech_estimate_lesson_id = script.lesson_id
    row.speech_estimate_basis = basis
    row.optional_hosted_speech_estimate_usd = script.words / 130 * rate


def curated_cost_report(db: Database, settings: Settings, user: User) -> CuratedCostReport:
    """Attribute each paid operation once, including failures, old revisions and chats."""
    if not user.owner:
        raise HTTPException(403, "Owner access is required")
    names = _system_names()
    rows = {
        plan.id: SystemCost(
            system_id=plan.id, title=plan.title, category=plan.category,
            owner_draft_reservation_usd=settings.generation_reserve,
        ) for plan in SYSTEMS.values()
    }
    for script in _authored_scripts():
        _set_speech_estimate(rows[script.system_id], script, settings.speech_rate, "authored-source")
    lesson_systems: dict[str, str] = {}
    revisions: dict[str, RevisionCost] = {}
    current_scripts: dict[str, tuple[float, str, _SpeechScript]] = {}
    for lesson_id, record in db.lessons.items():
        system_id = _lesson_system_id(db, lesson_id, names)
        if not system_id:
            continue
        lesson_systems[lesson_id] = system_id
        provenance = record.get("production_cost")
        provenance = provenance if isinstance(provenance, dict) else {}
        paid_calls = provenance.get("paid_calls")
        revision = RevisionCost(
            lesson_id=lesson_id, archived=bool(record.get("archived")),
            released=not record.get("archived") and bool(review_state(db, lesson_id)["ready"]),
            narration=str(record.get("narration", "Not recorded")),
            production_mode=str(provenance.get("mode", "unmeasured")),
            declared_paid_calls=paid_calls if isinstance(paid_calls, int) and not isinstance(paid_calls, bool) else None,
        )
        rows[system_id].revisions.append(revision)
        revisions[lesson_id] = revision
        if not record.get("archived") and not record.get("superseded_by") and not record.get("depth_parent"):
            spec = LessonSpec.model_validate(record["spec"])
            candidate = (float(str(record.get("created_at", 0))), lesson_id,
                         _SpeechScript(system_id, lesson_id, sum(len(stage.narration.split()) for stage in spec.stages)))
            current = current_scripts.get(system_id)
            if current is None or candidate[:2] > current[:2]:
                current_scripts[system_id] = candidate
    for _created, _lesson_id, script in current_scripts.values():
        _set_speech_estimate(rows[script.system_id], script, settings.speech_rate, "active-lesson")
    jobs: dict[str, str] = {}
    for job_id, job in db.jobs.items():
        system_id = (lesson_systems.get(str(job.get("lesson_id"))) or lesson_systems.get(str(job.get("revision_of")))
                     or lesson_systems.get(str(job.get("node_parent"))) or _system_id(job, names))
        if system_id:
            jobs[job_id] = system_id
            rows[system_id].jobs += 1
            if job.get("status") not in ("complete", "completed", "failed"):
                rows[system_id].active_reserved_usd += float(str(job.get("reservation", 0)))
    attributed, unallocated, total = CostTotals(), CostTotals(), CostTotals()
    for operation, receipt in db.ledger.items():
        total.include(receipt)
        kind, separator, remainder = operation.partition(":")
        record_id, separator2, _phase = remainder.partition(":")
        system_id = None
        if separator and separator2 and kind == "lesson" and record_id in jobs:
            system_id = jobs[record_id]
            rows[system_id].build.include(receipt)
            lesson_id = str(db.jobs[record_id].get("lesson_id", ""))
            if lesson_id in revisions:
                revisions[lesson_id].build.include(receipt)
        elif separator and separator2 and kind == "chat":
            lesson_id = str(db.chats.get(record_id, {}).get("lesson_id", ""))
            system_id = lesson_systems.get(lesson_id)
            if system_id:
                rows[system_id].chat.include(receipt)
        (attributed if system_id else unallocated).include(receipt)
    reserved = sum(row.active_reserved_usd for row in rows.values())
    return CuratedCostReport(
        systems=list(rows.values()), attributed=attributed, unallocated=unallocated,
        ledger_total=total, stored_spent_usd=db.spent,
        spent_ledger_difference_usd=db.spent - total.recorded_usd,
        stored_reserved_usd=db.reserved, unallocated_reserved_usd=max(0, db.reserved - reserved),
        budget_usd=settings.budget_usd, generation_reserve_usd=settings.generation_reserve,
        speech_rate_usd_per_minute=settings.speech_rate,
        assumptions=[
            "Receipt-based costs use actual returned token counts and configured rates; they are not a provider invoice.",
            "Speech and unclassified search charges remain estimates. Unknown billing retains its allowance until reconciliation.",
            "Each ledger operation is counted once. Reused research or prior revisions remain with their original job; they are not charged again.",
            "An owner draft reservation is an admission allowance, not an expected price or a guarantee of publishable quality. A new attempt requires a new allowance.",
            "The optional hosted-speech estimate counts every narrated stage in the active served core revision, or the complete current authored source before import, at 130 words/minute and the configured rate. Depth drafts do not replace the core script estimate. It is not a measured clip price. Local computer speech incurs no speech API charge.",
            "Local-authored zero paid calls requires recorded provenance. Missing receipts alone mean unmeasured. Hosting, storage, authoring and human review labor are excluded.",
            "This report covers the app ledger only. Separate local experiments and external invoices are not silently included.",
        ],
    )
