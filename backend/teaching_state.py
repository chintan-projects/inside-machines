"""Pure scene sampling. Qualitative causal rules live in the versioned lesson data."""

import math

from .contracts import LessonSpec
from .teaching_contracts import Beat, Change, Pose, Scenario


def teaching_at(spec: LessonSpec, seconds: float) -> tuple[Beat, float]:
    """Map a media checkpoint to a stable beat and a deliberate visual transition."""
    if spec.teaching is None or not math.isfinite(seconds):
        raise ValueError("A teaching scene needs a valid CE lesson and clock")
    elapsed = 0.0
    for index, stage in enumerate(spec.stages):
        if seconds < elapsed + stage.duration or index == len(spec.stages) - 1:
            fraction = max(0.0, min(1.0, (seconds - elapsed) / stage.duration))
            # Establish the input, show the change, then hold the result to inspect.
            progress = max(0.0, min(1.0, (fraction - 0.12) / 0.58))
            return spec.teaching.beats[index], progress
        elapsed += stage.duration
    raise ValueError("Lesson has no teaching checkpoints")


def scenario_for(spec: LessonSpec, beat: Beat, scenario_id: str | None) -> Scenario | None:
    """Reject unknown/cross-beat actions instead of quietly showing another state."""
    if spec.teaching is None:
        raise ValueError("Missing teaching contract")
    if scenario_id is None:
        return next((s for s in spec.teaching.scenarios if s.beat == beat.id), None)
    scenario = next((s for s in spec.teaching.scenarios if s.id == scenario_id), None)
    if scenario is None or scenario.beat != beat.id:
        raise ValueError("Scenario is unavailable for this beat")
    return scenario


def sampled_pose(change: Change | None, progress: float, base_fill: str = "") -> Pose:
    """Apply only the bounded interpolation semantics of the safe drawing contract."""
    if not math.isfinite(progress):
        raise ValueError("Scene progress must be finite")
    if change is None:
        return Pose()
    p = max(0.0, min(1.0, progress))
    poses = [change.before, *change.via, change.after]
    segment = min(len(poses) - 2, math.floor(p * (len(poses) - 1)))
    p = p * (len(poses) - 1) - segment
    a, b = poses[segment], poses[segment + 1]
    a_fill, b_fill = a.fill or base_fill, b.fill or base_fill
    fill = a_fill or b_fill
    if a_fill and b_fill:
        colors = [
            math.floor(int(a_fill[i : i + 2], 16) * (1 - p) + int(b_fill[i : i + 2], 16) * p + 0.5)
            for i in (1, 3, 5)
        ]
        fill = "#" + "".join(f"{c:02x}" for c in colors)
    return Pose(
        x=a.x + (b.x - a.x) * p,
        y=a.y + (b.y - a.y) * p,
        sx=a.sx + (b.sx - a.sx) * p,
        sy=a.sy + (b.sy - a.sy) * p,
        angle=a.angle + (b.angle - a.angle) * p,
        fill=fill,
        opacity=a.opacity + (b.opacity - a.opacity) * p,
    )
