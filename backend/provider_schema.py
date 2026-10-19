"""Translate application schemas without weakening application validation."""

from typing import cast


def openai_schema(schema: dict[str, object]) -> dict[str, object]:
    """Copy a strict schema with required fields and no URI format or defaults.

    Pydantic HttpUrl validation still runs on every returned lesson. Supported
    formats are listed at developers.openai.com/api/docs/guides/structured-outputs.
    Never mutate the shared application schema or relax additionalProperties.
    """

    def convert(value: object) -> object:
        if isinstance(value, dict):
            mapping = cast(dict[str, object], value)
            converted = {
                key: convert(item) for key, item in mapping.items() if key != "default" and not (key == "format" and item == "uri")
            }
            properties = mapping.get("properties")
            if mapping.get("type") == "object" and isinstance(properties, dict):
                converted["required"] = list(properties)
            return converted
        if isinstance(value, list):
            return [convert(item) for item in cast(list[object], value)]
        return value

    return cast(dict[str, object], convert(schema))
