"""Deterministic publication gates; these do not certify scientific correctness."""

from .contracts import LessonSpec


class LearningQualityError(ValueError):
    """Bounded, non-private authoring findings suitable for owner diagnostics."""

    def __init__(self, issues: list[str]) -> None:
        """Retain individual findings without storing a provider response or prompt."""
        self.issues = tuple(issues)
        super().__init__("Lesson failed learning-quality checks: " + "; ".join(issues))


def learning_issues(spec: LessonSpec) -> list[str]:
    """Reject missing component identification, causal staging or usable evidence."""
    issues: list[str] = []
    parts = {p.id: p for p in spec.parts}
    labels = [p for p in spec.parts if p.shape == "text" and p.id.startswith("label-")]
    targets = {p.id[6:] for p in labels if p.id[6:] in parts}
    if len(targets) < 3:
        issues.append("At least three working components need visible, anchored labels")
    for label in labels:
        if label.id[6:] not in parts:
            issues.append(f"Label {label.id} has no matching component")
        if label.h < 32 or not label.label.strip():
            issues.append(f"Label {label.id} is absent or too small")
        # Conservative deterministic text bounds, in the same 900×540 authoring space.
        if label.x + len(label.label) * label.h * 0.62 > 900 or label.y + label.h > 540:
            issues.append(f"Label {label.id} falls outside the drawing")
    for index, stage in enumerate(spec.stages):
        if not stage.input_state.strip() or not stage.output_state.strip():
            issues.append(f"Chapter {index + 1} needs a clear input and output")
        if not stage.focus or stage.focus not in stage.parts:
            issues.append(f"Chapter {index + 1} needs a focus component used in that chapter")
        if not stage.source_indices:
            issues.append(f"Chapter {index + 1} needs an evidence reference")
        if stage.focus and stage.focus not in targets:
            issues.append(f"Chapter {index + 1}'s focus component needs a visible label")
    # A clear text label must not physically cover another core label.
    for i, a in enumerate(labels):
        for b in labels[i + 1 :]:
            ax, ay = a.x + len(a.label) * a.h * 0.62, a.y + a.h + 8
            bx, by = b.x + len(b.label) * b.h * 0.62, b.y + b.h + 8
            if max(a.x, b.x) < min(ax, bx) and max(a.y, b.y) < min(ay, by):
                issues.append(f"Labels {a.id} and {b.id} overlap")
    return issues


def require_learning_quality(spec: LessonSpec) -> None:
    """Fail before narration or publication when basic teaching structure is absent."""
    issues = learning_issues(spec)
    if issues:
        raise LearningQualityError(issues)
