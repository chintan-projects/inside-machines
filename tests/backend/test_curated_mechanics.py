"""Physical geometry invariants; schema validity alone cannot detect these errors."""

import math

import pytest

from backend.curated import mechanics
from backend.curated.catalog import SYSTEMS
from backend.teaching_quality import _bounds
from backend.teaching_state import sampled_pose


@pytest.mark.parametrize("key", ["car", "refrigerator", "air-conditioner", "heat-pump"])
def test_working_stroke_gas_ends_at_piston_face(key: str) -> None:
    """Expanding gas never leaks under the piston; compression keeps a sealed top."""
    plan = SYSTEMS[key]
    index = next(i for i, step in enumerate(plan.steps) if step.style == "piston")
    view = mechanics.piston(plan, plan.steps[index], index)
    parts = {p.id.removeprefix(view.drawing.prefix): p for p in view.drawing.parts}
    changes = {c.target: c for c in view.changes}
    for fraction in [i/32 for i in range(33)]:
        gas = _bounds(parts["sealed-gas"], changes[parts["sealed-gas"].id], fraction)
        piston = _bounds(parts["piston"], changes[parts["piston"].id], fraction)
        rod = _bounds(parts["rod"], changes[parts["rod"].id], fraction)
        housing = _bounds(parts["drive-housing"], None, fraction)
        assert gas[1] == pytest.approx(165)
        assert gas[3] == pytest.approx(piston[1])
        assert rod[1] == pytest.approx(piston[3])
        assert housing[1] < rod[3] <= housing[3]


def test_liquid_pump_displaces_water_into_open_outlet() -> None:
    """The changing chamber has an exit, and its outlet markers remain inside that exit."""
    plan = SYSTEMS["espresso-machine"]
    view = mechanics.piston(plan, plan.steps[0], 0)
    parts = {p.id.removeprefix(view.drawing.prefix): p for p in view.drawing.parts}
    changes = {c.target: c for c in view.changes}
    assert "sealed-gas" not in parts
    assert "inlet-check-seated" in parts and "outlet-check-open" in parts
    for fraction in [i/32 for i in range(33)]:
        water = _bounds(parts["water-chamber"], changes[parts["water-chamber"].id], fraction)
        piston = _bounds(parts["piston"], changes[parts["piston"].id], fraction)
        assert water[1] == pytest.approx(170)
        assert water[3] == pytest.approx(piston[1])
        for j in range(3):
            marker = parts[f"delivered-water-{j}"]
            left, top, right, bottom = _bounds(marker, changes[marker.id], fraction)
            assert 560 <= left < right <= 745 and 192 <= top < bottom <= 218


@pytest.mark.parametrize("key", ["table-fan", "vacuum-cleaner"])
def test_rotor_pivot_is_its_shaft_and_stays_inside_guard(key: str) -> None:
    """A rotating blade must not swing around the old path's first point."""
    plan = SYSTEMS[key]
    view = mechanics.rotor(plan, plan.steps[0], 0)
    rotor = next(p for p in view.drawing.parts if p.id.endswith("-rotor"))
    assert rotor.shape == "polygon"
    assert (rotor.x+rotor.w/2, rotor.y+rotor.h/2) == (540, 280)
    assert max(math.hypot(x-540, y-280) for x, y in rotor.points) < 150


def test_fast_spin_load_follows_drum_instead_of_staying_in_room_coordinates() -> None:
    """Held against a rotating drum means an orbit, with fabric inside its cavity."""
    plan = SYSTEMS["washing-machine"]
    view = mechanics.drum(plan, plan.steps[1], 1)
    parts = {p.id: p for p in view.drawing.parts}
    fast = {c.target: c for c in view.alternate}
    for identity, change in fast.items():
        if "cloth-" not in identity and "lifter-" not in identity:
            continue
        p = parts[identity]
        center = (p.x+p.w/2, p.y+p.h/2)
        assert change.before != change.after
        for pose in [change.before, *change.via, change.after]:
            radius = math.hypot(center[0]+pose.x-450, center[1]+pose.y-270)
            assert radius == pytest.approx(108 if "cloth-" in identity else 116)
        for fraction in [i/32 for i in range(33)]:
            pose = sampled_pose(change, fraction)
            angle = math.radians(pose.angle)
            for x, y in p.points or [[p.x, p.y], [p.x+p.w, p.y], [p.x+p.w, p.y+p.h], [p.x, p.y+p.h]]:
                dx, dy = x-center[0], y-center[1]
                actual_x = center[0]+pose.x+dx*math.cos(angle)-dy*math.sin(angle)
                actual_y = center[1]+pose.y+dx*math.sin(angle)+dy*math.cos(angle)
                assert math.hypot(actual_x-450, actual_y-270) < 132
