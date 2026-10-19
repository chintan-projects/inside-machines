"""Validate the actual hosted gateway adapter against intercepted HTTP requests."""

import json

import httpx
import pytest
from _shared.services.model_gateway import ModelBackendError, Request

from backend.provider import (
    HostedBackend,
    UsageReceipt,
    configure_gateway,
    model_speech,
    model_text,
    receipt_context,
)
from backend.settings import Settings


async def test_gateway_structured_research_and_speech(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    """All model access goes through the shared gateway and returns provider usage."""
    observed: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        observed.append(body)
        assert request.headers["authorization"] == "Bearer test-not-a-real-key"
        if request.url.path.endswith("speech"):
            return httpx.Response(200, content=b"synthetic-test-audio")
        return httpx.Response(
            200,
            json={
                "status": "completed",
                "usage": {"input_tokens": 100, "output_tokens": 50},
                "output": [
                    {"type": "web_search_call"},
                    {"type": "message", "content": [{"type": "output_text", "text": '{"value":"test"}'}]},
                ],
            },
        )

    original = httpx.Client

    def client(*, timeout: httpx.Timeout) -> httpx.Client:
        return original(transport=httpx.MockTransport(handler), timeout=timeout)

    monkeypatch.setattr("backend.provider.httpx.Client", client)
    configure_gateway(settings)
    receipt = UsageReceipt()
    token = receipt_context.set(receipt)
    try:
        result = await model_text("RESEARCH_MACHINE\nTest only", settings, schema={"type": "object"})
        assert result == '{"value":"test"}'
        assert await model_speech("A synthetic test sentence.", settings) == b"synthetic-test-audio"
    finally:
        receipt_context.reset(token)
    assert observed[0]["max_tool_calls"] == 3
    assert observed[0]["store"] is False
    assert observed[0]["reasoning"] == {"effort": settings.reasoning_effort}
    assert observed[0]["text"] == {
        "format": {
            "type": "json_schema",
            "name": "lesson_response",
            "strict": True,
            "schema": {"type": "object"},
        }
    }
    assert receipt.input_tokens == 100 and receipt.output_tokens == 50 and receipt.search_calls == 1
    assert receipt.cost_usd > 0.01 and receipt.speech_characters > 0
    assert receipt.models == [settings.model, settings.speech_model]


@pytest.mark.parametrize("mode", ["rejected", "timeout", "incomplete", "no-output"])
def test_provider_failures_never_become_fake_answers(
    settings: Settings, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    """Refusals, partial responses and transport failures are explicit errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        if mode == "rejected":
            return httpx.Response(429, json={"error": "synthetic quota"})
        if mode == "timeout":
            raise httpx.ReadTimeout("synthetic timeout", request=request)
        return httpx.Response(
            200,
            json={
                "status": "incomplete" if mode == "incomplete" else "completed",
                "usage": {"input_tokens": 100, "output_tokens": 20},
                "output": [],
            },
        )

    original = httpx.Client

    def client(*, timeout: httpx.Timeout) -> httpx.Client:
        return original(transport=httpx.MockTransport(handler), timeout=timeout)

    monkeypatch.setattr("backend.provider.httpx.Client", client)
    receipt = UsageReceipt()
    token = receipt_context.set(receipt)
    try:
        with pytest.raises(ModelBackendError):
            HostedBackend(settings.model, settings).run(
                Request(prompt="Test", messages=None, grammar=None, max_tokens=5, label_tokens=None)
            )
    finally:
        receipt_context.reset(token)
    assert bool(receipt.models) == (mode in ("incomplete", "no-output"))


def test_provider_requires_receipt(settings: Settings) -> None:
    """No caller can bypass accounting by invoking the backend directly."""
    with pytest.raises(ModelBackendError, match="usage receipt"):
        HostedBackend(settings.model, settings).run(
            Request(prompt="Test", messages=None, grammar=None, max_tokens=5, label_tokens=None)
        )


def test_lesson_schema_translation_preserves_domain_url_validation() -> None:
    """Provider schema accepts URL strings; domain boundary still rejects unsafe URLs."""
    from pydantic import ValidationError

    from backend.contracts import LessonSpec, Source
    from backend.provider_schema import openai_schema

    schema = LessonSpec.model_json_schema()
    translated = openai_schema(schema)
    original_json = json.dumps(schema)
    assert '"format": "uri"' in original_json
    assert '"format": "uri"' not in json.dumps(translated)
    assert json.dumps(schema) == original_json
    assert translated["additionalProperties"] is False
    assert translated["required"] == schema["required"]
    with pytest.raises(ValidationError):
        Source.model_validate(
            {
                "title": "Invalid source",
                "url": "javascript:alert(1)",
                "supports": "A deliberately invalid source URL",
            }
        )
