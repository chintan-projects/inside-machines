"""Trusted vector sources and revision identity; never model-selected file paths."""

import hashlib
from functools import lru_cache

from .settings import ROOT


@lru_cache(maxsize=2)
def authored_context(context: str) -> str:
    """Load an allowlisted source bundled with both clients and video workers."""
    if context not in ("outside", "inside"):
        raise ValueError("Unknown cutaway context")
    return (ROOT / "public/figures" / f"ac-{context}.svg").read_text()


def ac_renderer_fingerprint() -> str:
    """Prevent an old lesson/video from silently acquiring a different cutaway."""
    return hashlib.sha256((authored_context("outside") + authored_context("inside")).encode()).hexdigest()
