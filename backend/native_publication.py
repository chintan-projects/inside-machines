"""Owner-operated verification/import of prebuilt native artwork, never remote code."""

import argparse
import asyncio
import hashlib
import json
import subprocess
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError

from .assets import Assets
from .learning_paths import LearningPath, validate_path
from .native_contracts import NativeData, NativeLessonSpec
from .native_proof import NativeProof, proof_digest, verify_proof
from .native_registry import canonical_digest, renderer_for, verify_sources
from .quality import require_learning_quality
from .starters import digest_spec
from .store import Database, Store


class NativeLocalArtifact(NativeData):
    """A bounded local export; file content must independently match real media proof."""

    spec: NativeLessonSpec
    proof: NativeProof
    video_file: str = Field(min_length=5, max_length=240)
    narration: str = Field(min_length=10, max_length=180)
    replaces: list[str] = Field(default_factory=list, max_length=12)


class NativeManifest(NativeData):
    schema_version: Literal["native-publication-1"]
    artifacts: list[NativeLocalArtifact] = Field(min_length=1, max_length=12)
    path: LearningPath | None = None


class PreparedNative(NativeData):
    """Storage location and exact proof are selected by trusted local production."""

    spec: NativeLessonSpec
    proof: NativeProof
    video: str
    narration: str
    replaces: list[str] = Field(default_factory=list)


def artifact_identity(spec: NativeLessonSpec, proof: NativeProof) -> str:
    """Bind the semantic contract, renderer source, real media and production checkpoints."""
    return canonical_digest({"spec_sha256": digest_spec(spec), "video_sha256": proof.video_sha256,
                             "proof_sha256": proof_digest(proof), "renderer": spec.renderer.model_dump(mode="json")})


def native_integrity_issues(record: dict[str, object], spec: NativeLessonSpec) -> list[str]:
    """Preserved media remains readable when its renderer retires; changed bytes do not."""
    try:
        proof = NativeProof.model_validate(record.get("native_proof"))
        if (record.get("spec_sha256") != digest_spec(spec)
                or record.get("video_sha256") != proof.video_sha256
                or record.get("native_proof_sha256") != proof_digest(proof)
                or record.get("native_artifact_sha256") != artifact_identity(spec, proof)):
            raise ValueError("Native production artifact identity changed")
    except (ValueError, OSError, ValidationError):
        return ["The native artwork/media production proof is missing, unsafe or does not match this revision"]
    return []


def native_record_issues(record: dict[str, object], spec: NativeLessonSpec) -> list[str]:
    """Current production/release additionally requires the exact available registered renderer."""
    issues = native_integrity_issues(record, spec)
    if issues:
        return issues
    try:
        verify_proof(spec, NativeProof.model_validate(record["native_proof"]))
    except (ValueError, OSError, ValidationError):
        return ["The native artwork source or rendered proof no longer meets current production checks"]
    return []


def verify_video(path: Path, proof: NativeProof) -> None:
    """Check actual bytes, duration and mobile H264/AAC media rather than trusting a filename."""
    if not path.is_file() or not 0 < path.stat().st_size <= 250_000_000:
        raise ValueError("Native export needs a bounded completed MP4 file")
    if hashlib.sha256(path.read_bytes()).hexdigest() != proof.video_sha256:
        raise ValueError("Native video bytes do not match the exact production proof")
    result = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                            check=True, capture_output=True, text=True, timeout=20)
    metadata = json.loads(result.stdout)
    videos = [s for s in metadata["streams"] if s.get("codec_type") == "video"]
    audio = [s for s in metadata["streams"] if s.get("codec_type") == "audio"]
    if (len(videos) != 1 or len(audio) != 1 or videos[0].get("codec_name") != "h264"
            or audio[0].get("codec_name") != "aac" or videos[0].get("pix_fmt") != "yuv420p"
            or videos[0].get("width") != proof.width or videos[0].get("height") != proof.height
            or videos[0].get("avg_frame_rate") not in ("24/1", "24000/1000")
            or abs(float(metadata["format"]["duration"]) - proof.video_duration) > .15):
        raise ValueError("Native MP4 must match its narrated duration, 1280×866/24fps and H264/AAC format")


def verify_manifest(manifest_path: Path) -> tuple[NativeManifest, list[Path]]:
    """Read only an explicit local manifest and its sibling media; no API or Store access."""
    manifest = NativeManifest.model_validate_json(manifest_path.read_text())
    ids = [a.spec.canonical for a in manifest.artifacts]
    if len(set(ids)) != len(ids):
        raise ValueError("Native manifest cannot repeat an immutable lesson revision")
    if manifest.path:
        validate_path(manifest.path.model_dump_json(), set(ids))
    paths = []
    base = manifest_path.parent.resolve()
    for artifact in manifest.artifacts:
        relative = Path(artifact.video_file)
        media = (base / relative).resolve()
        if relative.is_absolute() or not media.is_relative_to(base) or relative.suffix != ".mp4":
            raise ValueError("Native media must be an MP4 inside the explicit export directory")
        verify_sources(renderer_for(artifact.spec))
        require_learning_quality(artifact.spec)
        verify_proof(artifact.spec, artifact.proof)
        verify_video(media, artifact.proof)
        paths.append(media)
    return manifest, paths


def import_native(store: Store, artifacts: list[PreparedNative], path: LearningPath | None = None) -> tuple[int, int]:
    """Atomically add held native drafts; never archive a previous artifact or approve gates."""
    ids = [a.spec.canonical for a in artifacts]
    if not artifacts or len(set(ids)) != len(ids):
        raise ValueError("Native import needs distinct verified artifacts")
    if path:
        validate_path(path.model_dump_json(), set(ids))
    for artifact in artifacts:
        require_learning_quality(artifact.spec)
        verify_proof(artifact.spec, artifact.proof)

    def write(db: Database) -> tuple[int, int]:
        inserted, unchanged = 0, 0
        root_id = path.nodes[0].lesson_id if path else None
        root_spec = next((a.spec for a in artifacts if a.spec.canonical == root_id), None)
        for artifact in artifacts:
            spec, proof = artifact.spec, artifact.proof
            identity = artifact_identity(spec, proof)
            old = db.lessons.get(spec.canonical)
            if old:
                if old.get("native_artifact_sha256") != identity or old.get("video_sha256") != proof.video_sha256:
                    raise ValueError("Published native revisions are immutable; use a new revision ID")
                if native_record_issues(old, spec):
                    raise ValueError("Existing native publication proof changed; original history is preserved")
                unchanged += 1
                continue
            node = next((n for n in path.nodes if n.lesson_id == spec.canonical), None) if path else None
            db.lessons[spec.canonical] = {
                "id": spec.canonical, "spec": spec.model_dump(mode="json"), "video": artifact.video,
                "audio": [], "quality": "authored-native-draft", "created_at": time.time(), "views": 0,
                "cost_usd": 0, "spec_sha256": digest_spec(spec), "video_sha256": proof.video_sha256,
                "storyboard_version": "native-studio-1", "narration": artifact.narration,
                "native_proof": proof.model_dump(mode="json"), "native_proof_sha256": proof_digest(proof),
                "native_artifact_sha256": identity, "pending_replaces": artifact.replaces,
                "production_cost": {"mode": "local-authored-native", "paid_calls": 0, "speech": artifact.narration,
                                    "note": "Import/export performs no API calls; historical artwork/model spend and review labor are separate."},
                "depth_parent": root_id if node and node.role != "core" else None,
                "depth_parent_sha256": digest_spec(root_spec) if root_spec and node and node.role != "core" else None,
                "depth_role": node.role if node and node.role != "core" else None,
                "suggested_learning_path": path.model_dump(mode="json") if root_id == spec.canonical and path else None,
            }
            inserted += 1
        return inserted, unchanged

    return store.transaction(write)


async def _import_manifest(manifest_path: Path, local_data: Path | None) -> tuple[int, int]:
    from .settings import load_settings

    manifest, files = verify_manifest(manifest_path)
    settings = load_settings()
    if local_data:
        settings = replace(settings, data_dir=local_data, database_url="", blob_token="", production=False,
                           openai_key="", anthropic_key="", budget_usd=0)
    assets, store = Assets(settings), Store(settings.database_url, settings.data_dir)
    prepared = []
    for artifact, media in zip(manifest.artifacts, files, strict=True):
        location = await assets.put(f"native/{artifact.spec.canonical}/{artifact.proof.video_sha256}.mp4",
                                    media.read_bytes(), "video/mp4")
        if hashlib.sha256(await assets.read(location)).hexdigest() != artifact.proof.video_sha256:
            raise ValueError("Stored native video failed its byte verification; nothing was imported")
        prepared.append(PreparedNative(spec=artifact.spec, proof=artifact.proof, video=location,
                                       narration=artifact.narration, replaces=artifact.replaces))
    return import_native(store, prepared, manifest.path)


def main() -> None:
    """Canonicalization is a pure stdin/stdout protocol; import is a separate explicit action."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("canonicalize", "fingerprint", "verify", "import"))
    parser.add_argument("manifest", type=Path, nargs="?")
    parser.add_argument("--local-data", type=Path)
    parser.add_argument("--configured-destination", action="store_true")
    args = parser.parse_args()
    if args.command == "canonicalize":
        spec = NativeLessonSpec.model_validate_json(sys.stdin.read())
        sys.stdout.write(json.dumps({"spec": spec.model_dump(mode="json"), "sha256": digest_spec(spec),
                                    "canonical_json": json.dumps(spec.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))}))
    elif args.command == "fingerprint":
        sys.stdout.write(json.dumps({"sha256": canonical_digest(json.loads(sys.stdin.read()))}))
    elif args.command == "verify":
        if args.manifest is None:
            parser.error("verify requires an explicit local manifest")
        manifest, _ = verify_manifest(args.manifest)
        sys.stdout.write(json.dumps({"verified": len(manifest.artifacts), "released": False}))
    else:
        if args.manifest is None or not (args.local_data or args.configured_destination):
            parser.error("import requires a manifest and --local-data or explicit --configured-destination")
        inserted, unchanged = asyncio.run(_import_manifest(args.manifest, args.local_data))
        sys.stdout.write(json.dumps({"inserted": inserted, "unchanged": unchanged, "released": False}))


if __name__ == "__main__":
    main()
