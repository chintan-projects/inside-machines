"""Claude trial contracts intercept all HTTP; no automated test uses a paid key."""

import json
from pathlib import Path

import httpx
import pytest
from _shared.services.model_gateway import ModelBackendError, ModelResult, Request

from backend import claude_trial_run as runner
from backend.anthropic_trial import ClaudeReceipt, ClaudeTrialBackend, ClaudeTrialConfig
from backend.provider import receipt_context
from backend.store import Store


def config() -> ClaudeTrialConfig:
    """Read the trusted trial's exact declared limits/pricing."""
    return ClaudeTrialConfig.model_validate_json((runner.TRIAL / "config.json").read_text())


def test_gpu_trial_reuses_provider_but_isolates_concept_guidance() -> None:
    """The second concept cannot inherit the vacuum's causal rules or private output."""
    prompt = runner.trial_prompt(runner.GPU_TRIAL / "request-art-first.md")
    assert "GPU: many little jobs" in prompt
    assert "window.createGpuArt" in prompt
    assert "Create ONE complete standalone HTML page" not in prompt
    assert "clean-air BAGGED" not in prompt
    assert ".env.local" not in prompt and "sk-ant-" not in prompt


def response_events(mode: str) -> str:
    """A minimal synthetic SSE conversation with explicitly fake model text."""
    events: list[dict[str, object]] = [
        {
            "type": "message_start",
            "message": {
                "model": "claude-opus-5-5",
                "usage": {
                    "input_tokens": 100,
                    "cache_creation_input_tokens": 20,
                    "cache_read_input_tokens": 30,
                },
            },
        },
        {"type": "content_block_start", "content_block": {"type": "text"}},
        {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "synthetic answer"}},
        {"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 50}},
        {"type": "message_stop"},
    ]
    if mode == "incomplete":
        events[-2]["delta"] = {"stop_reason": "max_tokens"}
    elif mode == "refused":
        events[-2]["delta"] = {"stop_reason": "refusal"}
    elif mode == "missing-usage":
        events[-2].pop("usage")
    elif mode == "wrong-model":
        events[0]["message"] = {"model": "unpriced-model", "usage": {"input_tokens": 100}}
    elif mode == "truncated":
        events.pop()
    elif mode == "empty":
        events[2]["delta"] = {"type": "text_delta", "text": ""}
    elif mode == "unsupported":
        events[1]["content_block"] = {"type": "tool_use"}
    elif mode == "missing-input":
        events[0]["message"] = {"model": "claude-opus-5-5", "usage": {}}
    elif mode == "invalid-usage":
        events[-2]["usage"] = {"output_tokens": -1}
    return "\n\n".join("data: " + json.dumps(event) for event in events) + "\n\n"


@pytest.mark.parametrize(
    "mode",
    [
        "success",
        "incomplete",
        "refused",
        "missing-usage",
        "wrong-model",
        "truncated",
        "malformed",
        "timeout",
        "quota",
        "empty",
        "unsupported",
        "missing-input",
        "invalid-usage",
    ],
)
def test_stream_and_usage_contract(mode: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Only a complete accounted response succeeds; one call and sanitized failures."""
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        body = json.loads(request.content)
        assert body["stream"] and body["max_tokens"] == 100
        assert body["system"] == "Synthetic system"
        assert body["messages"] == [{"role": "user", "content": "Synthetic test"}]
        assert "tools" not in body
        assert request.headers["x-api-key"] == "test-key"
        assert request.extensions["timeout"]["read"] == config().timeout_seconds
        if mode == "timeout":
            raise httpx.ReadTimeout("PRIVATE RAW BODY", request=request)
        if mode == "quota":
            return httpx.Response(429, text="PRIVATE RAW BODY")
        content = "data: INVALID\n\n" if mode == "malformed" else response_events(mode)
        return httpx.Response(200, text=content, headers={"request-id": "synthetic-request"})

    original = httpx.Client
    monkeypatch.setattr(
        "backend.anthropic_trial.httpx.Client",
        lambda **kw: original(transport=httpx.MockTransport(handler), **kw),
    )
    receipt = ClaudeReceipt()
    token = receipt_context.set(receipt)
    request = Request(
        prompt=None,
        messages=(
            {"role": "system", "content": "Synthetic system"},
            {"role": "user", "content": "Synthetic test"},
        ),
        grammar=None,
        max_tokens=100,
        label_tokens=None,
    )
    try:
        adapter = ClaudeTrialBackend(config().model, "test-key", config())
        if mode == "success":
            assert adapter.run(request).text == "synthetic answer"
            assert receipt.input_tokens == 150 and receipt.output_tokens == 50
            assert receipt.cache_read_tokens == 30 and receipt.cache_write_tokens == 20
            assert receipt.cost_usd == pytest.approx((100 * 4 + 20 * 8 + 30 * 0.2 + 50 * 20) / 1e6)
            assert receipt.provider_request_id == "synthetic-request"
        else:
            with pytest.raises(ModelBackendError) as error:
                adapter.run(request)
            assert "PRIVATE RAW BODY" not in str(error.value)
            if mode in ("incomplete", "refused", "empty"):
                assert receipt.billing_complete
    finally:
        receipt_context.reset(token)
    assert len(calls) == 1


def test_preflight_rejects_unsupported_routes_and_bounds() -> None:
    """Structured output is explicitly unsupported; an entry alone is not production ready."""
    adapter = ClaudeTrialBackend(config().model, "test-key", config())
    for request in (
        Request("x", None, "{}", 10, None),
        Request("x", None, None, 10, ("yes", "no")),
        Request("x", None, None, 32001, None),
        Request("x" * 200000, None, None, 10, None),
    ):
        with pytest.raises(ModelBackendError):
            adapter.request_body(request)
    with pytest.raises(ValueError, match="pricing"):
        ClaudeTrialBackend("unpriced", "test-key", config())


@pytest.mark.parametrize("failure", [False, True])
async def test_trial_checkpoint_and_uncertain_settlement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: bool
) -> None:
    """Repeating a dispatched operation cannot spend again, including after ambiguous failure."""
    calls = 0

    async def invoke(**kwargs: object) -> ModelResult:
        nonlocal calls
        calls += 1
        receipt = receipt_context.get()
        assert isinstance(receipt, ClaudeReceipt)
        if failure:
            raise ModelBackendError("Synthetic uncertain timeout")
        receipt.models.append(config().model)
        receipt.cost_usd = 0.01
        return ModelResult("synthetic artifact", config().model, 10)

    monkeypatch.setattr(runner, "PRIVATE", tmp_path)
    monkeypatch.setattr(runner, "trial_prompt", lambda path: "Synthetic prompt")
    monkeypatch.setattr(runner, "get_env", lambda *args: "test-key")
    monkeypatch.setattr(runner, "invoke_model", invoke)
    if failure:
        with pytest.raises(ModelBackendError):
            await runner.run_trial("test-operation", Path("unused"))
        with pytest.raises(ValueError, match="already dispatched"):
            await runner.run_trial("test-operation", Path("unused"))
    else:
        await runner.run_trial("test-operation", Path("unused"))
        await runner.run_trial("test-operation", Path("unused"))
    state = Store("", tmp_path).snapshot()
    assert calls == 1 and state.reserved == 0
    assert state.spent == pytest.approx(config().allowance() if failure else 0.01)
    assert state.ledger["test-operation"]["uncertain"] is failure


async def test_actual_gateway_preserves_scoped_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Exercise the real thread boundary, registry, adapter and ledger as one local flow."""
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["x-api-key"] == "synthetic-local-key"
        calls.append(str(request.url))
        return httpx.Response(200, text=response_events("success"))

    original = httpx.Client
    monkeypatch.setattr(
        "backend.anthropic_trial.httpx.Client",
        lambda **kw: original(transport=httpx.MockTransport(handler), **kw),
    )
    monkeypatch.setattr(runner, "PRIVATE", tmp_path)
    monkeypatch.setattr(runner, "trial_prompt", lambda path: "Synthetic prompt")
    monkeypatch.setattr(runner, "get_env", lambda *args: "synthetic-local-key")
    await runner.run_trial("gateway-integration", Path("unused"))
    await runner.run_trial("gateway-integration", Path("unused"))
    state = Store("", tmp_path).snapshot()
    receipt = state.ledger["gateway-integration"]
    assert len(calls) == 1
    assert receipt["models"] == [config().model]
    assert receipt["input_tokens"] == 150 and receipt["output_tokens"] == 50
    assert receipt["observed_text_characters"] == len("synthetic answer")
    assert not receipt["uncertain"] and state.reserved == 0


def test_sonnet_uses_documented_thinking_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sonnet 5.5 uses between_tools, not the unsupported disabled setting."""
    cfg = ClaudeTrialConfig.model_validate_json((runner.TRIAL / "config-art-first.json").read_text())

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert body["thinking"] == {"type": "between_tools"}
        assert body["output_config"] == {"effort": "medium"}
        assert body["model"] == "claude-sonnet-5-5"
        return httpx.Response(200, text=response_events("success").replace("claude-opus-5-5", cfg.model))

    original = httpx.Client
    monkeypatch.setattr(
        "backend.anthropic_trial.httpx.Client",
        lambda **kw: original(transport=httpx.MockTransport(handler), **kw),
    )
    receipt = ClaudeReceipt()
    token = receipt_context.set(receipt)
    try:
        assert (
            ClaudeTrialBackend(cfg.model, "test-key", cfg)
            .run(Request("Synthetic", None, None, 100, None))
            .text
            == "synthetic answer"
        )
    finally:
        receipt_context.reset(token)
    assert receipt.models == [cfg.model] and receipt.billing_complete
    assert receipt.cost_usd == pytest.approx((100 * 2 + 20 * 4 + 30 * 0.1 + 50 * 10) / 1e6)
    with pytest.raises(ValueError, match="verified"):
        ClaudeTrialBackend(config().model, "test", config().model_copy(update={"thinking": "between_tools"}))
