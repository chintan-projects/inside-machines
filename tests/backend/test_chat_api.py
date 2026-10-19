"""Private conversation ownership and HTTP/session boundaries."""

import json
from dataclasses import replace

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.app import create_app, video_response
from backend.chat import Chats
from backend.domain import User
from backend.provider import receipt_context
from backend.settings import Settings
from backend.store import Store


async def answer(prompt: str, settings: Settings) -> str:
    """Explicit fake provider for isolation tests; no network or paid calls."""
    assert "QUESTION" in prompt and settings.openai_key == "test-not-a-real-key"
    receipt = receipt_context.get()
    assert receipt is not None
    receipt.models.append("test-provider")
    receipt.cost_usd = 0.003
    return json.dumps(
        {
            "answer": "The drum moves the clothes through the water.",
            "stage": 1,
            "part": "part-1",
            "source_indices": [0],
            "uncertain": False,
        }
    )


async def test_private_chat_and_idempotency(seeded: Store, settings: Settings, user: User) -> None:
    """Another member cannot read or append, even knowing a conversation id."""
    chats = Chats(seeded, settings, answer)
    chat = chats.create("washing-machine", user)
    other = User(id="second-person", name="Other", owner=False)
    with pytest.raises(HTTPException) as hidden:
        chats.get(chat.id, other)
    assert hidden.value.status_code == 404
    result = await chats.ask(chat.id, "Why does it turn?", "operation-1", user)
    assert len(result.messages) == 2
    again = await chats.ask(chat.id, "Why does it turn?", "operation-1", user)
    assert len(again.messages) == 2
    assert seeded.snapshot().spent == 0.003 and seeded.snapshot().reserved == 0
    assert "Why does it turn?" not in json.dumps(seeded.snapshot().events)
    assert seeded.snapshot().lessons["washing-machine"]["quality"] == "test-fixture"


async def test_chat_failure_retains_unknown_cost(seeded: Store, settings: Settings, user: User) -> None:
    """A request that times out may still be billable; no zero-cost fiction."""

    async def timeout(prompt: str, config: Settings) -> str:
        raise TimeoutError("Synthetic ambiguous timeout")

    chats = Chats(seeded, settings, timeout)
    chat = chats.create("washing-machine", user)
    with pytest.raises(HTTPException) as failure:
        await chats.ask(chat.id, "Why does it turn?", "operation-2", user)
    assert failure.value.status_code == 502
    assert seeded.snapshot().spent == settings.chat_reserve
    assert seeded.snapshot().reserved == 0
    assert not chats.get(chat.id, user).messages
    with pytest.raises(HTTPException) as duplicate:
        await chats.ask(chat.id, "Why does it turn?", "operation-2", user)
    assert duplicate.value.status_code == 409


async def test_chat_rejects_invalid_visual_actions(seeded: Store, settings: Settings, user: User) -> None:
    """A fabricated part cannot become an executable UI action."""

    async def invalid(prompt: str, config: Settings) -> str:
        raw = json.loads(await answer(prompt, config))
        raw["part"] = "invented-part"
        return json.dumps(raw)

    chats = Chats(seeded, settings, invalid)
    chat = chats.create("washing-machine", user)
    with pytest.raises(HTTPException):
        await chats.ask(chat.id, "Why does it turn?", "operation-3", user)
    assert seeded.snapshot().spent == 0.003
    assert not chats.get(chat.id, user).messages


def test_http_login_csrf_feedback_and_owner_report(seeded: Store, settings: Settings) -> None:
    """Cookie sessions gate all private APIs; the report never includes chat text."""
    app = create_app(settings)
    with TestClient(app) as client:
        assert client.get("/api/v1/lessons").status_code == 401
        assert (
            client.post(
                "/api/v1/auth/login",
                json={"name": "Ari", "code": settings.invite_code},
                headers={"Origin": "https://evil.example"},
            ).status_code
            == 403
        )
        response = client.post("/api/v1/auth/login", json={"name": "Ari", "code": settings.invite_code})
        assert response.status_code == 200
        assert "HttpOnly" in response.headers["set-cookie"]
        assert client.get("/api/v1/auth/me").json()["name"] == "Ari"
        assert len(client.get("/api/v1/lessons").json()) == 1
        lesson = client.get("/api/v1/lessons/washing-machine")
        assert lesson.status_code == 200 and lesson.headers["cache-control"] == "private, no-store"
        assert (
            client.post("/api/v1/lessons/washing-machine/feedback", json={"value": "up"}).status_code == 200
        )
        assert client.get("/api/v1/owner/report").status_code == 403
        request = client.post("/api/v1/requests", json={"question": "washer", "scope": "general"}).json()
        assert request["kind"] == "lesson"
        specific = client.post("/api/v1/requests", json={"question": "my washer", "scope": "specific"}).json()
        assert specific["kind"] == "specific"
        assert client.get("/api/v1/lessons/washing-machine/captions").text.startswith("WEBVTT")
        assert client.post("/api/v1/auth/logout").status_code == 200
        assert client.get("/api/v1/auth/me").status_code == 401
        client.post("/api/v1/auth/login", json={"name": "Owner", "code": settings.owner_code})
        report = client.get("/api/v1/owner/report").json()
        assert report["lesson_count"] == 1 and "chats" not in report


def test_production_requires_durable_setup(settings: Settings) -> None:
    """An ephemeral SQLite deployment must never claim production readiness."""
    with pytest.raises(RuntimeError, match="durable database"):
        create_app(replace(settings, production=True))


@pytest.mark.parametrize(
    ("header", "status", "content"),
    [
        (None, 200, b"0123456789"),
        ("bytes=2-5", 206, b"2345"),
        ("bytes=-3", 206, b"789"),
        ("bytes=7-", 206, b"789"),
        ("bytes=20-", 416, b""),
        ("bytes=7-2", 416, b""),
        ("invalid", 416, b""),
        ("bytes=-", 416, b""),
    ],
)
def test_mobile_video_ranges(header: str | None, status: int, content: bytes) -> None:
    """iOS and Android seek with byte ranges rather than restarting downloads."""
    result = video_response(b"0123456789", header)
    assert result.status_code == status and bytes(result.body) == content
