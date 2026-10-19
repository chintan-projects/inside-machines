"""Check the real authored library, independently of provider fixtures."""

import pytest

from backend.contracts import LessonSpec
from backend.render import draw_scene
from backend.seed_aircon import aircon
from backend.seed_cooker import cooker
from backend.seed_washer import washer


@pytest.mark.parametrize("spec", [washer(), cooker(), aircon()], ids=lambda spec: spec.canonical)
def test_starters_are_connected_and_renderable(spec: LessonSpec) -> None:
    """Every authored stage references real parts and the actual renderer can draw it."""
    assert 18 <= len(spec.parts) <= 65
    assert sum(len(s.narration.split()) for s in spec.stages) <= 260
    assert len(spec.questions) >= 3 and spec.sources and spec.assumptions
    elapsed = 0.0
    for stage in spec.stages:
        image = draw_scene(spec, elapsed + stage.duration / 2, width=450, height=270)
        assert image.getbbox() is not None
        assert len(image.getcolors(450 * 270) or []) > 20
        elapsed += stage.duration
