"""Explicit synthetic fixtures; these are never published as live AI output."""

from dataclasses import replace
from pathlib import Path

import pytest

from backend.contracts import LessonSpec
from backend.domain import User
from backend.native_publication import PreparedNative
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
        public_access=False,
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
        part.motion = []
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


@pytest.fixture
def native_prepared(ce_spec: LessonSpec, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> PreparedNative:
    """Synthetic native proof exercises contracts; it certifies no real artwork or lesson."""
    import hashlib
    import json

    from backend.native_contracts import NativeLessonSpec
    from backend.native_proof import NativeFrame, NativeProof, NativeViewport
    from backend.native_registry import canonical_digest
    from backend.settings import ROOT
    from backend.starters import digest_spec

    assert ce_spec.teaching is not None
    prediction, transfer = ce_spec.teaching.prediction, ce_spec.teaching.transfer
    components = [{"id": name, "name": "Synthetic " + name,
                   "description": "An explicit synthetic semantic component for native adapter tests.",
                   "label": name.capitalize()} for name in ("input", "working", "output")]
    claims = [claim.model_dump(mode="json") for claim in ce_spec.teaching.claims[:2]]
    claim_id, source_index = str(claims[0]["id"]), int(str(claims[0]["source"]))
    identity = {"id": "synthetic-native-1", "lessons": ["synthetic-native-core"], "sources": [{
        "path": "native/gpu-memory-r1.ts", "sha256": hashlib.sha256((ROOT / "native/gpu-memory-r1.ts").read_bytes()).hexdigest()}]}
    spec = NativeLessonSpec.model_validate({
        "version": 3, "spec_version": "native-studio-1", "title": "Synthetic native adapter fixture",
        "canonical": "synthetic-native-core", "aliases": ["synthetic native fixture"],
        "family": "Synthetic native protocol fixture", "question": "How does this synthetic native fixture work?",
        "summary": "A synthetic input changes through a labeled working component into a synthetic output.",
        "big_idea": "This is a protocol fixture, never an actual educational artifact.", "category": "Other", "accent": "#35645b",
        "assumptions": ["Entirely synthetic contract data; no actual technical or learner review is implied."],
        "sources": [s.model_dump(mode="json") for s in ce_spec.sources],
        "renderer": {"id": identity["id"], "fingerprint": canonical_digest(identity)}, "components": components,
        "stages": [{"id": name, "kind": kind, "start": i*5, "end": (i+1)*5, "still": i*5+2,
                    "title": "Synthetic " + name, "explanation": "An explicit synthetic causal statement for this adapter fixture.",
                    "narration": "An explicit synthetic narration cue for this adapter fixture.", "duration": 5,
                    "parts": ["input", "working", "output"], "cause": "The synthetic input causes the declared visible change.",
                    "input_state": "Synthetic input is supplied", "output_state": "Synthetic output is produced",
                    "focus": "working", "source_indices": [source_index], "claims": [claim_id]}
                   for i, (name, kind) in enumerate((("opening", "orientation"), ("working", "causal"), ("together", "recombine")))],
        "questions": [{"question": "What does the synthetic component do?", "answer": "This is an explicit synthetic answer used only in adapter tests.",
                       "stage": i, "part": "working"} for i in range(3)],
        "prediction": prediction.prompt, "prediction_answer": prediction.explanation,
        "teaching": {"goal": "Exercise real native data boundaries without pretending to establish teaching quality.",
                     "misconception": "A passing engineering fixture is actual scientific or learning evidence.",
                     "core": ["input", "working", "output"], "operation": "sequential",
                     "operation_note": "A synthetic sequence for tests, not a real machine or computation.",
                     "invariants": ["No real quality or release approval is implied."], "claims": claims,
                     "prediction": prediction.model_dump(mode="json"), "transfer": transfer.model_dump(mode="json"),
                     "teach_back": "Explain the synthetic input, change and output relationship.",
                     "teach_back_reasoning": ["Identify the input.", "Explain its output consequence."],
                     "scenarios": [{"id": value, "label": "Synthetic " + value, "kind": "qualitative", "controls": {"power": value},
                                    "cue_id": "working", "outcome": "Synthetic consequence " + value,
                                    "explanation": "An explicitly synthetic counterfactual for protocol tests.", "claims": [claim_id]}
                                   for value in ("on", "off")]},
        "controls": [{"key": "power", "label": "Synthetic power", "options": [{"value": value, "label": value} for value in ("on", "off")]}],
        "default_controls": {"power": "on"},
        "actions": [{"id": "observe", "label": "Observe the fixture", "start": 5, "end": 10, "still": 7, "controls": {}}],
    })
    registry = tmp_path / "native-registry.json"
    registry.write_text(json.dumps({"schema_version": "native-renderers-1", "renderers": [{
        **identity, "fingerprint": spec.renderer.fingerprint, "spec_sha256": {spec.canonical: digest_spec(spec)}}]}))
    monkeypatch.setattr("backend.native_registry.REGISTRY_FILE", registry)

    def frame(cue_id: str, time: float, x: int, scenario: str = "") -> NativeFrame:
        return NativeFrame(cue_id=cue_id, time=time, scenario_id=scenario,
                           controls={"power": scenario or "on"},
                           svg=f'<g><rect x="{x}" y="70" width="40" height="20"/><text x="20" y="30">Input</text><text x="100" y="30">Working</text><text x="200" y="30">Output</text></g>',
                           labels=[], viewport=NativeViewport(x=0, y=0, width=720, height=620),
                           caption="Synthetic labeled surroundings for an adapter fixture.",
                           alt="A synthetic input, working component and output with an explicit visible change.")

    proof = NativeProof(schema_version="native-proof-1", renderer_id=spec.renderer.id,
                        renderer_fingerprint=spec.renderer.fingerprint, spec_sha256=digest_spec(spec),
                        video_sha256=hashlib.sha256(b"Synthetic native media API bytes, not an actual video.").hexdigest(),
                        video_duration=15, fps=24, width=1280, height=866,
                        frames=[frame("opening", 2, 0), frame("working", 5.05, 10), frame("working", 7, 30),
                                frame("working", 9.95, 70), frame("together", 12, 90),
                                frame("working", 7, 30, "on"), frame("working", 7, 0, "off")])
    return PreparedNative(spec=spec, proof=proof, video="synthetic-native-fixture.mp4",
                          narration="Explicit synthetic narration; no provider call", replaces=[])
