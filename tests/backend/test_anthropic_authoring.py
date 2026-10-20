"""Production Claude contracts use intercepted HTTP, never real credentials."""

import json
from dataclasses import replace

import httpx
import pytest
from _shared.services.model_gateway import ModelBackendError, Request

from backend.anthropic_authoring import ClaudeAuthoringBackend
from backend.assets import Assets
from backend.author_transport import author_schema
from backend.domain import Domain, User
from backend.pipeline import Pipeline
from backend.provider import UsageReceipt, configure_gateway, model_speech, model_text, receipt_context
from backend.provider_schema import anthropic_schema
from backend.settings import Settings
from backend.store import Store


def claude(settings: Settings) -> Settings:
    """Only this explicit test route has an invented Anthropic key."""
    return replace(settings, authoring_provider="anthropic", anthropic_key="synthetic-claude-key")


def stream(mode: str = "success") -> str:
    """Synthetic message events include exact identity and both cache categories."""
    events: list[dict[str, object]] = [
        {"type": "message_start", "message": {
            "model": "claude-sonnet-5-5", "usage": {
                "input_tokens": 100, "cache_creation_input_tokens": 20, "cache_read_input_tokens": 30,
            },
        }},
        {"type": "content_block_start", "content_block": {"type": "text"}},
        {"type": "content_block_delta", "delta": {"type": "text_delta", "text": '{"value":"synthetic"}'}},
        {"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 50}},
        {"type": "message_stop"},
    ]
    if mode in ("refusal", "max_tokens"):
        events[-2]["delta"] = {"stop_reason": mode}
    if mode == "missing-input":
        events[0]["message"] = {"model": "claude-sonnet-5-5", "usage": {}}
    if mode == "missing-output":
        events[-2].pop("usage")
    if mode == "truncated":
        events.pop()
    if mode == "wrong-model":
        events[0]["message"] = {"model": "unpriced-model", "usage": {"input_tokens": 100}}
    if mode in ("bad-json", "non-object", "empty"):
        events[2]["delta"] = {
            "type": "text_delta", "text": {"bad-json": "{INVALID", "non-object": "[]", "empty": ""}[mode],
        }
    if mode == "tool":
        events[1]["content_block"] = {"type": "tool_use"}
    if mode == "repeated-start":
        events.insert(1, events[0])
    return "\n\n".join("data: " + json.dumps(event) for event in events) + "\n\n"


@pytest.mark.parametrize("mode", [
    "success", "refusal", "max_tokens", "missing-input", "missing-output", "truncated",
    "wrong-model", "bad-json", "non-object", "empty", "tool", "repeated-start", "malformed", "quota", "timeout",
])
def test_structured_stream_failure_and_usage(
    settings: Settings, monkeypatch: pytest.MonkeyPatch, mode: str,
) -> None:
    """No refusal, partial stream or protocol failure turns into a fake success."""
    config = claude(settings)
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        body = json.loads(request.content)
        assert body["model"] == config.anthropic_model and body["stream"]
        assert body["thinking"] == {"type": "between_tools"}
        assert body["output_config"]["format"]["type"] == "json_schema"
        assert body["system"] == "Synthetic system"
        assert body["messages"] == [{"role": "user", "content": "Synthetic question"}]
        assert "tools" not in body and "cache_control" not in json.dumps(body)
        assert request.headers["x-api-key"] == "synthetic-claude-key"
        if mode == "quota":
            return httpx.Response(429, text="PRIVATE BODY")
        if mode == "timeout":
            raise httpx.ReadTimeout("PRIVATE BODY", request=request)
        return httpx.Response(200, text="data: INVALID\n\n" if mode == "malformed" else stream(mode))

    original = httpx.Client
    monkeypatch.setattr(
        "backend.anthropic_transport.httpx.Client",
        lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs),
    )
    receipt = UsageReceipt()
    token = receipt_context.set(receipt)
    request = Request(None, (
        {"role": "system", "content": "Synthetic system"},
        {"role": "user", "content": "Synthetic question"},
    ), json.dumps({"type": "object", "properties": {"value": {"type": "string"}}}), 100, None)
    try:
        if mode == "success":
            assert ClaudeAuthoringBackend(config.anthropic_model, config).run(request).text == '{"value":"synthetic"}'
            assert receipt.input_tokens == 150 and receipt.output_tokens == 50
            assert receipt.cost_usd == pytest.approx((100 * 2 + 20 * 4 + 30 * .1 + 50 * 10) / 1e6)
            assert receipt.billing_complete and not receipt.model_identity_estimated
        else:
            with pytest.raises(ModelBackendError) as error:
                ClaudeAuthoringBackend(config.anthropic_model, config).run(request)
            assert "PRIVATE BODY" not in str(error.value)
            if mode in ("refusal", "max_tokens", "bad-json", "non-object", "empty"):
                assert receipt.billing_complete and receipt.cost_usd > 0
            if mode == "truncated":
                assert receipt.models and receipt.billing_complete is False
    finally:
        receipt_context.reset(token)
    assert len(calls) == 1


def test_schema_translation_preserves_original_constraints() -> None:
    """Only the transport subset changes; all original domain bounds survive."""
    original = author_schema()
    snapshot = json.dumps(original)
    translated = anthropic_schema(original)
    assert json.dumps(original) == snapshot
    properties = original["properties"]
    assert isinstance(properties, dict)
    assert translated["required"] == list(properties)
    assert translated["additionalProperties"] is False
    assert '"maxLength":' not in json.dumps(translated)
    assert "Domain constraints:" in json.dumps(translated)
    with pytest.raises(ValueError, match="local"):
        anthropic_schema({"$ref": "https://example.com/untrusted"})
    with pytest.raises(ValueError, match="closed"):
        anthropic_schema({"type": "object", "additionalProperties": {"type": "string"}})


def test_preflight_and_readiness_fail_closed(settings: Settings) -> None:
    """A registry name, missing key, unsupported schema or unpriced model cannot dispatch."""
    config = claude(settings)
    adapter = ClaudeAuthoringBackend(config.anthropic_model, config)
    for request in (
        Request("x", None, None, 10, None),
        Request("x", None, "INVALID", 10, None),
        Request("x", None, "[]", 10, None),
        Request("x", None, '{"type":"object"}', config.max_output_tokens + 1, None),
        Request("x" * config.anthropic_max_input_bytes, None, '{"type":"object"}', 10, None),
        Request("x", None, '{"type":"object"}', 10, ("a", "b")),
    ):
        with pytest.raises(ModelBackendError):
            adapter.request_body(request)
    assert not replace(config, anthropic_key="").generation_enabled
    assert not replace(config, openai_key="").generation_enabled
    assert config.generation_enabled
    with pytest.raises(ValueError, match="pricing"):
        replace(config, anthropic_model="claude-unpriced")
    with pytest.raises(ValueError, match="prices"):
        replace(config, anthropic_input_rate=1)
    with pytest.raises(ValueError, match="allowance"):
        replace(config, anthropic_output_rate=1000)
    with pytest.raises(ValueError, match="provider"):
        replace(settings, authoring_provider="client-supplied")
    with pytest.raises(ValueError, match="bounds"):
        replace(config, anthropic_max_input_bytes=100001)
    with pytest.raises(ModelBackendError, match="scoped"):
        adapter.run(Request("x", None, '{"type":"object"}', 10, None))
    token = receipt_context.set(UsageReceipt())
    try:
        with pytest.raises(ModelBackendError, match="server key"):
            ClaudeAuthoringBackend(config.anthropic_model, replace(config, anthropic_key="")).run(
                Request("x", None, '{"type":"object"}', 10, None)
            )
    finally:
        receipt_context.reset(token)


async def test_explicit_gateway_task_isolation(settings: Settings, monkeypatch: pytest.MonkeyPatch) -> None:
    """Only authoring reaches Anthropic; the retrieval checkpoint still uses OpenAI."""
    observed: list[tuple[str, dict[str, object]]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append((request.url.host, json.loads(request.content)))
        if request.url.host == "api.anthropic.com":
            return httpx.Response(200, text=stream())
        if request.url.path.endswith("/audio/speech"):
            return httpx.Response(200, content=b"synthetic-test-audio")
        return httpx.Response(200, json={
            "status": "completed", "model": settings.model,
            "usage": {"input_tokens": 100, "output_tokens": 50},
            "output": [{"type": "message", "content": [{"type": "output_text", "text": '{"value":"openai"}'}]}],
        })

    original = httpx.Client
    monkeypatch.setattr(
        "backend.anthropic_transport.httpx.Client",
        lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs),
    )
    config = claude(settings)
    configure_gateway(config)
    for task in ("authoring", "research", "review"):
        token = receipt_context.set(UsageReceipt())
        try:
            await model_text("RESEARCH_MACHINE\nSynthetic" if task == "research" else "Synthetic", config,
                             schema={"type": "object"}, task=task)
        finally:
            receipt_context.reset(token)
    token = receipt_context.set(UsageReceipt())
    try:
        await model_text("Synthetic", config, schema={"type": "object"}, chat=True)
        assert await model_speech("Synthetic test narration.", config) == b"synthetic-test-audio"
    finally:
        receipt_context.reset(token)
    assert [host for host, _ in observed] == ["api.anthropic.com", *["api.openai.com"]*4]
    assert observed[1][1]["tools"] == [{"type": "web_search"}]
    assert "tools" not in observed[2][1]
    assert "tools" not in observed[3][1]
    assert observed[4][1]["model"] == settings.speech_model


async def test_partial_stream_retains_full_allowance_without_retry(
    store: Store, settings: Settings, user: User,
) -> None:
    """Knowing a model identity does not mean final stream billing is known."""
    config = claude(settings)

    async def enqueue(job_id: str, phase: str) -> None:
        return None

    pipeline = Pipeline(store, config, Assets(config), enqueue)
    job_id = str(Domain(store, config).request("Synthetic machine", user)["job_id"])
    job = pipeline._claim(job_id)
    assert job is not None

    async def interrupted() -> str:
        receipt = receipt_context.get()
        assert receipt is not None
        receipt.models.append(config.anthropic_model)
        receipt.input_tokens, receipt.cost_usd, receipt.billing_complete = 100, .0002, False
        raise ModelBackendError("Synthetic interrupted stream")

    with pytest.raises(ModelBackendError):
        await pipeline._paid(job, "author", interrupted)
    state = store.snapshot()
    receipt = state.ledger[f"lesson:{job_id}:author"]
    assert receipt["uncertain"] and receipt["charged_usd"] == config.text_phase_reserve
    assert receipt["models"] == [config.anthropic_model]
    assert state.spent == config.text_phase_reserve
