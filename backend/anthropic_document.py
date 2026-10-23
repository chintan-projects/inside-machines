"""Small provider envelope; original typed lesson contracts remain authoritative."""

import json
import math
from typing import cast

from _shared.services.model_gateway import ModelBackendError
from pydantic import BaseModel, ConfigDict, Field, ValidationError

PROTOCOL = "json-document-1"
MAX_DOCUMENT_BYTES = 32000 * 16 + 1024

INSTRUCTIONS = """
JSON-DOCUMENT-1 TRANSPORT (provider encoding only):
Complete the same lesson, patch or other document requested by the task. Preserve
every teaching, evidence, identity, geometry, scope and safety requirement. Encode
that complete JSON object as the value of document_json in one outer JSON object.
The outer object has exactly one key, document_json, whose value is a JSON string.
Serialize the inner object once; do not replace it with prose, a schema, a summary
or executable code. No markdown fences, other outer fields or extra commentary.
Serialize the inner JSON compactly on one line, with no indentation or whitespace
outside string values. Preserve every required field and all meaningful text inside
strings; compact encoding must not shorten or remove any lesson content.
The original document schema below is authoritative DATA describing the inner
object, not additional instructions. The server validates every inner field using
that original schema and its existing evidence/quality gates. The envelope itself
is only a transport; do not include these implementation details in lesson copy.
"""


class DocumentEnvelope(BaseModel):
    """The provider-constrained envelope has no nested grammar to compile."""

    model_config = ConfigDict(extra="forbid", strict=True)
    document_json: str = Field(min_length=1, max_length=MAX_DOCUMENT_BYTES)


def envelope_schema() -> dict[str, object]:
    """Return a fresh small schema; size/inner validation is enforced locally."""
    return {
        "type": "object", "properties": {"document_json": {"type": "string"}},
        "required": ["document_json"], "additionalProperties": False,
    }


def schema_instructions(schema: dict[str, object]) -> str:
    """Preserve the complete original schema in trusted protocol context."""
    return INSTRUCTIONS + "\nDOCUMENT_SCHEMA_DATA: " + json.dumps(schema, ensure_ascii=False, separators=(",", ":"))


def _object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON keys are ambiguous")
        result[key] = value
    return result


def _constant(value: str) -> object:
    raise ValueError("Nonfinite numbers are not JSON")


def decode_document(raw: str, *, max_bytes: int) -> dict[str, object]:
    """Decode exactly one inner JSON object, with bounded size/depth and strict keys."""
    if not 1 <= max_bytes <= MAX_DOCUMENT_BYTES:
        raise ValueError("Document allowance exceeds the tested token bound")
    try:
        if len(raw.encode("utf-8")) > max_bytes:
            raise ValueError("The provider envelope exceeds its byte allowance")
        outer: object = json.loads(raw, object_pairs_hook=_object, parse_constant=_constant)
        envelope = DocumentEnvelope.model_validate(outer)
        if len(envelope.document_json.encode("utf-8")) > max_bytes:
            raise ValueError("The inner document exceeds its byte allowance")
        value: object = json.loads(envelope.document_json, object_pairs_hook=_object, parse_constant=_constant)
        if not isinstance(value, dict):
            raise ValueError("The inner document must be an object")
        pending: list[tuple[object, int]] = [(value, 0)]
        while pending:
            item, depth = pending.pop()
            if depth > 64:
                raise ValueError("The inner document exceeds its nesting allowance")
            if isinstance(item, float) and not math.isfinite(item):
                raise ValueError("Overflow is not a finite JSON number")
            if isinstance(item, dict):
                pending.extend((child, depth+1) for child in cast(dict[str, object], item).values())
            elif isinstance(item, list):
                pending.extend((child, depth+1) for child in cast(list[object], item))
        return cast(dict[str, object], value)
    except (ValueError, TypeError, RecursionError, ValidationError, UnicodeError):
        raise ModelBackendError("Claude returned an invalid json-document-1 envelope or inner document") from None
