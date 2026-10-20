"""Prepare immutable private starter assets and import only lesson records into Postgres."""

import argparse
import asyncio
import hashlib
import json
import time
from pathlib import Path
from typing import Literal, Protocol
from urllib.parse import urlparse

from _shared.services.logger import get_logger
from pydantic import BaseModel, Field, model_validator

from .assets import Assets
from .contracts import LessonSpec
from .settings import ROOT, load_settings
from .store import Database, Store

logger = get_logger(__name__)
STARTER_IDS = ("washing-machine", "pressure-cooker", "air-conditioner")


class ObjectAssets(Protocol):
    """Storage boundary shared by real private Blob and isolated test fixtures."""

    async def put(self, key: str, data: bytes, content_type: str) -> str:
        """Write one artifact and return its internal location."""
        ...

    async def read(self, location: str) -> bytes:
        """Read the exact stored artifact."""
        ...


class PreparedStarter(BaseModel):
    """A manifest contains public teaching data and a private object location only."""

    id: str
    spec: LessonSpec
    video: str
    video_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    spec_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    quality: Literal["authored-starter"] = "authored-starter"

    @model_validator(mode="after")
    def check_identity(self) -> "PreparedStarter":
        """Reject mismatched IDs, changed lesson data and unexpected remote locations."""
        if self.id not in STARTER_IDS or self.id != self.spec.canonical:
            raise ValueError("Only the three authored starters may be imported")
        if digest_spec(self.spec) != self.spec_sha256:
            raise ValueError("The prepared lesson content has changed")
        parsed = urlparse(self.video)
        if (
            parsed.scheme != "https"
            or not (parsed.hostname or "").endswith(".private.blob.vercel-storage.com")
            or parsed.query
        ):
            raise ValueError("Starter videos must use an unsigned private Blob location")
        return self


def digest_spec(spec: LessonSpec) -> str:
    """Fingerprint canonical JSON so key ordering does not change a revision."""
    data = spec.model_dump(mode="json")
    if spec.version == 1:
        # Preserve fingerprints of previously published v1 artifacts byte-for-byte.
        data.pop("teaching", None)
        data.pop("graphics", None)
    elif spec.teaching:
        if not data["teaching"].get("renderer_fingerprint"):
            data["teaching"].pop("renderer_fingerprint", None)
        # Empty trajectories preserve the original CE-1 pose semantics/fingerprint.
        for group in (*data["teaching"]["beats"], *data["teaching"]["scenarios"]):
            for change in group["changes"]:
                if not change.get("via"):
                    change.pop("via", None)
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


async def prepare_starters(source: Store, local: ObjectAssets, remote: ObjectAssets) -> list[PreparedStarter]:
    """Copy authored lesson/video pairs without copying sessions, feedback or analytics."""
    snapshot = source.snapshot()
    prepared = []
    for lesson_id in STARTER_IDS:
        record = snapshot.lessons.get(lesson_id)
        if not record or record.get("quality") != "authored-starter" or not record.get("video"):
            raise ValueError(f"Render the authored starter first: {lesson_id}")
        spec = LessonSpec.model_validate(record["spec"])
        data = await local.read(str(record["video"]))
        content_digest = hashlib.sha256(data).hexdigest()
        location = await remote.put(f"starters/v1/{lesson_id}/{content_digest}.mp4", data, "video/mp4")
        if hashlib.sha256(await remote.read(location)).hexdigest() != content_digest:
            raise ValueError("Stored starter video failed its integrity check")
        prepared.append(
            PreparedStarter(
                id=lesson_id,
                spec=spec,
                video=location,
                video_sha256=content_digest,
                spec_sha256=digest_spec(spec),
            )
        )
    return prepared


def save_manifest(path: Path, starters: list[PreparedStarter]) -> None:
    """Persist a deployment-only manifest inside the ignored Vercel directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([starter.model_dump(mode="json") for starter in starters], indent=2))


def read_manifest(path: Path) -> list[PreparedStarter]:
    """Validate every record before any database mutation."""
    payload: object = json.loads(path.read_text())
    if not isinstance(payload, list) or len(payload) != len(STARTER_IDS):
        raise ValueError("Expected exactly three prepared starters")
    starters = [PreparedStarter.model_validate(record) for record in payload]
    if {starter.id for starter in starters} != set(STARTER_IDS):
        raise ValueError("Starter identities must be unique and complete")
    return starters


def import_starters(target: Store, starters: list[PreparedStarter]) -> tuple[int, int]:
    """Atomically seed missing lessons without replacing existing catalog or private data."""
    if {starter.id for starter in starters} != set(STARTER_IDS) or len(starters) != len(STARTER_IDS):
        raise ValueError("Import requires a complete three-starter manifest")

    def write(db: Database) -> tuple[int, int]:
        inserted, skipped = 0, 0
        for starter in starters:
            if starter.id in db.lessons:
                skipped += 1
                continue
            db.lessons[starter.id] = {
                "id": starter.id,
                "spec": starter.spec.model_dump(mode="json"),
                "video": starter.video,
                "quality": starter.quality,
                "created_at": time.time(),
                "audio": [],
                "views": 0,
                "cost_usd": 0,
                "video_sha256": starter.video_sha256,
                "spec_sha256": starter.spec_sha256,
            }
            inserted += 1
        return inserted, skipped

    return target.transaction(write)


async def main() -> None:
    """Separate asset preparation from the explicitly requested database import."""
    from dataclasses import replace

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "import"))
    arguments = parser.parse_args()
    settings = load_settings()
    manifest = ROOT / ".vercel" / "starter-manifest.json"
    if arguments.action == "prepare":
        if not settings.blob_token:
            raise RuntimeError("Private Blob storage must be configured before preparing starter assets")
        local = Assets(replace(settings, blob_token="", production=False))
        prepared = await prepare_starters(Store("", settings.data_dir), local, Assets(settings))
        save_manifest(manifest, prepared)
        logger.info("Starter assets prepared and verified", count=len(prepared))
    else:
        if not settings.database_url:
            raise RuntimeError("Configure the destination DATABASE_URL before importing starter lessons")
        prepared = read_manifest(manifest)
        inserted, skipped = import_starters(Store(settings.database_url, settings.data_dir), prepared)
        logger.info("Starter lesson import complete", inserted=inserted, existing=skipped)


if __name__ == "__main__":
    asyncio.run(main())
