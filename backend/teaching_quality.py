"""CE structural checks; their success never implies scientific or human approval."""

import math

from .contracts import LessonSpec, Part
from .teaching_contracts import Change
from .teaching_state import sampled_pose


def _bounds(part: Part, change: Change | None, progress: float) -> tuple[float, float, float, float]:
    pose = sampled_pose(change, progress, part.color)
    points = (
        part.points
        if part.shape in ("path", "polygon")
        else [
            [part.x, part.y],
            [part.x + part.w, part.y],
            [part.x, part.y + part.h],
            [part.x + part.w, part.y + part.h],
        ]
    )
    if part.shape == "text":
        points = [[part.x, part.y], [part.x + len(part.label) * part.h * 0.62, part.y + part.h]]
    cx, cy = part.x + part.w / 2, part.y + part.h / 2
    angle = math.radians(pose.angle)
    corners = [
        (
            cx + pose.x + (p[0] - cx) * pose.sx * math.cos(angle) - (p[1] - cy) * pose.sy * math.sin(angle),
            cy + pose.y + (p[0] - cx) * pose.sx * math.sin(angle) + (p[1] - cy) * pose.sy * math.cos(angle),
        )
        for p in points
    ]
    return (
        min(p[0] for p in corners),
        min(p[1] for p in corners),
        max(p[0] for p in corners),
        max(p[1] for p in corners),
    )


def teaching_issues(spec: LessonSpec) -> list[str]:
    """Check real references, geometric changes, readable labels and bounded poses."""
    teaching = spec.teaching
    if teaching is None:
        return ["CE lessons require a teaching contract"]
    issues: list[str] = []
    if teaching.renderer != "ac-cutaway-v2" and any(p.motion for p in spec.parts):
        issues.append("CE context parts must be static; causal motion belongs to teaching graphic changes")
    if teaching.renderer == "ac-cutaway-v2":
        from .renderer_assets import ac_renderer_fingerprint

        if teaching.renderer_fingerprint != ac_renderer_fingerprint():
            issues.append(
                "Authored cutaway revision does not match this lesson; preserve its video and author a new revision"
            )
    labels = {p.id[6:] for p in spec.parts if p.shape == "text" and p.id.startswith("label-")}
    if not set(teaching.core) <= labels:
        issues.append("Every core component requires a permanent label")
    graphics = {p.id: p for p in spec.graphics}
    claims = {c.id: c for c in teaching.claims}
    for beat in teaching.beats:
        if teaching.renderer == "authored-sections-v1":
            from .section_assets import section_asset

            try:
                _, replaced = section_asset(spec, beat.stage)
                moving = {c.target for c in beat.changes} | {
                    c.target for s in teaching.scenarios if s.beat == beat.id for c in s.changes
                }
                if moving & replaced:
                    issues.append("Static artwork cannot replace an animated mechanism identity")
                if not replaced <= set(beat.graphics):
                    issues.append("Artwork replaces unknown geometry")
            except ValueError:
                issues.append("Authored section revision is unavailable; preserve its original media")
        stage = spec.stages[beat.stage]
        if not any(graphics[id].shape == "text" and graphics[id].label.strip() for id in beat.graphics):
            issues.append(f"Beat {beat.id} needs a labeled self-contained causal detail view")
        if len(stage.title) > 60 or len(beat.bridge) > 180 or len(beat.static_explanation) > 280:
            issues.append(f"Beat {beat.id} copy exceeds the readable scene layout")
        if sum(len(p.name) + len(p.before) + len(p.after) for p in beat.properties) > 170:
            issues.append(f"Beat {beat.id} needs concise qualitative state labels")
        if stage.focus not in teaching.core:
            issues.append(f"Beat {beat.id} must focus a labeled core component")
        if not {claims[c].source for c in beat.claims} <= set(stage.source_indices):
            issues.append(f"Beat {beat.id} source indices must include its claim evidence")
        if not any(
            any(
                getattr(c.before, k) != getattr(pose, k)
                for k in ("x", "y", "sx", "sy", "angle", "opacity")
                for pose in [*c.via, c.after]
            )
            for c in beat.changes
        ):
            issues.append(f"Beat {beat.id} needs a visible mechanism change, not just color emphasis")
        changes = {c.target: c for c in beat.changes}
        variants = [
            changes,
            *[
                {**changes, **{c.target: c for c in s.changes}}
                for s in teaching.scenarios
                if s.beat == beat.id
            ],
        ]
        for id in beat.graphics:
            part = graphics[id]
            if part.motion:
                issues.append(f"Graphic {id} must use CE poses rather than legacy motion")
            if part.shape == "text" and (part.h < 28 or not part.label.strip()):
                issues.append(f"Graphic {id} text is absent or too small")
            for variant in variants:
                change = variant.get(id)
                samples = {i / 16 for i in range(17)}
                if change:
                    samples.update(i / (len(change.via) + 1) for i in range(len(change.via) + 2))
                for progress in sorted(samples):
                    bounds = _bounds(part, variant.get(id), progress)
                    if min(bounds[:2]) < -1 or bounds[2] > 901 or bounds[3] > 541:
                        issues.append(f"Graphic {id} leaves the canvas in beat {beat.id}")
                        break
    return list(dict.fromkeys(issues))
