"""Explicit, text-only Claude trial adapter; never enabled by the production app."""

import json
import math
from dataclasses import dataclass
from typing import Literal

import httpx as httpx  # Preserve the existing trial HTTP interception seam.
from _shared.services.model_gateway import BackendOutput, ModelBackendError, Request
from pydantic import BaseModel, ConfigDict, Field

from .anthropic_transport import ClaudeRates, stream_message
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

    billing_complete: bool | None = False


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
        return stream_message(
            model=self.model_id, key=self._key, body=body,
            timeout=self.config.timeout_seconds,
            rates=ClaudeRates(
                self.config.input_usd_per_million, self.config.output_usd_per_million,
                self.config.cache_write_usd_per_million, self.config.cache_read_usd_per_million,
            ),
            receipt=receipt, max_text_characters=self.config.max_output_tokens * 16 + 1024,
        )
