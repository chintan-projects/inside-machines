"""Hosted backends registered with the mandatory workspace Model Gateway."""

import base64
import json
import time
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Literal

import httpx
from _shared.services.logger import get_logger
from _shared.services.model_gateway import (
    BackendOutput,
    ModelBackendError,
    Request,
    invoke_model,
    set_backend_factory,
)
from pydantic import BaseModel, Field

from .provider_schema import openai_schema
from .routing import TASKS, ModelTask, ProviderPlugin, ProviderRegistry, TaskRoute, gateway_id
from .settings import Settings

logger = get_logger(__name__)


class ProviderUsage(BaseModel):
    """Usage returned by the provider, including charged output/reasoning tokens."""

    input_tokens: int = 0
    output_tokens: int = 0


class TextBlock(BaseModel):
    """Response content may also contain a refusal instead of text."""

    type: str = ""
    text: str = ""
    refusal: str = ""


class ToolAction(BaseModel):
    """Distinguish chargeable searches from page opens and in-page finds."""

    type: str = ""


class OutputItem(BaseModel):
    """Only the fields needed for bounded output and tool accounting."""

    type: str = ""
    action: ToolAction | None = None
    content: list[TextBlock] = Field(default_factory=list)


class ProviderResponse(BaseModel):
    """Ignore provider metadata not needed by the product."""

    status: str = ""
    model: str = Field(default="", max_length=160)
    output: list[OutputItem] = Field(default_factory=list)
    usage: ProviderUsage = Field(default_factory=ProviderUsage)
    incomplete_details: dict[str, str] | None = None


@dataclass
class UsageReceipt:
    """Mutable request-scoped collector survives the gateway's worker-thread boundary."""

    input_tokens: int = 0
    output_tokens: int = 0
    search_calls: int = 0
    web_tool_calls: int = 0
    search_estimated: bool = False
    response_status: str = ""
    incomplete_reason: str = ""
    model_identity_estimated: bool = False
    speech_characters: int = 0
    cost_usd: float = 0
    models: list[str] = field(default_factory=list)
    uncached_input_tokens: int = 0
    cache_write_tokens: int = 0
    cache_read_tokens: int = 0
    provider_request_id: str = ""
    observed_text_characters: int = 0
    first_text_seconds: float | None = None
    # None preserves the older non-streaming receipt contract. A streaming
    # adapter explicitly keeps False until the terminal usage event arrives.
    billing_complete: bool | None = None


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
            with httpx.Client(
                timeout=httpx.Timeout(self.settings.provider_timeout_seconds, connect=10)
            ) as client:
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
                    receipt.model_identity_estimated = True
                    return BackendOutput(text=base64.b64encode(response.content).decode())
                messages = list(request.messages or ({"role": "user", "content": request.prompt or ""},))
                if len(json.dumps(messages).encode()) > 100000:
                    raise ModelBackendError("Lesson context exceeds the alpha input budget")
                body: dict[str, object] = {
                    "model": self._model_id,
                    "input": messages,
                    "max_output_tokens": request.max_tokens,
                    "store": False,
                    "reasoning": {"effort": self.settings.reasoning_effort},
                }
                if request.grammar:
                    body["text"] = {
                        "format": {
                            "type": "json_schema",
                            "name": "lesson_response",
                            "strict": True,
                            "schema": openai_schema(json.loads(request.grammar)),
                        }
                    }
                # Research is an explicit evidence phase; authoring/review/chat do not search.
                if request.prompt and request.prompt.startswith("RESEARCH_MACHINE\n"):
                    body["tools"] = [{"type": "web_search"}]
                    body["max_tool_calls"] = 3
                response = client.post("https://api.openai.com/v1/responses", headers=headers, json=body)
                response.raise_for_status()
                parsed = ProviderResponse.model_validate_json(response.content)
                receipt.response_status = (
                    parsed.status if parsed.status in ("completed", "incomplete", "failed") else "unknown"
                )
                reason = (parsed.incomplete_details or {}).get("reason", "")
                receipt.incomplete_reason = (
                    reason if reason in ("max_output_tokens", "content_filter", "") else "unknown"
                )
                web_calls = [item for item in parsed.output if item.type == "web_search_call"]
                # Open/find actions have no search-tool fee. If the provider omits
                # an action, retain a conservative estimate rather than assume zero.
                searches = sum(
                    item.action is None or item.action.type not in ("open_page", "find_in_page")
                    for item in web_calls
                )
                receipt.web_tool_calls += len(web_calls)
                receipt.search_estimated |= any(
                    item.action is None or item.action.type not in ("search", "open_page", "find_in_page")
                    for item in web_calls
                )
                receipt.input_tokens += parsed.usage.input_tokens
                receipt.output_tokens += parsed.usage.output_tokens
                receipt.search_calls += searches
                receipt.cost_usd += (
                    parsed.usage.input_tokens * self.settings.input_rate
                    + parsed.usage.output_tokens * self.settings.output_rate
                ) / 1e6 + searches * 0.01
                receipt.models.append(parsed.model or self._model_id)
                receipt.model_identity_estimated |= not bool(parsed.model)
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


def configure_gateway(settings: Settings, registry: ProviderRegistry | None = None) -> None:
    """Install explicit task routes using the shared gateway's public extension point.

    Custom registries are trusted startup dependencies, never HTTP request data.
    Claude authoring is opt-in; research, review, chat and speech retain their
    own OpenAI routes. Adapter contract tests do not establish lesson quality.
    """
    if registry is None:
        from .anthropic_authoring import ClaudeAuthoringBackend

        plugins = {
            "openai": ProviderPlugin(lambda model: HostedBackend(model, settings), frozenset(TASKS)),
            "anthropic": ProviderPlugin(
                lambda model: ClaudeAuthoringBackend(model, settings), frozenset({"authoring"})
            ),
        }
        routes = {
            task: TaskRoute("openai", settings.speech_model if task == "speech" else settings.model)
            for task in TASKS
        }
        if settings.authoring_provider == "anthropic":
            routes["authoring"] = TaskRoute("anthropic", settings.anthropic_model)
        selected = ProviderRegistry(plugins, routes)
    else:
        selected = registry
    set_backend_factory(selected.backend)


async def _invoke_task(
    task: ModelTask, prompt: str, *, schema: dict[str, object] | None, max_tokens: int, timeout_ms: int
) -> str:
    """Log bounded metadata, excluding prompts, answers and credentials."""
    started = time.monotonic()
    try:
        result = await invoke_model(
            prompt=prompt,
            models=[gateway_id(task)],
            grammar=json.dumps(schema) if schema else None,
            max_tokens=max_tokens,
            timeout_ms=timeout_ms,
        )
    except Exception as exc:
        # Log metadata then propagate; callers retain uncertain billing and checkpoints.
        logger.warning(
            "Model task failed",
            task=task,
            error_type=type(exc).__name__,
            duration_ms=round((time.monotonic() - started) * 1000, 1),
        )
        raise
    logger.info(
        "Model task completed",
        task=task,
        route=result.model_id,
        duration_ms=round((time.monotonic() - started) * 1000, 1),
    )
    return result.text


async def model_text(
    prompt: str,
    settings: Settings,
    *,
    schema: dict[str, object] | None = None,
    chat: bool = False,
    task: Literal["research", "authoring", "review"] = "authoring",
) -> str:
    """Call the selected task through the shared gateway with explicit bounds."""
    return await _invoke_task(
        "chat" if chat else task,
        prompt,
        schema=schema,
        max_tokens=settings.max_chat_tokens
        if chat
        else settings.max_research_tokens
        if task == "research"
        else settings.max_output_tokens,
        timeout_ms=(settings.provider_timeout_seconds + 10) * 1000,
    )


async def model_speech(narration: str, settings: Settings) -> bytes:
    """Synthesize one stage through the dedicated speech route."""
    result = await _invoke_task(
        "speech",
        narration,
        schema=None,
        max_tokens=1,
        timeout_ms=(settings.provider_timeout_seconds + 10) * 1000,
    )
    return base64.b64decode(result, validate=True)
