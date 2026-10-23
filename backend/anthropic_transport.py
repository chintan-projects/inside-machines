"""Shared bounded Messages stream transport for trial and production adapters."""

import time
from dataclasses import dataclass

import httpx
from _shared.services.model_gateway import BackendOutput, ModelBackendError
from pydantic import BaseModel, Field, ValidationError

from .provider import UsageReceipt


@dataclass(frozen=True)
class ClaudeRates:
    """Trusted prices supplied by startup composition, never by a client."""

    input: float
    output: float
    cache_write: float
    cache_read: float


class ClaudeUsage(BaseModel):
    """Provider counters include billed thinking in output tokens."""

    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    cache_creation_input_tokens: int = Field(default=0, ge=0)
    cache_read_input_tokens: int = Field(default=0, ge=0)


class ClaudeMessage(BaseModel):
    """Initial message identity and input usage."""

    model: str = Field(min_length=1, max_length=160)
    usage: ClaudeUsage


class ClaudeDelta(BaseModel):
    """Expose text only; private thinking is neither logged nor persisted."""

    type: str = ""
    text: str = ""
    stop_reason: str | None = None


class ClaudeEvent(BaseModel):
    """Validate the supported Messages SSE event boundary."""

    type: str
    message: ClaudeMessage | None = None
    delta: ClaudeDelta | None = None
    content_block: ClaudeDelta | None = None
    usage: ClaudeUsage | None = None


def stream_message(
    *, model: str, key: str, body: dict[str, object], timeout: int,
    rates: ClaudeRates, receipt: UsageReceipt, max_text_characters: int,
) -> BackendOutput:
    """Dispatch once; incomplete streams retain known usage and uncertain billing."""
    started = time.monotonic()
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
    parts: list[str] = []
    complete, stopped, got_usage, got_start = False, False, False, False
    receipt.billing_complete = False
    try:
        with httpx.Client(timeout=httpx.Timeout(timeout, connect=10)) as client:
            with client.stream(
                "POST", "https://api.anthropic.com/v1/messages", headers=headers, json=body
            ) as response:
                response.raise_for_status()
                receipt.provider_request_id = response.headers.get("request-id", "")[:160]
                for line in response.iter_lines():
                    if time.monotonic() - started > timeout:
                        raise ModelBackendError("Claude deadline exceeded; billing may be uncertain")
                    if not line.startswith("data: "):
                        continue
                    event = ClaudeEvent.model_validate_json(line[6:])
                    if event.type == "message_start" and event.message:
                        if got_start:
                            raise ModelBackendError("Claude returned repeated message identity")
                        got_start = True
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
                        if event.content_block.type == "text" and event.content_block.text:
                            parts.append(event.content_block.text)
                            receipt.observed_text_characters += len(event.content_block.text)
                    elif (
                        event.type == "content_block_delta" and event.delta
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
                            reason = event.delta.stop_reason
                            stopped = reason == "end_turn"
                            receipt.response_status = "completed" if stopped else "incomplete"
                            receipt.incomplete_reason = "" if stopped else (
                                reason if reason in (
                                    "max_tokens", "refusal", "tool_use", "pause_turn", "stop_sequence"
                                ) else "unknown"
                            )
                    elif event.type == "message_stop":
                        complete = True
                    elif event.type == "error":
                        raise ModelBackendError("Claude stream failed; billing may be uncertain")
                    if receipt.observed_text_characters > max_text_characters:
                        raise ModelBackendError("Claude response exceeds its bounded text allowance")
    except httpx.HTTPStatusError as exc:
        raise ModelBackendError(f"Claude returned HTTP {exc.response.status_code}") from None
    except (httpx.RequestError, ValidationError) as exc:
        raise ModelBackendError(
            f"Claude request failed: {type(exc).__name__}; billing may be uncertain"
        ) from None
    finally:
        receipt.cost_usd = (
            receipt.uncached_input_tokens * rates.input
            + receipt.cache_write_tokens * rates.cache_write
            + receipt.cache_read_tokens * rates.cache_read
            + receipt.output_tokens * rates.output
        ) / 1e6
    receipt.billing_complete = complete and got_usage and receipt.models == [model]
    if not complete or not stopped or not got_usage or not got_start or not "".join(parts).strip():
        raise ModelBackendError("Claude did not complete a usable, accounted answer")
    if receipt.models != [model]:
        raise ModelBackendError("Claude model identity differs from configured rates")
    return BackendOutput(text="".join(parts))
