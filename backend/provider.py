"""Hosted backends registered with the mandatory workspace Model Gateway."""

import base64
import json
from contextvars import ContextVar
from dataclasses import dataclass, field

import httpx
from _shared.services.model_gateway import (
    BackendOutput,
    ModelBackendError,
    Request,
    invoke_model,
    set_backend_factory,
)
from pydantic import BaseModel, Field

from .settings import Settings


class ProviderUsage(BaseModel):
    """Usage returned by the provider, including charged output/reasoning tokens."""

    input_tokens: int = 0
    output_tokens: int = 0


class TextBlock(BaseModel):
    """Response content may also contain a refusal instead of text."""

    type: str = ""
    text: str = ""
    refusal: str = ""


class OutputItem(BaseModel):
    """Only the fields needed for bounded output and tool accounting."""

    type: str = ""
    content: list[TextBlock] = Field(default_factory=list)


class ProviderResponse(BaseModel):
    """Ignore provider metadata not needed by the product."""

    status: str = ""
    output: list[OutputItem] = Field(default_factory=list)
    usage: ProviderUsage = Field(default_factory=ProviderUsage)


@dataclass
class UsageReceipt:
    """Mutable request-scoped collector survives the gateway's worker-thread boundary."""

    input_tokens: int = 0
    output_tokens: int = 0
    search_calls: int = 0
    speech_characters: int = 0
    cost_usd: float = 0
    models: list[str] = field(default_factory=list)


receipt_context: ContextVar[UsageReceipt | None] = ContextVar("inside_usage", default=None)


class HostedBackend:
    """Sync gateway backend for Responses or speech; no silent fallback to invented text."""

    def __init__(self, model_id: str, settings: Settings) -> None:
        """Bind provider settings without exposing credentials to callers."""
        self._model_id = model_id
        self.settings = settings

    @property
    def model_id(self) -> str:
        """Gateway model identifier."""
        return self._model_id

    @property
    def n_ctx(self) -> int:
        """Application's conservative input bound, not a provider context claim."""
        return 32000

    def run(self, request: Request) -> BackendOutput:
        """Execute exactly one bounded request and account for observed usage."""
        if not self.settings.openai_key:
            raise ModelBackendError("A server-side OpenAI key has not been configured")
        receipt = receipt_context.get()
        if receipt is None:
            raise ModelBackendError("Model calls require a usage receipt")
        headers = {"Authorization": "Bearer " + self.settings.openai_key}
        try:
            with httpx.Client(timeout=httpx.Timeout(100, connect=10)) as client:
                if self._model_id == self.settings.speech_model:
                    text = request.prompt or ""
                    if len(text) > 9000:
                        raise ModelBackendError("Narration exceeds the bounded speech request")
                    response = client.post(
                        "https://api.openai.com/v1/audio/speech",
                        headers=headers,
                        json={
                            "model": self._model_id,
                            "voice": self.settings.speech_voice,
                            "input": text,
                            "response_format": "mp3",
                            "instructions": "Speak clearly and warmly, like a patient science teacher. Moderate pace. Read exactly the supplied narration.",
                        },
                    )
                    response.raise_for_status()
                    receipt.speech_characters += len(text)
                    # Speech endpoint does not return the text usage contract. Label as estimate.
                    receipt.cost_usd += len(text.split()) / 130 * self.settings.speech_rate
                    receipt.models.append(self._model_id)
                    return BackendOutput(text=base64.b64encode(response.content).decode())
                messages = list(request.messages or ({"role": "user", "content": request.prompt or ""},))
                if len(json.dumps(messages).encode()) > 100000:
                    raise ModelBackendError("Lesson context exceeds the alpha input budget")
                body: dict[str, object] = {
                    "model": self._model_id,
                    "input": messages,
                    "max_output_tokens": request.max_tokens,
                    "store": False,
                }
                if request.grammar:
                    body["text"] = {
                        "format": {
                            "type": "json_schema",
                            "name": "lesson_response",
                            "strict": True,
                            "schema": json.loads(request.grammar),
                        }
                    }
                # Research is used for new lesson authoring only, never ordinary chat.
                if request.prompt and request.prompt.startswith("RESEARCH_MACHINE\n"):
                    body["tools"] = [{"type": "web_search"}]
                    body["max_tool_calls"] = 3
                response = client.post("https://api.openai.com/v1/responses", headers=headers, json=body)
                response.raise_for_status()
                parsed = ProviderResponse.model_validate_json(response.content)
                searches = sum(item.type == "web_search_call" for item in parsed.output)
                receipt.input_tokens += parsed.usage.input_tokens
                receipt.output_tokens += parsed.usage.output_tokens
                receipt.search_calls += searches
                receipt.cost_usd += (
                    parsed.usage.input_tokens * self.settings.input_rate
                    + parsed.usage.output_tokens * self.settings.output_rate
                ) / 1e6 + searches * 0.01
                receipt.models.append(self._model_id)
                texts = [
                    block.text
                    for item in parsed.output
                    for block in item.content
                    if block.type == "output_text"
                ]
                if parsed.status != "completed" or not texts:
                    raise ModelBackendError("The provider did not complete a usable answer")
                return BackendOutput(text="\n".join(texts))
        except httpx.HTTPStatusError as exc:
            raise ModelBackendError(f"Provider returned HTTP {exc.response.status_code}") from exc
        except httpx.RequestError as exc:
            raise ModelBackendError("The model provider could not be reached") from exc


def configure_gateway(settings: Settings) -> None:
    """Use the gateway's public extension point; leave shared code unmodified."""
    set_backend_factory(lambda model_id: HostedBackend(model_id, settings))


async def model_text(
    prompt: str, settings: Settings, *, schema: dict[str, object] | None = None, chat: bool = False
) -> str:
    """Call text generation through the shared gateway with explicit bounds."""
    result = await invoke_model(
        prompt=prompt,
        models=[settings.model],
        grammar=json.dumps(schema) if schema else None,
        max_tokens=settings.max_chat_tokens if chat else settings.max_output_tokens,
        timeout_ms=110000,
    )
    return result.text


async def model_speech(narration: str, settings: Settings) -> bytes:
    """Synthesize one stage through the mandatory model gateway."""
    result = await invoke_model(
        prompt=narration, models=[settings.speech_model], max_tokens=1, timeout_ms=110000
    )
    return base64.b64decode(result.text, validate=True)
