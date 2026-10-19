"""llama-cpp-python backend: one resident ``Llama`` per model id.

Construction reads the registry entry, loads the GGUF with every layer offloaded
(``n_gpu_layers=-1`` unless the entry sets ``n_gpu_layers``), ``n_ctx`` from the entry's
``context_length`` capped at ``N_CTX_CAP`` (plan correction C-b), ``verbose=False`` and the
native library's stdout/stderr redirected to ``/dev/null`` while it loads (plan correction C-d:
an MCP server owns stdout, and llama.cpp still prints to stderr with ``verbose=False``).

Chat turns go through the model's own Jinja chat template from the GGUF metadata
(``tokenizer.chat_template``); a model without one gets a plain ``role: content`` prompt.

Label probabilities (``Request.label_tokens``) take one forward pass: ``Llama.reset()``,
``Llama.eval(prompt_tokens)``, then the last-position logits through
``llama_cpp.llama_get_logits_ith(ctx, -1)``. ``Llama.scores`` is not an option in 0.3.16: it is
only written when ``logits_all=True``, which this backend does not set (it would compute logits
for every prompt position on every call).

Nothing here is thread-safe; the gateway serializes calls per model.
"""

import contextlib
import os
import sys
import time
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Any, cast

import llama_cpp
import numpy as np
import numpy.typing as npt
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Jinja2ChatFormatter
from llama_cpp.llama_grammar import LlamaGrammar
from llama_cpp.llama_types import ChatCompletionRequestMessage, CreateCompletionResponse

from ..logger import get_logger
from .contracts import (
    BackendOutput,
    LabelTokenizationError,
    Message,
    ModelBackendError,
    ModelGatewayError,
    Request,
)
from .registry import ModelEntry, get_model_config

logger = get_logger(__name__)

N_CTX_CAP = 4096
DEFAULT_GPU_LAYERS = -1
CHAT_TEMPLATE_KEY = "tokenizer.chat_template"


def resolve_n_ctx(entry: ModelEntry) -> int:
    """The context window to load with: the entry's ``context_length`` capped at ``N_CTX_CAP``."""
    raw = entry.get("context_length", N_CTX_CAP)
    if not isinstance(raw, int) or isinstance(raw, bool) or raw <= 0:
        raise ModelBackendError(f"registry context_length must be a positive integer, got {raw!r}")
    return min(raw, N_CTX_CAP)


def resolve_gpu_layers(entry: ModelEntry) -> int:
    """``n_gpu_layers`` for the load: the entry's value, else every layer (``-1``)."""
    raw = entry.get("n_gpu_layers", DEFAULT_GPU_LAYERS)
    if not isinstance(raw, int) or isinstance(raw, bool):
        raise ModelBackendError(f"registry n_gpu_layers must be an integer, got {raw!r}")
    return raw


@contextlib.contextmanager
def silence_native_output() -> Iterator[None]:
    """Send file descriptors 1 and 2 to ``/dev/null`` for the block; restore them after.

    Python-level ``sys.stdout`` is untouched; this exists for native code that writes to the
    descriptors directly.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    devnull = os.open(os.devnull, os.O_WRONLY)
    saved = [os.dup(fd) for fd in (1, 2)]
    try:
        for fd in (1, 2):
            os.dup2(devnull, fd)
        yield
    finally:
        for fd, original in zip((1, 2), saved, strict=True):
            os.dup2(original, fd)
            os.close(original)
        os.close(devnull)


@dataclass(frozen=True)
class RenderedPrompt:
    """A prompt ready to tokenize: the text, whether BOS is still needed, and stop strings."""

    text: str
    add_bos: bool
    stop: tuple[str, ...] = ()


def render_plain(messages: Sequence[Message]) -> str:
    """The fallback for a GGUF without a chat template: ``role: content`` lines, then the
    assistant turn opened with a trailing newline so labels tokenize after a line start."""
    body = "\n".join(f"{message['role']}: {message['content']}" for message in messages)
    return f"{body}\nassistant:\n"


def softmax(logits: npt.NDArray[np.floating[Any]]) -> npt.NDArray[np.float64]:
    """Numerically stable softmax in float64 over a one-dimensional array."""
    shifted = logits.astype(np.float64) - float(logits.max())
    exp = np.exp(shifted)
    return cast(npt.NDArray[np.float64], exp / exp.sum())


class LlamaCppBackend:
    """One loaded GGUF. Implements ``ModelBackend``; construction is the load."""

    def __init__(self, model_id: str, entry: ModelEntry | None = None) -> None:
        """Load ``model_id``. ``entry`` overrides the registry lookup (tests, pinned configs).

        Raises:
            ModelUnavailableError: ``model_id`` is not registered.
            ModelBackendError: The entry is malformed, the file is missing, or the load failed.
        """
        self._model_id = model_id
        config = entry if entry is not None else get_model_config(model_id)
        path = config.get("path")
        if not isinstance(path, str) or not path:
            raise ModelBackendError(f"registry entry for {model_id!r} has no path")
        if not os.path.isfile(path):
            raise ModelBackendError(f"model file for {model_id!r} is missing: {path}")
        n_ctx = resolve_n_ctx(config)
        n_gpu_layers = resolve_gpu_layers(config)

        started = time.perf_counter()
        try:
            with silence_native_output():
                self._llama = Llama(
                    model_path=path, n_gpu_layers=n_gpu_layers, n_ctx=n_ctx, verbose=False
                )
        except Exception as exc:
            raise ModelBackendError(f"{model_id!r} failed to load from {path}: {exc}") from exc
        self._n_ctx = int(self._llama.n_ctx())
        self._bos_text = self._token_text(self._llama.token_bos())
        self._formatter = self._build_formatter()
        logger.info(
            "model loaded",
            model_id=model_id,
            path=path,
            n_ctx=self._n_ctx,
            n_gpu_layers=n_gpu_layers,
            chat_template=self._formatter is not None,
            load_ms=round((time.perf_counter() - started) * 1000, 1),
        )

    @property
    def model_id(self) -> str:
        """The registry id this backend serves."""
        return self._model_id

    @property
    def n_ctx(self) -> int:
        """The context window the model was loaded with."""
        return self._n_ctx

    def count_tokens(self, text: str) -> int:
        """How many tokens ``text`` takes, BOS excluded (for callers sizing a prompt)."""
        return len(self._tokenize(text, add_bos=False))

    def run(self, request: Request) -> BackendOutput:
        """Serve one request: label probabilities if ``label_tokens`` is set, else a completion.

        Raises:
            LabelTokenizationError: A label is not exactly one token after the prompt.
            ModelBackendError: The prompt does not fit ``n_ctx`` or the model errored.
        """
        rendered = self.render(request)
        try:
            if request.label_tokens is not None:
                return self._label_probs(rendered, request.label_tokens)
            return self._generate(rendered, request)
        except ModelGatewayError:
            raise
        except Exception as exc:
            raise ModelBackendError(f"{self._model_id!r} call failed: {exc}") from exc

    def render(self, request: Request) -> RenderedPrompt:
        """The text the model will see: a raw prompt as-is, or chat turns through the template."""
        if request.prompt is not None:
            return RenderedPrompt(text=request.prompt, add_bos=True)
        messages = list(request.messages or ())
        if self._formatter is None:
            return RenderedPrompt(text=render_plain(messages), add_bos=True)
        response = self._formatter(messages=cast(list[ChatCompletionRequestMessage], messages))
        stop = response.stop
        stops = (stop,) if isinstance(stop, str) else tuple(stop or ())
        # Jinja2ChatFormatter reports added_special=True unconditionally, so decide from the text:
        # a template that emits bos_token (LFM2.5 does) must not get a second BOS; one that does
        # not (Qwen2.5) gets add_bos=True, which llama.cpp still skips when the vocab says so.
        already_has_bos = bool(self._bos_text) and response.prompt.startswith(self._bos_text)
        return RenderedPrompt(text=response.prompt, add_bos=not already_has_bos, stop=stops)

    def _build_formatter(self) -> Jinja2ChatFormatter | None:
        template = self._llama.metadata.get(CHAT_TEMPLATE_KEY)
        if not isinstance(template, str) or not template:
            logger.warning(
                "GGUF has no chat template; using plain prompts", model_id=self._model_id
            )
            return None
        return Jinja2ChatFormatter(
            template=template,
            eos_token=self._token_text(self._llama.token_eos()),
            bos_token=self._bos_text,
            add_generation_prompt=True,
        )

    def _token_text(self, token_id: int) -> str:
        if token_id < 0:
            return ""
        return self._llama.detokenize([token_id], special=True).decode("utf-8", errors="replace")

    def _tokenize(self, text: str, add_bos: bool) -> list[int]:
        # special=True so template control tokens tokenize as tokens, matching create_completion.
        return list(self._llama.tokenize(text.encode("utf-8"), add_bos=add_bos, special=True))

    def _prompt_tokens(self, rendered: RenderedPrompt) -> list[int]:
        tokens = self._tokenize(rendered.text, rendered.add_bos)
        if len(tokens) >= self._n_ctx:
            raise ModelBackendError(
                f"prompt of {len(tokens)} tokens does not fit n_ctx={self._n_ctx} "
                f"for {self._model_id!r}"
            )
        return tokens

    def _label_ids(
        self, rendered: RenderedPrompt, prompt_tokens: list[int], labels: Sequence[str]
    ) -> dict[str, int]:
        """Each label's token id in context: tokenize prompt+label, take what follows the prompt."""
        n_prompt = len(prompt_tokens)
        ids: dict[str, int] = {}
        for label in labels:
            full = self._tokenize(rendered.text + label, rendered.add_bos)
            if full[:n_prompt] != prompt_tokens:
                raise LabelTokenizationError(
                    self._model_id, label, "it merges with the end of the prompt"
                )
            extra = full[n_prompt:]
            if len(extra) != 1:
                raise LabelTokenizationError(
                    self._model_id, label, f"it is {len(extra)} tokens after the prompt"
                )
            if extra[0] in ids.values():
                raise LabelTokenizationError(
                    self._model_id, label, f"it shares token id {extra[0]} with another label"
                )
            ids[label] = extra[0]
        return ids

    def _label_probs(self, rendered: RenderedPrompt, labels: Sequence[str]) -> BackendOutput:
        prompt_tokens = self._prompt_tokens(rendered)
        ids = self._label_ids(rendered, prompt_tokens, labels)
        llama = self._llama
        llama.reset()  # type: ignore[no-untyped-call]  # llama-cpp leaves reset() unannotated
        llama.eval(prompt_tokens)
        logits = llama_cpp.llama_get_logits_ith(llama.ctx, -1)
        probs = softmax(np.ctypeslib.as_array(logits, shape=(llama.n_vocab(),)))
        raw = {label: float(probs[token_id]) for label, token_id in ids.items()}
        mass = sum(raw.values())
        if mass <= 0.0:
            raise ModelBackendError(f"label tokens hold no probability mass for {self._model_id!r}")
        label_probs = {label: p / mass for label, p in raw.items()}
        text = max(label_probs, key=lambda label: label_probs[label])
        return BackendOutput(text=text, label_probs=label_probs, label_mass=mass)

    def _generate(self, rendered: RenderedPrompt, request: Request) -> BackendOutput:
        prompt_tokens = self._prompt_tokens(rendered)
        grammar = (
            LlamaGrammar.from_string(request.grammar, verbose=False) if request.grammar else None
        )
        response = self._llama.create_completion(
            prompt_tokens,
            max_tokens=request.max_tokens,
            temperature=0.0,
            grammar=grammar,
            stop=list(rendered.stop),
            stream=False,
        )
        completion = cast(CreateCompletionResponse, response)
        return BackendOutput(text=completion["choices"][0]["text"])
