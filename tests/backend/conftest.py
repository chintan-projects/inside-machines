"""Explicit synthetic fixtures; these are never published as live AI output."""

from dataclasses import replace
from pathlib import Path

import pytest

from backend.contracts import LessonSpec
from backend.domain import User
from backend.research import ResearchSpec
from backend.settings import Settings, load_settings
from backend.store import Store


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    """No real provider key or external asset writes in automated tests."""
    return replace(
        load_settings(),
        database_url="",
        data_dir=tmp_path,
        openai_key="test-not-a-real-key",
        blob_token="",
        invite_code="family-test-invite",
        owner_code="owner-test-invite",
        session_secret="test-only-session-secret",
        budget_usd=20,
        production=False,
        video_width=320,
        video_height=240,
        video_fps=2,
    )


@pytest.fixture
def store(settings: Settings) -> Store:
    """Each test gets an independent transactional repository."""
    return Store("", settings.data_dir)


@pytest.fixture
def user() -> User:
    """An ordinary member, distinct from the owner."""
    return User(id="test-member", name="Ari", owner=False)


@pytest.fixture
def spec() -> LessonSpec:
    """Schema-valid teaching fixture with visible animation, not a seed lesson."""
    return LessonSpec.model_validate(
        {
            "version": 1,
            "title": "Washing machine",
            "canonical": "washing-machine",
            "aliases": ["washer", "washing machine"],
            "family": "Generic front-loading washer",
            "question": "How does a washing machine work?",
            "summary": "Water, detergent and movement loosen dirt; rinsing and spinning remove it.",
            "big_idea": "The outer tub holds water while the perforated drum moves clothes.",
            "category": "Home",
            "accent": "#006d7c",
            "assumptions": ["A schematic test fixture, without real appliance specifications."],
            "sources": [
                {
                    "title": "Whirlpool washing machine overview",
                    "url": "https://www.whirlpool.com/blog/washers-and-dryers/how-does-a-washing-machine-work.html",
                    "supports": "The general order of washing, draining, rinsing and spinning.",
                }
            ],
            "parts": [
                {
                    "id": f"part-{i}",
                    "name": f"Fixture part {i}",
                    "description": "An explicit synthetic shape for renderer and API tests.",
                    "shape": shape,
                    "x": 180 + i * 38,
                    "y": 110 + i * 20,
                    "w": 50 if shape != "path" else 4,
                    "h": 50,
                    "color": "#d5e0e4",
                    "stroke": "#49636e",
                    "label": "Test" if shape == "text" else "",
                    "points": [[200, 100], [260, 120], [250, 160]],
                    "layer": i,
                    "motion": [{"stage": i % 3, "kind": kind, "amount": 90, "axis": "x"}],
                }
                for i, (shape, kind) in enumerate(
                    zip(
                        ["box", "ellipse", "ring", "path", "polygon", "text", "box", "ring"],
                        ["rotate", "translate", "pulse", "flow", "translate", "pulse", "translate", "rotate"],
                        strict=True,
                    )
                )
            ]
            + [
                {
                    "id": f"label-part-{i}",
                    "name": f"Part {i}",
                    "description": "Synthetic component label for pipeline contract tests.",
                    "shape": "text",
                    "x": 60 + i * 260,
                    "y": 35,
                    "w": 0,
                    "h": 32,
                    "color": "#17232d",
                    "stroke": "#49636e",
                    "label": f"Part {i}",
                    "points": [],
                    "layer": 30,
                    "motion": [],
                }
                for i in range(3)
            ],
            "stages": [
                {
                    "title": title,
                    "explanation": "A test stage explains a bounded causal mechanism.",
                    "narration": "This is synthetic narration for an automated video test.",
                    "duration": 5,
                    "parts": [f"part-{i}", "part-3"],
                    "cause": "A test action causes a visible change.",
                    "input_state": "Explicit synthetic input",
                    "output_state": "Explicit synthetic output",
                    "focus": f"part-{i}",
                    "source_indices": [0],
                }
                for i, title in enumerate(["Fill", "Wash", "Drain"])
            ],
            "questions": [
                {
                    "question": f"What does part {i} do?",
                    "answer": "This part has a defined role in the test mechanism.",
                    "stage": i,
                    "part": f"part-{i}",
                }
                for i in range(3)
            ],
            "prediction": "What happens if the water inlet is closed?",
            "prediction_answer": "The machine cannot admit fresh water through the closed inlet.",
        }
    )


@pytest.fixture
def seeded(store: Store, spec: LessonSpec) -> Store:
    """Insert only into this test's isolated database."""
    store.transaction(
        lambda db: db.lessons.update(
            {
                spec.canonical: {
                    "id": spec.canonical,
                    "spec": spec.model_dump(mode="json"),
                    "views": 0,
                    "created_at": 1,
                    "quality": "test-fixture",
                    "video": None,
                }
            }
        )
    )
    return store


@pytest.fixture
def ce_spec() -> LessonSpec:
    """Synthetic truncated pipeline fixture; never imported as a teaching artifact."""
    from backend.ac_concept import aircon_concept
    from backend.teaching_contracts import Change, Pose

    candidate = aircon_concept()
    candidate.canonical, candidate.title = "washing-machine", "Synthetic CE pipeline fixture"
    candidate.aliases = ["washer"]
    candidate.stages = candidate.stages[:3]
    assert candidate.teaching is not None
    candidate.teaching.renderer = "declarative"
    candidate.teaching.renderer_fingerprint = ""
    candidate.teaching.beats = candidate.teaching.beats[:3]
    for stage in candidate.stages:
        stage.duration = 5
    for question in candidate.questions:
        question.stage = min(2, question.stage)
    for part in candidate.parts:
        part.motion = [m for m in part.motion if m.stage < 3]
    for scenario in candidate.teaching.scenarios:
        scenario.beat = candidate.teaching.beats[-1].id
        scenario.context = "none"
        scenario.changes = []
    candidate.teaching.scenarios[1].changes = [
        Change(target="compress-piston", before=Pose(), after=Pose(x=-120))
    ]
    return LessonSpec.model_validate(candidate.model_dump())


@pytest.fixture
def evidence(ce_spec: LessonSpec) -> "ResearchSpec":
    """Explicitly synthetic evidence for phase tests, never presented as sourced research."""
    from backend.research import ResearchFact

    return ResearchSpec(
        family="Synthetic mechanism fixture",
        sources=[source.model_copy(deep=True) for source in ce_spec.sources],
        facts=[
            ResearchFact(
                statement="Synthetic evidence for a controlled test only.",
                source=ce_spec.sources[i % len(ce_spec.sources)].url,
                locator="Synthetic fixture section",
            )
            for i in range(3)
        ],
        limits=["Synthetic evidence is not a technical review."],
    )
