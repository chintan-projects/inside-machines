"""Owner-authored depth context binds the existing lesson pipeline to one core."""

import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .contracts import LessonSpec
from .learning_paths import LearningPath, PathNode
from .starters import digest_spec
from .store import Database

DepthRole = Literal["insight", "model"]


class DepthContext(BaseModel):
    """Trusted immutable job input, not a new public path or release decision."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal["depth-authoring-1"] = "depth-authoring-1"
    parent_lesson_id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,79}$")
    parent_spec_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    role: DepthRole
    node_id: DepthRole
    path: LearningPath
    parent_example: dict[str, object]


def depth_context(root_id: str, root: LessonSpec, question: str, role: DepthRole,
                  canonical: str) -> DepthContext:
    """Compose bounded parent context entirely from the stored immutable core."""
    if root.version != 2 or root.teaching is None:
        raise ValueError("Depth authoring requires a CE core lesson")
    label = "Show me the insight" if role == "insight" else "Explain the model"
    path = LearningPath(
        schema_version="learning-path-1", id=canonical+"-context", title=root.title[:120],
        example=(root.family + ". " + root.big_idea)[:400], entry="core",
        nodes=[
            PathNode(id="core", role="core", label="Core explanation", question=root.question,
                     outcome=root.teaching.goal[:400], lesson_id=root_id, prerequisites=[],
                     next=[role], queries=["core explanation"]),
            PathNode(id=role, role=role, label=label, question=question,
                     outcome=("Answer this follow-up and reconnect it to " + root.title)[:400],
                     lesson_id=canonical, prerequisites=["core"], next=[], queries=[question[:160]]),
        ],
    )
    return DepthContext(
        parent_lesson_id=root_id, parent_spec_sha256=digest_spec(root), role=role, node_id=role, path=path,
        parent_example={
            "root_question": root.question, "family": root.family, "big_idea": root.big_idea,
            "components": [{"id": p.id, "name": p.name, "description": p.description}
                           for p in root.parts if p.id in root.teaching.core],
            "story": [{"title": s.title, "input": s.input_state, "output": s.output_state,
                       "explanation": s.explanation} for s in root.stages],
            "visible_labels": [{"id": p.id, "label": p.label}
                               for p in [*root.parts, *root.graphics] if p.shape == "text"],
        },
    )


def job_depth_context(job: dict[str, object], db: Database) -> DepthContext | None:
    """Reject stale/tampered context before spending or registering a new artifact."""
    raw = job.get("path_context")
    if raw is None:
        if job.get("node_parent") or job.get("node_role"):
            raise ValueError("The depth draft lost its parent context")
        return None
    context = DepthContext.model_validate(raw)
    parent = db.lessons.get(context.parent_lesson_id)
    if not parent or parent.get("archived") or parent.get("superseded_by"):
        raise ValueError("The depth draft's core is unavailable or superseded")
    expected = depth_context(
        context.parent_lesson_id, LessonSpec.model_validate(parent["spec"]),
        str(job["question"]), context.role, str(job["canonical"]),
    )
    if (context != expected or job.get("node_parent") != context.parent_lesson_id
            or job.get("node_role") != context.role or job.get("revision_of")):
        raise ValueError("The depth draft no longer matches its bound core and question")
    return context


def depth_research_question(context: DepthContext) -> str:
    """Retrieve evidence for the scoped question without treating parent text as a source."""
    return json.dumps({
        "question": context.path.nodes[1].question,
        "parent_question": context.path.nodes[0].question,
        "shared_example": context.path.example,
        "scope": context.role,
    })
