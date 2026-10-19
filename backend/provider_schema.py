"""Translate application schemas without weakening application validation."""

from typing import cast


def openai_schema(schema: dict[str, object]) -> dict[str, object]:
    """Copy a schema, omitting URI format unsupported by structured outputs.

    Pydantic HttpUrl validation still runs on every returned lesson. Supported
    formats are listed at developers.openai.com/api/docs/guides/structured-outputs.
    Never mutate the shared application schema or relax additionalProperties.
    """

    def convert(value: object) -> object:
        if isinstance(value, dict):
            mapping = cast(dict[str, object], value)
            return {
                key: convert(item) for key, item in mapping.items() if not (key == "format" and item == "uri")
            }
        if isinstance(value, list):
            return [convert(item) for item in cast(list[object], value)]
        return value

    return cast(dict[str, object], convert(schema))
