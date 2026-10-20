"""CE contract, causal states, export agreement and immutable revision regressions."""

import hashlib
import json
import subprocess
from typing import cast

import pytest
from pydantic import ValidationError

from backend.ac_concept import aircon_concept
from backend.concept_publication import ConceptArtifact, authored_lessons, import_concepts, validate_concept
from backend.contracts import AuthorLessonSpec, LessonSpec
from backend.evaluation import HumanRatings, cases, comparison, packet
from backend.quality import learning_issues, require_learning_quality
from backend.renderer_assets import authored_context
from backend.section_assets import section_asset
from backend.starters import digest_spec
from backend.store import Database, Store
from backend.teaching_contracts import Change, Pose
from backend.teaching_state import sampled_pose, scenario_for, teaching_at
from backend.teaching_svg import graphic_scene, teaching_image, teaching_svg
from backend.washer_concept import washer_concept


def test_pipe_motion_passes_through_actual_pump_and_matches_javascript() -> None:
    """The marker crosses the pump rather than taking a diagonal shortcut; exports agree."""
    spec = washer_concept()
    assert spec.teaching is not None
    beat = spec.teaching.beats[2]
    change = next(c for c in beat.changes if c.target.endswith("water"))
    marker = next(p for p in spec.graphics if p.id == change.target)
    pose = sampled_pose(change, 0.5)
    assert (marker.x + marker.w / 2 + pose.x, marker.y + marker.h / 2 + pose.y) == (620, 480)
    samples = [-1, 0, 0.125, 0.25, 0.5, 0.75, 0.99, 1, 2]
    program = "import {sampledPose} from './web/teaching/state.ts'; const {change,samples}=JSON.parse(process.argv[1]); process.stdout.write(JSON.stringify(samples.map(p=>sampledPose(change,p))));"
    result = subprocess.run(
        [
            "node",
            "--experimental-strip-types",
            "--input-type=module",
            "-e",
            program,
            json.dumps({"change": change.model_dump(), "samples": samples}),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    assert json.loads(result.stdout) == [sampled_pose(change, p).model_dump() for p in samples]


def test_authored_paths_have_real_changes_and_transfer() -> None:
    """Different mechanisms share the contract without becoming AC reskins."""
    for spec, _ in authored_lessons():
        require_learning_quality(spec)
        assert spec.teaching is not None
        assert spec.teaching.prediction.prompt != spec.teaching.transfer.prompt
        for i, stage in enumerate(spec.stages):
            at = sum(s.duration for s in spec.stages[:i])
            beat, before = teaching_at(spec, at)
            assert before == 0 and beat.stage == i and stage.input_state != stage.output_state
            assert teaching_at(spec, at + stage.duration * 0.9)[1] == 1
            assert graphic_scene(spec, at) != graphic_scene(spec, at + stage.duration * 0.9)
            svg = teaching_svg(spec, at + stage.duration * 0.9)
            assert stage.title in svg
            if spec.teaching.renderer == "authored-sections-v1" and i == len(spec.stages) - 1:
                assert section_asset(spec, -1)[0] in svg
            else:
                assert "data-graphic=" in svg
        end = sum(s.duration for s in spec.stages) - 1
        assert teaching_svg(spec, end, spec.teaching.scenarios[0].id) != teaching_svg(
            spec, end, spec.teaching.scenarios[1].id
        )


def test_ac_pressure_phase_and_compression_are_distinct() -> None:
    """The inset changes volume and piston position rather than just shell color."""
    spec = aircon_concept()
    assert spec.teaching is not None
    beat = spec.teaching.beats[2]
    properties = {p.name: (p.before, p.after) for p in beat.properties}
    assert properties["Phase"] == ("Vapor", "Vapor") and properties["Pressure"] == ("Low", "High")
    assert next(c for c in beat.changes if c.target == "compress-gas").after.sx < 1
    assert next(c for c in beat.changes if c.target == "compress-piston").after.x < 0
    assert spec.teaching.operation == "simultaneous"
    assert "electrical" in spec.teaching.scenarios[1].explanation


@pytest.mark.parametrize(
    "mutation", ["version", "source", "dependency", "graphic", "renderer", "scenario", "core"]
)
def test_untrusted_contract_references_fail(ce_spec: LessonSpec, mutation: str) -> None:
    """Unknown actions, lost claims and cross-version reinterpretation fail closed."""
    candidate = ce_spec.model_copy(deep=True)
    assert candidate.teaching is not None
    if mutation == "version":
        candidate.version = 1
    if mutation == "source":
        candidate.teaching.claims[0].source = 7
    if mutation == "dependency":
        candidate.teaching.beats[0].requires = ["add-work"]
    if mutation == "graphic":
        candidate.teaching.beats[0].changes[0].target = "unknown"
    if mutation == "renderer":
        candidate.teaching.renderer = "ac-cutaway-v2"
    if mutation == "scenario":
        candidate.teaching.scenarios[0].beat = "unknown"
    if mutation == "core":
        candidate.teaching.core.append("unknown")
    with pytest.raises(ValidationError):
        LessonSpec.model_validate(candidate.model_dump())


def test_quality_rejects_highlight_only_and_clipped_states(ce_spec: LessonSpec) -> None:
    """Readable bounded causal changes are required beyond schema-valid JSON."""
    assert ce_spec.teaching is not None
    beat = ce_spec.teaching.beats[0]
    beat.changes = [Change(target=beat.changes[0].target, before=Pose(), after=Pose(fill="#ff0000"))]
    assert any("not just color" in s for s in learning_issues(ce_spec))
    beat.changes[0].after = Pose(x=850)
    assert any("leaves the canvas" in s for s in learning_issues(ce_spec))
    ce_spec.stages[0].source_indices = []
    assert any("claim evidence" in s for s in learning_issues(ce_spec))
    ce_spec.parts = [p for p in ce_spec.parts if p.id != "label-compressor"]
    assert any("Every core" in s for s in learning_issues(ce_spec))


def test_scene_clock_actions_and_escaped_export(ce_spec: LessonSpec) -> None:
    """Renderers receive bounded primitives, not arbitrary markup or scenario code."""
    assert ce_spec.teaching is not None
    assert teaching_at(ce_spec, -1)[1] == 0 and teaching_at(ce_spec, 999)[0].stage == 2
    for clock in (float("nan"), float("inf")):
        with pytest.raises(ValueError):
            teaching_at(ce_spec, clock)
    with pytest.raises(ValueError):
        scenario_for(ce_spec, ce_spec.teaching.beats[0], "inside")
    with pytest.raises(ValueError):
        scenario_for(ce_spec, ce_spec.teaching.beats[-1], "unknown")
    change = Change(target="intro-heat", before=Pose(fill="#000000"), after=Pose(x=100, fill="#ffffff"))
    assert sampled_pose(change, 0.5).fill == "#808080"
    assert sampled_pose(change, -1).x == 0 and sampled_pose(change, 2).x == 100
    label = next(p for p in ce_spec.graphics if p.shape == "text")
    label.label = "<script>alert(1)</script>"
    svg = teaching_svg(ce_spec, 3)
    assert "<script>" not in svg and "&lt;script&gt;" in svg
    assert teaching_image(ce_spec, 3, 320, 216).size == (320, 216)
    for context in ("outside", "inside"):
        assert "Indoor coil" in authored_context(context) and "tabindex=" not in authored_context(context)
    with pytest.raises(ValueError):
        authored_context("../secret")


def test_v1_fingerprints_and_new_author_boundary(spec: LessonSpec) -> None:
    """The legacy reader/hash survive while newly authored output must use v2."""
    original = spec.model_dump(mode="json", exclude={"graphics", "teaching"})
    expected = hashlib.sha256(
        json.dumps(original, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert digest_spec(LessonSpec.model_validate(original)) == expected
    with pytest.raises(ValidationError):
        AuthorLessonSpec.model_validate(original)


def test_import_preserves_private_history_and_rejects_replacement(store: Store) -> None:
    """Publication is atomic/idempotent and cannot overwrite published revisions."""
    from backend.ac_craft import aircon_craft

    old = aircon_craft()

    def history(db: Database) -> None:
        db.lessons[old.canonical] = {"id": old.canonical, "spec": old.model_dump(mode="json")}
        db.chats["private"] = {"lesson_id": old.canonical, "messages": [{"text": "private question"}]}

    store.transaction(history)
    spec = aircon_concept()
    artifact = ConceptArtifact(
        spec=spec,
        spec_sha256=digest_spec(spec),
        video="fixture.mp4",
        video_sha256="0" * 64,
        replaces=["air-conditioner", "air-conditioner-craft"],
    )
    assert import_concepts(store, [artifact]) == (1, 0) and import_concepts(store, [artifact]) == (0, 1)
    before = store.snapshot()
    with pytest.raises(ValueError, match="immutable"):
        import_concepts(store, [artifact.model_copy(update={"video_sha256": "1" * 64})])
    assert store.snapshot() == before and before.chats["private"]["lesson_id"] == old.canonical
    assert before.lessons[old.canonical]["spec"] == old.model_dump(mode="json")
    with pytest.raises(ValueError):
        validate_concept(artifact.model_copy(update={"replaces": ["unknown"]}))


def test_evaluation_keeps_missing_judgments_unmeasured(store: Store, ce_spec: LessonSpec) -> None:
    """No model/cost or learning result is invented for an authored artifact."""
    store.transaction(lambda db: db.lessons.update({"fixture": {"spec": ce_spec.model_dump(mode="json")}}))
    candidate = packet(store, "fixture", "washer")
    row = cast(list[dict[str, object]], comparison([candidate])["rows"])[0]
    assert row["quality_result"] == "unmeasured" and row["cost_recorded_usd"] is None
    candidate.ratings = HumanRatings(
        reviewer="Synthetic test reviewer",
        factual=2,
        causal=2,
        visual=2,
        simplicity=2,
        transfer=2,
        critical_error=False,
    )
    assert cast(list[dict[str, object]], comparison([candidate])["rows"])[0]["human_review_complete"]
    with pytest.raises(ValueError):
        packet(store, "fixture", "missing")
    with pytest.raises(ValueError):
        comparison([])
    assert {"scope", "ambiguous"} <= {c.id for c in cases()}


def test_context_motion_cannot_diverge_from_static_video(ce_spec: LessonSpec) -> None:
    """Legacy motion in a new locator scene cannot bypass the shared causal storyboard."""
    from backend.contracts import Motion

    ce_spec.parts[0].motion = [Motion(stage=0, kind="translate", amount=100, axis="x")]
    assert any("context parts must be static" in issue for issue in learning_issues(ce_spec))


def test_identity_fill_resolves_to_the_original_graphic_color() -> None:
    """An empty before/after fill retains the graphic rather than revealing its result early."""
    change = Change(target="sample", before=Pose(), after=Pose(fill="#ffffff"))
    assert sampled_pose(change, 0, "#000000").fill == "#000000"
    assert sampled_pose(change, 0.5, "#000000").fill == "#808080"
    change = Change(target="sample", before=Pose(fill="#ffffff"), after=Pose())
    assert sampled_pose(change, 1, "#000000").fill == "#000000"
