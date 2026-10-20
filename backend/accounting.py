"""Atomic reservation and auditable provider-cost settlement."""

import time
from dataclasses import asdict
from typing import Literal

from fastapi import HTTPException

from .provider import UsageReceipt
from .settings import Settings
from .store import Database


def receipt_origin(db: Database, job_id: str, phase: Literal["research", "author"]) -> str | None:
    """Resolve known paid provenance through reuse links, failing closed on cycles."""
    seen: set[str] = set()
    field = "research_reused_from" if phase == "research" else "draft_reused_from"
    while job_id and job_id not in seen:
        seen.add(job_id)
        receipt = db.ledger.get(f"lesson:{job_id}:{phase}")
        if receipt is not None:
            return job_id if receipt.get("models") and not receipt.get("uncertain") else None
        job_id = str(db.jobs.get(job_id, {}).get(field) or "")
    return None


def reserve(db: Database, amount: float, settings: Settings) -> None:
    """Reserve before dispatch so concurrent callers cannot overspend the ceiling."""
    if amount <= 0 or db.spent + db.reserved + amount > settings.budget_usd + 1e-9:
        raise HTTPException(429, "The alpha AI budget is reserved or used. Existing explanations still work.")
    db.reserved += amount


def charge(
    db: Database, operation: str, receipt: UsageReceipt, reserved: float, *, uncertain: bool = False
) -> float:
    """Settle once; retain the full allowance when provider billing is unknown.

    Speech cost remains an estimate because that endpoint omits usage. An
    ambiguous transport failure is never recorded as a free provider request.
    """
    if operation in db.ledger:
        return float(str(db.ledger[operation]["charged_usd"]))
    amount = max(receipt.cost_usd, reserved if uncertain else 0)
    db.reserved = max(0, db.reserved - reserved)
    db.spent += amount
    db.ledger[operation] = {
        **asdict(receipt),
        "at": time.time(),
        "operation": operation,
        "charged_usd": amount,
        "uncertain": uncertain,
        "speech_estimated": receipt.speech_characters > 0,
    }
    return amount
