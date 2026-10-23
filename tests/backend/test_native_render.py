"""Parity checks for the trusted player's dynamic SVG updates and offline media export."""

import pytest

from backend.native_proof import inspect_svg
from backend.native_render import RawFrame, materialize, wrap_scene


def frame(svg: str, updates: list[dict[str, str]] | None = None) -> RawFrame:
    return RawFrame.model_validate({"cue_id": "working", "time": 2, "scenario_id": "",
        "controls": {}, "svg": svg, "labels": [{"text": "Working input", "x": 100, "y": 80}],
        "viewport": {"x": 0, "y": 0, "width": 720, "height": 620},
        "caption": "An illustrative logical calculation, with its input supplied.",
        "alt": "The ready input arrives at the calculation slot.", "attributes": updates or []})


def test_media_applies_player_updates_before_proof_or_raster() -> None:
    before = frame('<g data-copy=""><rect width="12" height="20"/></g>')
    after = frame(before.svg, [{"selector": "[data-copy]", "name": "transform", "value": "translate(80 40)"}])
    initial, final = materialize(before), materialize(after)
    assert inspect_svg(initial)[1] != inspect_svg(final)[1]
    assert 'transform="translate(80 40)"' in final.svg
    assert "attributes" not in final.model_dump()
    exported = wrap_scene(final)
    assert "Working input" in exported
    assert 'viewBox="0.0 0.0 720.0 620.0"' in exported


@pytest.mark.parametrize("svg", [
    '<rect width="30" height="20" onclick="alert(1)"/>',
    '<foreignObject><div>remote body</div></foreignObject>',
    '<image href="https://example.com/tracker.png"/>',
    '<!DOCTYPE svg [<!ENTITY x "unsafe">]><g/>',
])
def test_export_refuses_executable_or_external_scene_content(svg: str) -> None:
    with pytest.raises(ValueError):
        materialize(frame(svg))


def test_a_changed_renderer_selector_cannot_silently_export_an_old_pose() -> None:
    value = frame('<rect data-progress="" width="30" height="20"/>',
        [{"selector": "[data-missing]", "name": "width", "value": "90"}])
    with pytest.raises(ValueError, match="no corresponding"):
        materialize(value)
