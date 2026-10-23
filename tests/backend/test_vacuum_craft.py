"""Trusted artwork binding, qualitative counterfactual and immutable export checks."""

import pytest

from backend.quality import learning_issues, require_learning_quality
from backend.section_assets import section_asset, vacuum_art_fingerprint
from backend.teaching_state import sampled_pose, scenario_for
from backend.teaching_svg import graphic_scene, teaching_svg
from backend.vacuum_concept import vacuum_concept
from backend.washer_concept import washer_concept


def test_clogged_bag_restricts_air_but_does_not_stop_the_fan() -> None:
    """The taught consequence is airflow restriction, not an invented stalled motor."""
    spec = vacuum_concept()
    require_learning_quality(spec)
    assert spec.teaching is not None
    beat = spec.teaching.beats[2]
    clogged = scenario_for(spec, beat, "clogged")
    assert clogged is not None
    base = {c.target: c for c in beat.changes}
    changed = {**base, **{c.target: c for c in clogged.changes}}
    assert sampled_pose(changed["vb-impeller"], 1).angle == sampled_pose(base["vb-impeller"], 1).angle > 0
    assert sampled_pose(changed["vb-air-0"], 1).x < sampled_pose(base["vb-air-0"], 1).x
    assert sampled_pose(changed["vb-dust-0"], 1).x < sampled_pose(base["vb-dust-0"], 1).x
    assert "not measured speed" in spec.teaching.operation_note
    assert "complete filtration" in spec.teaching.scenarios[0].explanation


def test_artwork_binds_static_surfaces_without_hiding_causal_changes() -> None:
    """Every output uses the same trusted source while movable markers remain data."""
    spec = vacuum_concept()
    assert spec.teaching is not None
    assert spec.teaching.renderer_fingerprint == vacuum_art_fingerprint()
    for beat in spec.teaching.beats:
        source, replaced = section_asset(spec, beat.stage)
        assert "linearGradient" in source and replaced <= set(beat.graphics)
        assert not {c.target for c in beat.changes} & replaced
        at = sum(s.duration for s in spec.stages[: beat.stage]) + spec.stages[beat.stage].duration * 0.6
        export = graphic_scene(spec, at)
        assert source in export
        assert all(f'data-graphic="{c.target}"' in export for c in beat.changes)
    assert 'width="880" height="405"' in teaching_svg(spec, 10)
    assert 'width="470" height="310"' in teaching_svg(washer_concept(), 10)


def test_unknown_artwork_revision_fails_closed_and_static_targets_cannot_move() -> None:
    """An older artifact cannot silently acquire changed authored SVG geometry."""
    spec = vacuum_concept()
    assert spec.teaching is not None
    spec.teaching.renderer_fingerprint = "f" * 64
    assert any("revision is unavailable" in issue for issue in learning_issues(spec))
    with pytest.raises(ValueError, match="artwork revision"):
        section_asset(spec, 0)
    spec = vacuum_concept()
    assert spec.teaching is not None
    spec.teaching.beats[0].changes[0].target = "vf-motor-core"
    assert any("Static artwork" in issue for issue in learning_issues(spec))


def test_air_and_dirt_markers_keep_separate_positions_in_the_passage() -> None:
    """Markers must not merge into one symbol midway or cross the hose wall at the end."""
    spec = vacuum_concept()
    assert spec.teaching is not None
    parts = {p.id: p for p in spec.graphics}
    for beat in spec.teaching.beats[1:]:
        for prefix in ("vi-air-", "vi-dust-") if beat.stage == 1 else ("vb-air-", "vb-dust-"):
            changes = [c for c in beat.changes if c.target.startswith(prefix)]
            for progress in (0.5, 1):
                centers = []
                for c in changes:
                    p, pose = parts[c.target], sampled_pose(c, progress)
                    x, y = p.x + p.w / 2 + pose.x, p.y + p.h / 2 + pose.y
                    centers.append((round(x, 3), round(y, 3)))
                    if beat.stage == 1 and progress == 1:
                        assert 410 <= x <= 436 and 148 <= y <= 286
                assert len(set(centers)) == len(centers)


def test_video_reconnects_the_whole_and_scenario_exports_show_the_tested_condition() -> None:
    """Base narration never describes an unseen clog; explicit comparisons stay visible."""
    spec = vacuum_concept()
    assert spec.teaching is not None
    start = sum(s.duration for s in spec.stages[:2])
    whole, _ = section_asset(spec, -1)
    assert whole in teaching_svg(spec, start + spec.stages[2].duration * 0.55)
    comparison = teaching_svg(spec, start + spec.stages[2].duration * 0.8, "clogged")
    assert "vb-fiber" in comparison and "Pause and predict" not in comparison
    assert "clog" not in spec.stages[2].narration
    assert spec.teaching.scenarios[1].claims == ["claim-clog"]
    spec.canonical = "gpu"
    with pytest.raises(ValueError, match="artwork revision"):
        section_asset(spec, 0)


def test_video_copy_fits_the_frame_with_the_actual_bundled_font() -> None:
    """A long reassembly sentence must wrap before it is clipped by the video edge."""
    from xml.etree import ElementTree

    from PIL import ImageFont

    from backend.settings import ROOT

    spec = vacuum_concept()
    start = 0.0
    for stage in spec.stages:
        root = ElementTree.fromstring(teaching_svg(spec, start + stage.duration * 0.55))
        for node in root.findall("{http://www.w3.org/2000/svg}text"):
            font = ImageFont.truetype(
                str(ROOT / "public/fonts/Inter.ttf"), size=int(node.attrib["font-size"])
            )
            assert float(node.attrib["x"]) + font.getlength(node.text or "") <= 945
        start += stage.duration
