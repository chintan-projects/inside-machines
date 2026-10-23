"""Bounded durable sliding-window counters, independent from disposable telemetry."""

import hashlib
import math
import time
from typing import TYPE_CHECKING, Literal

from fastapi import HTTPException

if TYPE_CHECKING:
    from .store import Database

type RateScope = Literal["login", "guest", "conversation", "chat-browser", "chat-network"]
MAX_BUCKETS = 4096
MAX_HITS = 512
HORIZON = 3600
LEGACY: tuple[tuple[str, str, RateScope], ...] = (
    ("login_failed", "address", "login"), ("guest_started", "address", "guest"),
    ("chat_started", "user_id", "conversation"), ("chat_requested", "user_id", "chat-browser"),
    ("chat_requested", "address", "chat-network"),
)


def rate_key(scope: RateScope, subject: str) -> str:
    """Opaque subjects/rate hashes stay server-only, including serialized bucket keys."""
    return hashlib.sha256(f"{scope}:{subject}".encode()).hexdigest()


def initialize_rates(db: "Database") -> None:
    """Migrate active historical events before the Store can trim any telemetry."""
    if db.rate_limits_version == 1:
        return
    now = time.time()
    counters: dict[str, list[float]] = {}
    for event in db.events:
        at = float(str(event.get("at", 0)))
        if not math.isfinite(at) or at <= now - HORIZON:
            continue
        for kind, field, scope in LEGACY:
            subject = str(event.get(field) or "")
            if event.get("kind") != kind or not subject:
                continue
            key = rate_key(scope, subject)
            if key not in counters and len(counters) >= MAX_BUCKETS:
                # Never silently forget an active omitted subject. New buckets
                # stay closed until the omitted horizon has expired.
                db.rate_limits_overflow_until = max(db.rate_limits_overflow_until, at + HORIZON)
                continue
            counters[key] = sorted([*counters.get(key, []), at])[-MAX_HITS:]
    db.rate_limits = counters
    db.rate_limits_version = 1


def take_rate(db: "Database", scope: RateScope, subject: str, limit: int, message: str,
              *, seconds: int = HORIZON, consume: bool = True) -> None:
    """Check/consume under the caller's Store lock, alongside sessions or paid reserves."""
    if not subject or not 1 <= seconds <= HORIZON or limit < 1:
        raise HTTPException(503, "The request limit is not configured safely")
    initialize_rates(db)
    now = time.time()
    key = rate_key(scope, subject)
    hits = [at for at in db.rate_limits.get(key, []) if at > now - seconds]
    if len(hits) >= min(limit, MAX_HITS):
        raise HTTPException(429, message)
    if not consume:
        return
    if key not in db.rate_limits:
        # Expired buckets may be reclaimed; active buckets are never evicted.
        db.rate_limits = {k: values for k, values in db.rate_limits.items()
                          if values and values[-1] > now - HORIZON}
        if len(db.rate_limits) >= MAX_BUCKETS or now < db.rate_limits_overflow_until:
            raise HTTPException(429, "The public demo is busy. Please try again later.")
    db.rate_limits[key] = [*hits, now]
