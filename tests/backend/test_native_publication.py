"""Native import is held, source-bound and independent of provider/runtime code input."""

import hashlib
import json
import subprocess
from pathlib import Path
from typing import cast

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.app import create_app
from backend.assets import Assets
from backend.chat import Chats
from backend.contracts import AnswerSpec, LessonSpec
from backend.domain import Domain, User
from backend.interests import Interests
from backend.learning_bundle import learning_bundle
from backend.learning_reviews import LearningReviews, ReviewSubmission, native_release_identity, review_state
from backend.native_activation import NativeActivation, NativeActivationBody
from backend.native_contracts import NativeLessonSpec
from backend.native_proof import inspect_svg, verify_proof
from backend.native_publication import PreparedNative, import_native, native_record_issues
from backend.native_registry import renderer_for, verify_sources
from backend.quality import learning_issues
from backend.settings import ROOT, Settings
from backend.starters import digest_spec
from backend.store import Store
from backend.stored_lessons import component_ids, native_visible, parse_stored_spec

OWNER = User(id="native-test-owner", name="Synthetic native owner", owner=True)


def approve_fixture(store: Store, artifact: PreparedNative) -> None:
    """Synthetic attestations test the protocol, never approve actual artwork or learners."""
    for gate in ("engineering", "technical", "craft", "learning", "release"):
        data: dict[str, object] = {
            "spec_sha256": digest_spec(artifact.spec), "video_sha256": artifact.proof.video_sha256,
            "gate": gate, "reviewer": "Synthetic protocol fixture", "method": "human", "decision": "pass",
            "evidence": "Entirely synthetic test evidence; no actual human, device or beginner review occurred.",
            "independent": True, "real_device": True, "device": "Synthetic test phone",
        }
        if gate == "learning":
            data["scores"] = [{"participant": f"anon-{i}", "baseline": 0, "causal": 2, "transfer": 2} for i in range(5)]
        LearningReviews(store).record(artifact.spec.canonical, ReviewSubmission.model_validate(data), OWNER)


def test_native_reader_and_canonical_cli_preserve_legacy_hashes(
    native_prepared: PreparedNative, ce_spec: LessonSpec,
) -> None:
    """Native data is explicit v3, and normalized floats never alter old schema/hash semantics."""
    assert parse_stored_spec(ce_spec.model_dump(mode="json")) == ce_spec
    assert digest_spec(parse_stored_spec(ce_spec.model_dump(mode="json"))) == digest_spec(ce_spec)
    spec = native_prepared.spec
    assert parse_stored_spec(spec.model_dump(mode="json")) == spec
    assert "parts" not in spec.model_dump() and "graphics" not in spec.model_dump()
    assert component_ids(spec) == [c.id for c in spec.components]
    output = subprocess.run([str(ROOT / ".venv/bin/python"), "-m", "backend.native_publication", "canonicalize"],
                            input=spec.model_dump_json(), text=True, capture_output=True, check=True, timeout=15)
    result = json.loads(output.stdout)
    assert not output.stderr and result["sha256"] == digest_spec(spec)
    assert hashlib.sha256(result["canonical_json"].encode()).hexdigest() == result["sha256"]
    assert NativeLessonSpec.model_validate(result["spec"]) == spec


def test_native_registry_binds_actual_sources_and_exact_metadata(
    native_prepared: PreparedNative, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    registration = renderer_for(native_prepared.spec)
    verify_sources(registration)
    assert not learning_issues(native_prepared.spec)
    changed = native_prepared.spec.model_copy(update={"summary": "A changed summary must not inherit the approved source registration."})
    assert learning_issues(changed)
    copied = tmp_path / registration.sources[0].path
    copied.parent.mkdir(parents=True)
    copied.write_bytes((ROOT / registration.sources[0].path).read_bytes())
    monkeypatch.setattr("backend.native_registry.ROOT", tmp_path)
    verify_sources(registration)
    copied.write_text("Changed executable source")
    with pytest.raises(ValueError, match="source changed"):
        verify_sources(registration)


@pytest.mark.parametrize("change", ["cue-gap", "unknown-focus", "unsupported-control", "prediction-divergence", "raw-code"])
def test_native_schema_rejects_false_semantic_links(native_prepared: PreparedNative, change: str) -> None:
    payload = native_prepared.spec.model_dump(mode="json")
    if change == "cue-gap":
        payload["stages"][1]["start"] = 6
    elif change == "unknown-focus":
        payload["stages"][1]["focus"] = "nonexistent"
    elif change == "unsupported-control":
        payload["teaching"]["scenarios"][0]["controls"] = {"endpoint": "https://untrusted.example"}
    elif change == "prediction-divergence":
        payload["prediction_answer"] = "A different answer cannot inherit the actual prediction."
    else:
        payload["javascript"] = "execute arbitrary model output"
    with pytest.raises(ValidationError):
        NativeLessonSpec.model_validate(payload)


@pytest.mark.parametrize("change", ["focus-label", "core-label", "motion", "cue", "scenario", "controls", "identity", "duplicate"])
def test_native_proof_requires_actual_complete_labeled_rendering(native_prepared: PreparedNative, change: str) -> None:
    proof = native_prepared.proof.model_copy(deep=True)
    if change in ("focus-label", "core-label"):
        for frame in proof.frames:
            frame.svg = frame.svg.replace("Working" if change == "focus-label" else "Output", "Missing")
    elif change == "motion":
        first = next(f for f in proof.frames if f.cue_id == "working" and not f.scenario_id)
        for frame in proof.frames:
            if frame.cue_id == "working" and not frame.scenario_id:
                frame.svg = first.svg.replace('fill="red"', 'fill="blue"')
    elif change == "cue":
        proof.frames = [f for f in proof.frames if f.cue_id != "opening"]
    elif change == "scenario":
        proof.frames = [f for f in proof.frames if f.scenario_id != "off"]
    elif change == "controls":
        proof.frames[-1].controls = {"power": "on"}
    elif change == "identity":
        proof.spec_sha256 = "0" * 64
    else:
        proof.frames.append(proof.frames[0].model_copy())
    with pytest.raises(ValueError):
        verify_proof(native_prepared.spec, proof)


def test_real_native_marker_shape_is_safe_but_external_marker_is_not(native_prepared: PreparedNative) -> None:
    """The actual R2 arrow construct is local bounded SVG, not an external resource."""
    frame = native_prepared.proof.frames[0].model_copy(deep=True)
    frame.svg += '<defs><marker id="heat-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#9e4a21"/></marker></defs><path d="M20 30L100 30" marker-end="url(#heat-arrow)"/>'
    inspect_svg(frame)
    frame.svg = frame.svg.replace("url(#heat-arrow)", "url(https://untrusted.example/arrow.svg)")
    with pytest.raises(ValueError, match="fetch"):
        inspect_svg(frame)


def test_native_import_is_atomic_held_and_preserves_private_history(
    seeded: Store, settings: Settings, native_prepared: PreparedNative, user: User,
) -> None:
    seeded.transaction(lambda db: (db.chats.update({"private": {"messages": ["PRIVATE CHAT"]}}),
                                   db.ledger.update({"existing": {"charged_usd": .25}})))
    before = seeded.snapshot()
    artifact = native_prepared.model_copy(update={"replaces": ["washing-machine"]})
    assert import_native(seeded, [artifact]) == (1, 0)
    assert import_native(seeded, [artifact]) == (0, 1)
    after = seeded.snapshot()
    assert after.lessons["washing-machine"] == before.lessons["washing-machine"]
    assert after.chats == before.chats and after.ledger == before.ledger
    assert after.spent == before.spent and after.reserved == before.reserved
    assert not review_state(after, artifact.spec.canonical)["ready"]
    assert not native_visible(after, artifact.spec.canonical, user.owner)
    assert native_visible(after, artifact.spec.canonical, True)
    assert artifact.spec.canonical not in {row["id"] for row in Domain(seeded, settings).catalog()}
    assert artifact.spec.canonical in {row["id"] for row in Domain(seeded, settings).catalog(include_native_drafts=True)}
    changed = artifact.model_copy(deep=True)
    changed.proof.video_sha256 = "0" * 64
    with pytest.raises(ValueError, match="immutable"):
        import_native(seeded, [changed])
    assert seeded.snapshot() == after


def test_native_records_fail_closed_when_production_proof_is_tampered(
    store: Store, native_prepared: PreparedNative,
) -> None:
    import_native(store, [native_prepared])
    record = store.snapshot().lessons[native_prepared.spec.canonical]
    assert not native_record_issues(record, native_prepared.spec)
    raw = cast(dict[str, object], record["native_proof"])
    raw["video_sha256"] = "0" * 64
    assert native_record_issues(record, native_prepared.spec)


def test_native_revisions_and_paid_depth_are_explicitly_local_only(
    store: Store, settings: Settings, native_prepared: PreparedNative,
) -> None:
    import_native(store, [native_prepared])
    before = store.snapshot()
    for kwargs in ({"revision_of": native_prepared.spec.canonical, "operation": "native-revision-attempt"},
                   {"node_parent": native_prepared.spec.canonical, "node_role": "insight", "operation": "native-depth-attempt"}):
        with pytest.raises(HTTPException, match="trusted local production") as failure:
            Domain(store, settings).request("Why does this native mechanism change?", OWNER, **kwargs)  # type: ignore[arg-type] # Deliberately tests both existing keyword-only operation shapes.
        assert failure.value.status_code == 422
    assert store.snapshot() == before


async def test_retired_renderer_preserves_exact_released_media_bundle_and_private_chat(
    store: Store, settings: Settings, native_prepared: PreparedNative, user: User,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Previously approved immutable media stays accessible without approving altered source."""
    import_native(store, [native_prepared])
    approve_fixture(store, native_prepared)
    assert native_release_identity(store.snapshot(), native_prepared.spec.canonical)
    media = Assets(settings).root / native_prepared.video
    media.write_bytes(b"Synthetic native media API bytes, not an actual video.")
    chats = Chats(store, settings)
    original = chats.create(native_prepared.spec.canonical, user)
    registry_file = tmp = settings.data_dir / "retired-native-registry.json"
    tmp.write_text('{"schema_version":"native-renderers-1","renderers":[]}')
    monkeypatch.setattr("backend.native_registry.REGISTRY_FILE", registry_file)
    state = store.snapshot()
    assert not review_state(state, native_prepared.spec.canonical)["ready"]
    assert native_visible(state, native_prepared.spec.canonical, False)
    assert learning_bundle(state, native_prepared.spec.canonical, user)["lessons"]
    assert chats.get(original.id, user).lesson_id == original.lesson_id

    async def answer(prompt: str, config: Settings) -> str:
        assert "PRIVATE" not in prompt and "working" in prompt
        return AnswerSpec(answer="This synthetic reply uses the preserved immutable lesson context.", stage=1,
                          part="working", source_indices=[0], uncertain=False).model_dump_json()

    answered = await Chats(store, settings, answer).ask(original.id, "Explain the working input", "retired-native-question", user)
    assert len(answered.messages) == 2
    with TestClient(create_app(settings)) as client:
        client.post("/api/v1/auth/login", json={"name": "Family", "code": settings.invite_code})
        base = f"/api/v1/lessons/{native_prepared.spec.canonical}"
        assert client.get(base).status_code == client.get(base + "/captions").status_code == 200
        assert client.get(base + "/video").content == media.read_bytes()
        assert client.get(f"/api/v1/learning-paths/{native_prepared.spec.canonical}").status_code == 200
    store.transaction(lambda db: db.lessons[native_prepared.spec.canonical].update(video_sha256="0" * 64))
    assert not native_visible(store.snapshot(), native_prepared.spec.canonical, False)


def test_unreleased_native_is_not_exposed_by_member_routes(settings: Settings, native_prepared: PreparedNative) -> None:
    store = Store("", settings.data_dir)
    import_native(store, [native_prepared])
    with TestClient(create_app(settings)) as client:
        client.post("/api/v1/auth/login", json={"name": "Family", "code": settings.invite_code})
        base = f"/api/v1/lessons/{native_prepared.spec.canonical}"
        assert all(client.get(base + suffix).status_code == 404 for suffix in ("", "/captions", "/video"))
        assert client.get(f"/api/v1/learning-paths/{native_prepared.spec.canonical}").status_code == 404
        assert client.post("/api/v1/chats", json={"lesson_id": native_prepared.spec.canonical}).status_code == 404
        assert not client.get("/api/v1/lessons").json()
        client.post("/api/v1/auth/login", json={"name": "Owner", "code": settings.owner_code})
        assert client.get(base).status_code == 200
        assert "native_proof" not in client.get(base).json()
        assert client.post(f"/api/v1/owner/lessons/{native_prepared.spec.canonical}/revise",
                           json={"operation": "explicit-native-revision"}).status_code == 422


def activation_body(artifact: PreparedNative, old_ids: list[str] | None = None) -> NativeActivationBody:
    return NativeActivationBody(spec_sha256=digest_spec(artifact.spec), video_sha256=artifact.proof.video_sha256,
                                bundle_sha256="", expected_old_ids=old_ids or ["washing-machine"])


def test_native_activation_is_explicit_atomic_and_preserves_aliases_and_private_history(
    seeded: Store, native_prepared: PreparedNative, settings: Settings, user: User,
) -> None:
    artifact = native_prepared.model_copy(update={"replaces": ["washing-machine"]})
    import_native(seeded, [artifact])
    activation = NativeActivation(seeded)
    body = activation_body(artifact)
    held = seeded.snapshot()
    with pytest.raises(HTTPException) as rejected:
        activation.activate(artifact.spec.canonical, body, OWNER)
    assert rejected.value.status_code == 409 and seeded.snapshot() == held
    approve_fixture(seeded, artifact)
    # Release alone deliberately preserves the old catalog head.
    assert not seeded.snapshot().lessons["washing-machine"].get("archived")
    seeded.transaction(lambda db: (db.chats.update({"old-private": {"lesson_id": "washing-machine", "messages": ["PRIVATE"]}}),
                                   db.ledger.update({"old-receipt": {"charged_usd": .17}})))
    before = seeded.snapshot()
    result = activation.activate(artifact.spec.canonical, body, OWNER)
    assert result == {"lesson_id": artifact.spec.canonical, "replaced_ids": ["washing-machine"], "reused": False}
    after = seeded.snapshot()
    assert after.lessons["washing-machine"] == {**before.lessons["washing-machine"], "archived": True,
                                                "superseded_by": artifact.spec.canonical}
    assert after.chats == before.chats and after.ledger == before.ledger and after.learning_reviews == before.learning_reviews
    assert after.spent == before.spent and after.reserved == before.reserved
    assert activation.activate(artifact.spec.canonical, body, OWNER)["reused"]
    assert seeded.snapshot() == after
    for request in (Interests(seeded, settings).request, Domain(seeded, settings).request):
        assert request("How does a washer work?", user)["lesson_id"] == artifact.spec.canonical
    final = seeded.snapshot()
    assert not final.jobs and final.chats == before.chats and final.ledger == before.ledger
    ids = {row["id"] for row in Domain(seeded, settings).catalog()}
    assert artifact.spec.canonical in ids and "washing-machine" not in ids
    assert parse_stored_spec(final.lessons["washing-machine"]["spec"]).canonical == "washing-machine"
    # A changed native artifact cannot inherit the alias path's visibility.
    seeded.transaction(lambda db: db.lessons[artifact.spec.canonical].update(video_sha256="0" * 64))
    assert Interests(seeded, settings).request("How does a washer work?", user)["kind"] == "interest"


@pytest.mark.parametrize("change", ["spec", "video", "bundle", "proof", "intent", "malformed-intent", "missing", "branch", "target-branch", "cycle", "conflict", "self", "rejected"])
def test_native_activation_rejects_stale_or_unsafe_adoption_without_mutation(
    seeded: Store, native_prepared: PreparedNative, change: str,
) -> None:
    import_native(seeded, [native_prepared])
    approve_fixture(seeded, native_prepared)
    body = activation_body(native_prepared)
    if change in ("spec", "video", "bundle"):
        body = body.model_copy(update={change + "_sha256": "0" * 64})
    elif change == "proof":
        seeded.transaction(lambda db: db.lessons[native_prepared.spec.canonical].update(native_proof_sha256="0" * 64))
    elif change == "intent":
        seeded.transaction(lambda db: db.lessons[native_prepared.spec.canonical].update(pending_replaces=["different-head"]))
    elif change == "missing":
        body.expected_old_ids = ["washing-machine", "nonexistent-head"]
    elif change == "malformed-intent":
        seeded.transaction(lambda db: db.lessons[native_prepared.spec.canonical].update(pending_replaces="invalid"))
    elif change == "branch":
        seeded.transaction(lambda db: db.lessons["washing-machine"].update(depth_parent="some-other-core"))
    elif change == "target-branch":
        seeded.transaction(lambda db: db.lessons[native_prepared.spec.canonical].update(depth_parent="washing-machine"))
    elif change == "cycle":
        seeded.transaction(lambda db: db.lessons["washing-machine"].update(superseded_by="washing-machine"))
    elif change == "conflict":
        seeded.transaction(lambda db: db.lessons["washing-machine"].update(superseded_by=native_prepared.spec.canonical))
    elif change == "rejected":
        LearningReviews(seeded).record(native_prepared.spec.canonical, ReviewSubmission(
            spec_sha256=body.spec_sha256, video_sha256=body.video_sha256, gate="craft", reviewer="Synthetic reviewer",
            method="human", decision="needs-work", evidence="Synthetic test rejection; no actual artwork reviewed."), OWNER)
    else:
        body.expected_old_ids = [native_prepared.spec.canonical]
    before = seeded.snapshot()
    with pytest.raises(HTTPException) as rejected:
        NativeActivation(seeded).activate(native_prepared.spec.canonical, body, OWNER)
    assert rejected.value.status_code == 409 and seeded.snapshot() == before


def test_native_activation_endpoint_is_owner_only_and_bound_to_exact_body(
    seeded: Store, native_prepared: PreparedNative, settings: Settings,
) -> None:
    import_native(seeded, [native_prepared])
    approve_fixture(seeded, native_prepared)
    body = activation_body(native_prepared).model_dump(mode="json")
    with TestClient(create_app(settings)) as client:
        route = f"/api/v1/owner/lessons/{native_prepared.spec.canonical}/activate"
        client.post("/api/v1/auth/login", json={"name": "Family", "code": settings.invite_code})
        before = seeded.snapshot()
        assert client.post(route, json=body).status_code == 403 and seeded.snapshot() == before
        client.post("/api/v1/auth/login", json={"name": "Owner", "code": settings.owner_code})
        assert client.post(route, json={**body, "automatic": True}).status_code == 422
        assert client.post(route, json=body).json()["reused"] is False
        assert client.post(route, json=body).json()["reused"] is True
        assert client.post(route, json={**body, "expected_old_ids": ["another-head"]}).status_code == 409
        assert client.post("/api/v1/owner/lessons/missing/activate", json=body).status_code == 404
