"""Trusted structured Claude authoring adapter behind the shared gateway."""

import json
from typing import cast

from _shared.services.model_gateway import BackendOutput, ModelBackendError, Request

from .anthropic_transport import ClaudeRates, stream_message
from .provider import receipt_context
from .provider_schema import anthropic_schema
from .settings import Settings


class ClaudeAuthoringBackend:
    """Author data only; no tools, retrieval, speech, JavaScript execution or fallback."""

    def __init__(self, model_id: str, settings: Settings) -> None:
        """Bind a verified model/price/allowance tuple from trusted startup settings."""
        if settings.authoring_provider != "anthropic" or model_id != settings.anthropic_model:
            raise ValueError("Claude model has no enabled trusted authoring route")
        # Settings validates model-specific prices, token limits and reservations.
        settings.__post_init__()
        self._model_id, self.settings = model_id, settings

    @property
    def model_id(self) -> str:
        """Requested identity; receipts independently record the actual model."""
        return self._model_id

    @property
    def n_ctx(self) -> int:
        """Conservative byte-derived token ceiling, not the model's context claim."""
        return self.settings.anthropic_max_input_bytes

    def request_body(self, request: Request) -> dict[str, object]:
        """Validate structured contract and exact serialized input before dispatch."""
        if request.label_tokens or not request.grammar:
            raise ModelBackendError("Claude authoring requires a structured JSON contract")
        if not 1 <= request.max_tokens <= self.settings.max_output_tokens:
            raise ModelBackendError("Claude authoring output limit exceeded")
        try:
            original: object = json.loads(request.grammar)
            if not isinstance(original, dict) or original.get("type") != "object":
                raise ValueError("Authoring schema must describe an object")
            schema = anthropic_schema(cast(dict[str, object], original))
        except (ValueError, TypeError) as exc:
            raise ModelBackendError("Claude authoring schema is unsupported") from exc
        messages = (
            list(request.messages) if request.messages
            else [{"role": "user", "content": request.prompt or ""}]
        )
        if not messages or any(message["role"] not in ("system", "user", "assistant") for message in messages):
            raise ModelBackendError("Claude authoring message roles are unsupported")
        system = "\n\n".join(message["content"] for message in messages if message["role"] == "system")
        conversation = [message for message in messages if message["role"] != "system"]
        if not conversation or conversation[-1]["role"] != "user":
            raise ModelBackendError("Claude structured authoring requires a final user message")
        body: dict[str, object] = {
            "model": self.model_id,
            "max_tokens": request.max_tokens,
            "messages": conversation,
            "stream": True,
            "thinking": {"type": "between_tools"},
            "output_config": {
                "effort": "medium", "format": {"type": "json_schema", "schema": schema},
            },
        }
        if system:
            body["system"] = system
        if len(json.dumps(body, ensure_ascii=False).encode()) > self.settings.anthropic_max_input_bytes:
            raise ModelBackendError("Claude authoring context exceeds its reserved input allowance")
        return body

    def run(self, request: Request) -> BackendOutput:
        """Execute one accounted stream; validate JSON before domain decoding."""
        receipt = receipt_context.get()
        if not self.settings.anthropic_key or receipt is None:
            raise ModelBackendError("Claude authoring requires its server key and a scoped usage receipt")
        body = self.request_body(request)
        result = stream_message(
            model=self.model_id, key=self.settings.anthropic_key, body=body,
            timeout=self.settings.provider_timeout_seconds,
            rates=ClaudeRates(
                self.settings.anthropic_input_rate, self.settings.anthropic_output_rate,
                self.settings.anthropic_cache_write_rate, self.settings.anthropic_cache_read_rate,
            ),
            receipt=receipt, max_text_characters=request.max_tokens * 16 + 1024,
        )
        try:
            parsed: object = json.loads(result.text)
        except (ValueError, RecursionError):
            raise ModelBackendError("Claude did not return parseable structured data") from None
        if not isinstance(parsed, dict):
            raise ModelBackendError("Claude authoring returned a non-object document")
        # The original full Pydantic schema and all evidence/quality gates still
        # validate this result in the pipeline. Translation never relaxes them.
        return result
