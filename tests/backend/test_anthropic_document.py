"""The provider envelope never replaces the existing typed lesson boundaries."""

import json
from dataclasses import replace

import pytest
from _shared.services.model_gateway import Message, ModelBackendError, Request

from backend.anthropic_authoring import ClaudeAuthoringBackend
from backend.anthropic_document import decode_document, envelope_schema
from backend.author_transport import author_schema, compact_author, expand_author
from backend.contracts import AuthorLessonSpec, LessonSpec
from backend.lesson_patch import patch_schema
from backend.settings import Settings, load_settings


def test_decoder_returns_one_object_for_existing_domain_validation(ce_spec: LessonSpec) -> None:
    """Exactly one string layer is decoded; another wrapper or a list is not an artifact."""
    original = compact_author(ce_spec)
    raw = json.dumps({"document_json": json.dumps(original)})
    decoded = decode_document(raw, max_bytes=161024)
    assert decoded == original
    assert expand_author(json.dumps(decoded)).model_dump() == ce_spec.model_dump()


@pytest.mark.parametrize("raw", [
    "INVALID",
    "[]",
    "null",
    "{}",
    '{"document_json":{}}',
    '{"document_json":false}',
    '{"document_json":""}',
    '{"document_json":"{}","extra":"not permitted"}',
    '{"document_json":"{}","document_json":"{}"}',
    json.dumps({"document_json": "INVALID INNER"}),
    json.dumps({"document_json": "[]"}),
    json.dumps({"document_json": "null"}),
    json.dumps({"document_json": '"another encoded string"'}),
    json.dumps({"document_json": '{"a":1,"a":2}'}),
    json.dumps({"document_json": '{"number":NaN}'}),
    json.dumps({"document_json": '{"number":Infinity}'}),
    json.dumps({"document_json": '{"number":1e309}'}),
    json.dumps({"document_json": '{"number":-1e309}'}),
    json.dumps({"document_json": '{"nested":'+"["*80+"0"+"]"*80+"}"}),
    json.dumps({"document_json": '{"nested":'+"["*1100+"0"+"]"*1100+"}"}),
])
def test_malformed_envelope_or_inner_document_never_succeeds(raw: str) -> None:
    with pytest.raises(ModelBackendError) as error:
        decode_document(raw, max_bytes=10000)
    assert "INVALID INNER" not in str(error.value) and "not permitted" not in str(error.value)


def test_encoded_bytes_and_configuration_are_bounded() -> None:
    with pytest.raises(ModelBackendError):
        decode_document(json.dumps({"document_json": '{"large":"'+"x"*200+'"}'}), max_bytes=100)
    with pytest.raises(ModelBackendError):
        decode_document("\ud800", max_bytes=100)
    for maximum in (0, 513025):
        with pytest.raises(ValueError):
            decode_document('{"document_json":"{}"}', max_bytes=maximum)


def test_request_and_original_schema_are_not_rewritten(settings: Settings) -> None:
    """Transport instructions are isolated from immutable input and lesson-facing copy."""
    config = replace(settings, authoring_provider="anthropic", anthropic_key="synthetic-claude-key")
    adapter = ClaudeAuthoringBackend(config.anthropic_model, config)
    grammar = json.dumps(author_schema())
    messages: tuple[Message, ...] = (
        {"role": "system", "content": "Synthetic trusted teaching policy"},
        {"role": "user", "content": "Synthetic request"},
    )
    before = json.dumps(messages)
    request = Request(None, messages, grammar, 10000, None)
    body = adapter.request_body(request)
    assert request.grammar == grammar and json.dumps(messages) == before
    assert body["messages"] == [messages[1]]
    system = body["system"]
    assert isinstance(system, str) and system.startswith(messages[0]["content"]+"\n\n")
    assert "no indentation or whitespace\noutside string values" in system
    assert "Preserve every required field" in system
    first = envelope_schema()
    first["properties"] = {}
    assert envelope_schema()["properties"] == {"document_json": {"type": "string"}}


@pytest.mark.parametrize("mode", ["compact", "full", "patch"])
def test_each_existing_document_contract_uses_the_same_small_envelope(
    settings: Settings, ce_spec: LessonSpec, mode: str,
) -> None:
    """Transport never drops a patch/base identity or rewrites a task's document contract."""
    config = replace(settings, authoring_provider="anthropic", anthropic_key="synthetic-claude-key")
    schema = (
        author_schema() if mode == "compact"
        else AuthorLessonSpec.model_json_schema() if mode == "full"
        else patch_schema(AuthorLessonSpec.model_validate(ce_spec.model_dump()))
    )
    before = json.dumps(schema, sort_keys=True)
    body = ClaudeAuthoringBackend(config.anthropic_model, config).request_body(
        Request("Synthetic existing task contract", None, json.dumps(schema), 10000, None)
    )
    system = body["system"]
    assert isinstance(system, str)
    assert json.loads(system.split("\nDOCUMENT_SCHEMA_DATA: ")[1]) == schema
    assert json.dumps(schema, sort_keys=True) == before
    output = body["output_config"]
    assert isinstance(output, dict)
    assert output["format"] == {"type": "json_schema", "schema": envelope_schema()}


def test_existing_environment_token_override_reaches_bounded_request(monkeypatch: pytest.MonkeyPatch) -> None:
    """Hosted overrides affect the actual route without changing repository defaults or reserves."""
    monkeypatch.setenv("INSIDE_AUTHORING_PROVIDER", "anthropic")
    monkeypatch.setenv("INSIDE_MAX_OUTPUT_TOKENS", "20000")
    config = load_settings()
    assert config.max_output_tokens == 20000 and config.text_phase_reserve == .65
    body = ClaudeAuthoringBackend(config.anthropic_model, config).request_body(
        Request("Synthetic token allowance preflight", None, json.dumps(author_schema()), 20000, None)
    )
    assert body["max_tokens"] == 20000 and config.generation_reserve == 2
    monkeypatch.setenv("INSIDE_MAX_OUTPUT_TOKENS", "20362")
    with pytest.raises(ValueError, match="Text allowance cannot cover"):
        load_settings()
