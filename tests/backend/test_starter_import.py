"""Ensure production seeding never copies local private records or overwrites lessons."""

import hashlib
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.seed_aircon import aircon
from backend.seed_cooker import cooker
from backend.seed_washer import washer
from backend.starters import PreparedStarter, import_starters, prepare_starters, read_manifest, save_manifest
from backend.store import Database, Store


class MemoryAssets:
    """Isolated test transport; no network or production writes."""

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    async def put(self, key: str, data: bytes, content_type: str) -> str:
        """Return a schema-valid private location for this explicit fixture."""
        assert content_type == "video/mp4"
        location = "https://test.private.blob.vercel-storage.com/" + key
        self.objects[location] = data
        return location

    async def read(self, location: str) -> bytes:
        """Read only objects inside this fixture."""
        return self.objects[location]


async def test_seed_import_is_selective_and_idempotent(tmp_path: Path) -> None:
    """Only approved authored lessons cross the local/hosted boundary."""
    source, target = Store("", tmp_path / "source"), Store("", tmp_path / "target")
    local, remote = MemoryAssets(), MemoryAssets()

    def seed(db: Database) -> None:
        for spec in (washer(), cooker(), aircon()):
            location = spec.canonical + ".mp4"
            local.objects[location] = b"explicit-test-media:" + spec.canonical.encode()
            db.lessons[spec.canonical] = {
                "id": spec.canonical,
                "spec": spec.model_dump(mode="json"),
                "video": location,
                "quality": "authored-starter",
            }
        db.users["private-local-user"] = {"name": "Not for import"}
        db.chats["private-local-chat"] = {"text": "Private conversation must remain local"}
        db.feedback["private-local-rating"] = {"reason": "Private feedback"}
        db.spent = 12

    source.transaction(seed)
    prepared = await prepare_starters(source, local, remote)
    manifest = tmp_path / "private" / "manifest.json"
    save_manifest(manifest, prepared)
    assert "Private conversation" not in manifest.read_text()
    assert "Not for import" not in manifest.read_text()
    assert import_starters(target, read_manifest(manifest)) == (3, 0)
    target.transaction(lambda db: db.lessons["washing-machine"].update(views=12))
    assert import_starters(target, prepared) == (0, 3)
    state = target.snapshot()
    assert not state.chats and not state.feedback and not state.users and state.spent == 0
    assert state.lessons["washing-machine"]["views"] == 12
    assert all(
        item.video_sha256 == hashlib.sha256(remote.objects[item.video]).hexdigest() for item in prepared
    )


def test_prepared_manifest_rejects_changed_content_and_hosts(tmp_path: Path) -> None:
    """A tampered record cannot redirect media delivery or silently change the lesson."""
    spec = washer()
    payload: dict[str, object] = {
        "id": spec.canonical,
        "spec": spec.model_dump(mode="json"),
        "video": "https://attacker.example/video",
        "video_sha256": "0" * 64,
        "spec_sha256": "0" * 64,
    }
    with pytest.raises(ValidationError):
        PreparedStarter.model_validate(payload)
    manifest = tmp_path / "bad.json"
    manifest.write_text("[]")
    with pytest.raises(ValueError):
        read_manifest(manifest)


async def test_only_ready_authored_starters_are_uploaded(tmp_path: Path) -> None:
    """Missing or generated local lessons cannot become purported authored seeds."""
    with pytest.raises(ValueError, match="Render the authored starter"):
        await prepare_starters(Store("", tmp_path), MemoryAssets(), MemoryAssets())
