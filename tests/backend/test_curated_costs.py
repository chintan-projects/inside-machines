"""Cost accounting is attributed once and never substitutes assumptions for bills."""

from dataclasses import replace
from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.ac_concept import aircon_concept
from backend.app import create_app
from backend.concept_publication import authored_lessons
from backend.contracts import LessonSpec, canonicalize
from backend.curated.catalog import SYSTEMS
from backend.curated_costs import curated_cost_report
from backend.domain import User
from backend.settings import Settings
from backend.store import Database

OWNER = User(id="owner", name="Synthetic owner", owner=True)


def test_twenty_scopes_do_not_invent_a_generation_price(settings: Settings, user: User) -> None:
    """An empty ledger is unmeasured; the reserve is never called an expected cost."""
    with pytest.raises(HTTPException) as denied:
        curated_cost_report(Database(), settings, user)
    assert denied.value.status_code == 403
    report = curated_cost_report(Database(), settings, OWNER)
    assert len(report.systems) == 20 and len({row.system_id for row in report.systems}) == 20
    assert all(row.expected_generation_usd is None and not row.revisions for row in report.systems)
    assert all(row.owner_draft_reservation_usd == settings.generation_reserve for row in report.systems)
    assert len({row.optional_hosted_speech_estimate_usd for row in report.systems}) > 1
    assert report.ledger_total.operations == 0 and report.stored_spent_usd == 0


def test_speech_fallback_counts_reunion_and_preserved_longer_source(settings: Settings) -> None:
    """The real complete authored script is longer than the planning steps alone."""
    sources = {canonicalize(spec.title): spec for spec, _ in authored_lessons()}
    report = curated_cost_report(Database(), settings, OWNER)
    assert all(row.optional_hosted_speech_estimate_usd is not None for row in report.systems)
    for key in ("refrigerator", "air-conditioner"):
        row = next(row for row in report.systems if row.system_id == key)
        spec = sources[key]
        words = sum(len(stage.narration.split()) for stage in spec.stages)
        assert words > sum(len(step.narration.split()) for step in SYSTEMS[key].steps)
        assert row.speech_script_words == words
        assert row.speech_estimate_lesson_id == spec.canonical and row.speech_estimate_basis == "authored-source"
        assert row.optional_hosted_speech_estimate_usd == pytest.approx(words / 130 * settings.speech_rate)
    assert sources["refrigerator"].stages[-1].title == "Put the whole system together"


def test_speech_estimate_prefers_complete_current_stored_narration(settings: Settings, ce_spec: LessonSpec) -> None:
    """A newer archived short script cannot underprice the active longer revision."""
    active = ce_spec.model_copy(deep=True)
    active.canonical = "air-conditioner-legacy-active"
    active.title = "Synthetic air conditioner fixture"
    active.question = "How does a generic air conditioner work?"
    active.aliases = ["air conditioner"]
    active.stages[0].narration += " Synthetic expanded narration for a longer served clip."
    archived = active.model_copy(deep=True)
    archived.canonical = "air-conditioner-newer-archived"
    for stage in archived.stages:
        stage.narration = "Synthetic short narration."
    depth = archived.model_copy(deep=True)
    depth.canonical, depth.title = "synthetic-depth-leaf", "Synthetic independent depth question"
    depth.question, depth.aliases = "Why does this relationship change the result?", ["synthetic independent depth"]
    db = Database(lessons={
        active.canonical: {"id": active.canonical, "spec": active.model_dump(mode="json"), "created_at": 1},
        archived.canonical: {"id": archived.canonical, "spec": archived.model_dump(mode="json"), "created_at": 100, "archived": True},
        depth.canonical: {"id": depth.canonical, "spec": depth.model_dump(mode="json"), "created_at": 200, "depth_parent": active.canonical},
    }, jobs={"depth": {"node_parent": active.canonical, "status": "failed"}}, ledger={
        "historical": {"charged_usd": .13, "models": ["actual-model"]},
        "lesson:depth:author": {"charged_usd": .2, "models": ["actual-model"]},
    }, spent=.33)
    before = db.model_dump(mode="json")
    result = curated_cost_report(db, settings, OWNER)
    row = next(row for row in result.systems if row.system_id == "air-conditioner")
    words = sum(len(stage.narration.split()) for stage in active.stages)
    assert row.speech_estimate_basis == "active-lesson" and row.speech_estimate_lesson_id == active.canonical
    assert row.speech_script_words == words
    assert row.optional_hosted_speech_estimate_usd == pytest.approx(words / 130 * settings.speech_rate)
    assert row.build.recorded_usd == .2 and len(row.revisions) == 3
    assert result.ledger_total.recorded_usd == .33 and result.spent_ledger_difference_usd == 0
    assert db.model_dump(mode="json") == before


def test_costs_reconcile_failures_chats_estimates_and_unknown_billing(settings: Settings) -> None:
    """Old jobs, failed operations and private chats count once, without their text."""
    spec = aircon_concept()
    lesson = {"id": spec.canonical, "spec": spec.model_dump(mode="json"), "narration": "Test voice", "cost_usd": 99}
    db = Database(
        lessons={spec.canonical: lesson},
        jobs={
            "current": {"lesson_id": spec.canonical, "status": "complete", "reservation": 0},
            "prior": {"question": "How does an air conditioner work?", "status": "failed"},
            "queued": {"revision_of": spec.canonical, "status": "queued", "reservation": 1.1},
            "unknown": {"question": "Unregistered chemical plant", "status": "queued", "reservation": 0.4},
        },
        chats={"private-id": {"lesson_id": spec.canonical, "messages": [{"text": "PRIVATE CHAT"}], "user_id": "PRIVATE MEMBER"}},
        ledger={
            "lesson:prior:research": {"charged_usd": .05, "models": ["actual-model"], "input_tokens": 500, "output_tokens": 200},
            "lesson:current:author": {"charged_usd": .12, "models": ["actual-model"], "input_tokens": 1000, "output_tokens": 400, "prompt": "PRIVATE PROMPT"},
            "lesson:current:voice-0": {"charged_usd": .01, "models": ["voice"], "speech_estimated": True},
            "lesson:prior:review": {"charged_usd": .65, "models": [], "uncertain": True},
            "chat:private-id:turn-1": {"charged_usd": .03, "models": ["actual-model"], "input_tokens": 150, "output_tokens": 75},
            "old-unmatched": {"charged_usd": .04, "models": ["legacy"]},
        },
        spent=1.01, reserved=1.5,
    )
    result = curated_cost_report(db, settings, OWNER)
    aircon = next(row for row in result.systems if row.system_id == "air-conditioner")
    assert aircon.build.recorded_usd == pytest.approx(.83)
    assert aircon.build.receipt_based_usd == pytest.approx(.17)
    assert aircon.build.estimated_usd == pytest.approx(.01)
    assert aircon.build.uncertain_usd == pytest.approx(.65)
    assert aircon.build.input_tokens == 1500 and aircon.build.output_tokens == 600
    assert aircon.chat.recorded_usd == pytest.approx(.03)
    assert aircon.revisions[0].build.recorded_usd == pytest.approx(.13)
    assert aircon.revisions[0].declared_paid_calls is None  # cost_usd=99 is not an operation receipt.
    assert result.attributed.recorded_usd == pytest.approx(.86)
    assert result.unallocated.recorded_usd == pytest.approx(.04)
    assert result.ledger_total.recorded_usd == pytest.approx(.9)
    assert result.spent_ledger_difference_usd == pytest.approx(.11)
    assert result.unallocated_reserved_usd == pytest.approx(.4)
    assert "PRIVATE" not in result.model_dump_json() and "private-id" not in result.model_dump_json()


def test_local_zero_requires_provenance_and_does_not_hide_receipts(settings: Settings) -> None:
    """A local declaration is shown separately, never used to erase a paid receipt."""
    spec = aircon_concept()
    db = Database(
        lessons={spec.canonical: {
            "id": spec.canonical, "spec": spec.model_dump(mode="json"), "curated_system_id": "air-conditioner",
            "production_cost": {"mode": "local-authored", "paid_calls": 0},
        }},
        jobs={"paid": {"lesson_id": spec.canonical, "status": "failed"}},
        ledger={"lesson:paid:author": {"charged_usd": .25, "models": ["actual-model"]}},
        spent=.25,
    )
    report = curated_cost_report(db, settings, OWNER)
    row = next(row for row in report.systems if row.system_id == "air-conditioner")
    assert row.revisions[0].declared_paid_calls == 0
    assert row.build.recorded_usd == .25
    assert report.spent_ledger_difference_usd == 0


def test_costs_endpoint_is_owner_only_and_has_all_scopes(settings: Settings, tmp_path: Path) -> None:
    """No model call or raw private data is involved in this read-only projection."""
    config = replace(settings, data_dir=tmp_path)
    with TestClient(create_app(config)) as client:
        assert client.get("/api/v1/owner/costs").status_code == 401
        client.post("/api/v1/auth/login", json={"name": "Family", "code": config.invite_code})
        assert client.get("/api/v1/owner/costs").status_code == 403
        client.post("/api/v1/auth/login", json={"name": "Owner", "code": config.owner_code})
        response = client.get("/api/v1/owner/costs")
        assert response.status_code == 200 and len(response.json()["systems"]) == 20
