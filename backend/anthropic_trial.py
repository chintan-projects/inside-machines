"""Explicit, text-only Claude trial adapter; never enabled by the production app."""

import json
import math
import time
from dataclasses import dataclass
from typing import Literal

import httpx
from _shared.services.model_gateway import BackendOutput, ModelBackendError, Request
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .provider import UsageReceipt, receipt_context


class ClaudeTrialConfig(BaseModel):
    """Trusted model-specific limits and list prices, checked before dispatch."""

    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)
    model: str = Field(pattern=r"^claude-[a-z0-9][a-z0-9-]+$", max_length=160)
    input_usd_per_million: float = Field(gt=0)
    output_usd_per_million: float = Field(gt=0)
    cache_write_usd_per_million: float = Field(gt=0)
    cache_read_usd_per_million: float = Field(gt=0)
    max_input_bytes: int = Field(ge=1024, le=250000)
    max_output_tokens: int = Field(ge=1, le=32000)
    timeout_seconds: int = Field(ge=10, le=600)
    effort: Literal["medium", "high"] = "high"
    thinking: Literal["adaptive", "between_tools"] = "adaptive"
    budget_usd: float = Field(gt=0, le=5)

    def allowance(self) -> float:
        """Conservative byte/token ceiling plus fixed protocol headroom; no tools/cache."""
        result = (
            (self.max_input_bytes + 4096) * self.input_usd_per_million
            + self.max_output_tokens * self.output_usd_per_million
        ) / 1e6
        if not math.isfinite(result) or result > self.budget_usd:
            raise ValueError("Trial allowance exceeds its finite ceiling")
        return result


@dataclass
class ClaudeReceipt(UsageReceipt):
    """Retain cache distinctions and provider request identity in the existing ledger."""

    uncached_input_tokens: int = 0
    cache_write_tokens: int = 0
    cache_read_tokens: int = 0
    provider_request_id: str = ""
    observed_text_characters: int = 0
    first_text_seconds: float | None = None
    billing_complete: bool = False


class ClaudeUsage(BaseModel):
    """Observed provider counters; output includes billed thinking tokens."""

    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    cache_creation_input_tokens: int = Field(default=0, ge=0)
    cache_read_input_tokens: int = Field(default=0, ge=0)


class ClaudeMessage(BaseModel):
    """Initial streamed message identity and input usage."""

    model: str = Field(min_length=1, max_length=160)
    usage: ClaudeUsage


class ClaudeDelta(BaseModel):
    """Only text deltas are exposed; private thinking is never logged or saved."""

    type: str = ""
    text: str = ""
    stop_reason: str | None = None


class ClaudeEvent(BaseModel):
    """Boundary validation for the subset of the Messages SSE protocol we support."""

    type: str
    message: ClaudeMessage | None = None
    delta: ClaudeDelta | None = None
    content_block: ClaudeDelta | None = None
    usage: ClaudeUsage | None = None


class ClaudeTrialBackend:
    """One bounded Messages call, with no retry, tools, remote code execution or fallback."""

    def __init__(self, model_id: str, key: str, config: ClaudeTrialConfig) -> None:
        """Only trusted startup composition can supply credentials or model selection."""
        if model_id != config.model:
            raise ValueError("Model has no verified trial pricing")
        if config.model != "claude-sonnet-5-5" and config.thinking == "between_tools":
            raise ValueError("Only the verified Sonnet 5.5 trial accepts between_tools")
        config.allowance()
        self._model_id, self._key, self.config = model_id, key, config

    @property
    def model_id(self) -> str:
        """Gateway identity; receipts separately retain the provider's actual model."""
        return self._model_id

    @property
    def n_ctx(self) -> int:
        """Conservative application context bound, not the provider's advertised limit."""
        return self.config.max_input_bytes

    def request_body(self, request: Request) -> dict[str, object]:
        """Preflight the exact payload before a caller reserves or dispatches paid work."""
        if request.grammar or request.label_tokens:
            raise ModelBackendError("Claude local trial supports plain text only")
        if not 1 <= request.max_tokens <= self.config.max_output_tokens:
            raise ModelBackendError("Claude trial output limit exceeded")
        messages = (
            list(request.messages)
            if request.messages
            else [{"role": "user", "content": request.prompt or ""}]
        )
        system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
        body: dict[str, object] = {
            "model": self.model_id,
            "max_tokens": request.max_tokens,
            "stream": True,
            "messages": [m for m in messages if m["role"] != "system"],
            "thinking": {"type": self.config.thinking},
            "output_config": {"effort": self.config.effort},
        }
        if system:
            body["system"] = system
        if len(json.dumps(body, ensure_ascii=False).encode()) > self.config.max_input_bytes:
            raise ModelBackendError("Claude trial context limit exceeded")
        return body

    def run(self, request: Request) -> BackendOutput:
        """Reject unsupported contracts before dispatch and account for streamed usage."""
        receipt = receipt_context.get()
        if not self._key or not isinstance(receipt, ClaudeReceipt):
            raise ModelBackendError("Claude trial requires a key and its scoped receipt")
        body = self.request_body(request)
        started = time.monotonic()
        headers = {"x-api-key": self._key, "anthropic-version": "2023-06-01"}
        parts: list[str] = []
        complete, stopped, got_usage = False, False, False
        try:
            with httpx.Client(timeout=httpx.Timeout(self.config.timeout_seconds, connect=10)) as client:
                with client.stream(
                    "POST", "https://api.anthropic.com/v1/messages", headers=headers, json=body
                ) as response:
                    response.raise_for_status()
                    receipt.provider_request_id = response.headers.get("request-id", "")[:160]
                    for line in response.iter_lines():
                        if time.monotonic() - started > self.config.timeout_seconds:
                            raise ModelBackendError(
                                "Claude trial deadline exceeded; billing may be uncertain"
                            )
                        if not line.startswith("data: "):
                            continue
                        event = ClaudeEvent.model_validate_json(line[6:])
                        if event.type == "message_start" and event.message:
                            receipt.models.append(event.message.model)
                            usage = event.message.usage
                            if "input_tokens" not in usage.model_fields_set:
                                raise ModelBackendError("Claude input usage is missing")
                            receipt.uncached_input_tokens = usage.input_tokens
                            receipt.cache_write_tokens = usage.cache_creation_input_tokens
                            receipt.cache_read_tokens = usage.cache_read_input_tokens
                            receipt.input_tokens = (
                                usage.input_tokens + receipt.cache_write_tokens + receipt.cache_read_tokens
                            )
                        elif event.type == "content_block_start" and event.content_block:
                            if event.content_block.type not in ("text", "thinking", "redacted_thinking"):
                                raise ModelBackendError("Claude returned unsupported content")
                        elif (
                            event.type == "content_block_delta"
                            and event.delta
                            and event.delta.type == "text_delta"
                        ):
                            parts.append(event.delta.text)
                            receipt.observed_text_characters += len(event.delta.text)
                            if receipt.first_text_seconds is None:
                                receipt.first_text_seconds = round(time.monotonic() - started, 3)
                        elif event.type == "message_delta":
                            if event.usage:
                                if "output_tokens" not in event.usage.model_fields_set:
                                    raise ModelBackendError("Claude output usage is missing")
                                receipt.output_tokens = event.usage.output_tokens
                                got_usage = True
                            if event.delta and event.delta.stop_reason:
                                stopped = event.delta.stop_reason == "end_turn"
                                receipt.response_status = "completed" if stopped else "incomplete"
                                receipt.incomplete_reason = (
                                    ""
                                    if stopped
                                    else (
                                        event.delta.stop_reason
                                        if event.delta.stop_reason
                                        in (
                                            "max_tokens",
                                            "refusal",
                                            "tool_use",
                                            "pause_turn",
                                            "stop_sequence",
                                        )
                                        else "unknown"
                                    )
                                )
                        elif event.type == "message_stop":
                            complete = True
                        elif event.type == "error":
                            raise ModelBackendError("Claude stream failed; billing may be uncertain")
        except httpx.HTTPStatusError as exc:
            raise ModelBackendError(f"Claude returned HTTP {exc.response.status_code}") from None
        except (httpx.RequestError, ValidationError) as exc:
            raise ModelBackendError(
                f"Claude trial failed: {type(exc).__name__}; billing may be uncertain"
            ) from None
        finally:
            receipt.cost_usd = (
                receipt.uncached_input_tokens * self.config.input_usd_per_million
                + receipt.cache_write_tokens * self.config.cache_write_usd_per_million
                + receipt.cache_read_tokens * self.config.cache_read_usd_per_million
                + receipt.output_tokens * self.config.output_usd_per_million
            ) / 1e6
        receipt.billing_complete = complete and got_usage and receipt.models == [self.model_id]
        if not complete or not stopped or not got_usage or not receipt.models or not "".join(parts).strip():
            raise ModelBackendError("Claude did not complete a usable, accounted answer")
        if receipt.models != [self.model_id]:
            raise ModelBackendError("Claude model identity differs from the configured trial rates")
        return BackendOutput(text="".join(parts))
