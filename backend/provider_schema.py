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
                key: convert(item)
                for key, item in mapping.items()
                if key != "default" and not (key == "format" and item == "uri")
            }
            properties = mapping.get("properties")
            if mapping.get("type") == "object" and isinstance(properties, dict):
                converted["required"] = list(properties)
            return converted
        if isinstance(value, list):
            return [convert(item) for item in cast(list[object], value)]
        return value

    return cast(dict[str, object], convert(schema))


def anthropic_schema(schema: dict[str, object]) -> dict[str, object]:
    """Translate Claude's supported subset; domain validation remains mandatory.

    Numeric/string/array bounds move into descriptions, as Anthropic's SDK does.
    The returned JSON must still pass the original Pydantic contract and quality
    gates. Objects remain closed and all properties are required to keep the
    compiled grammar within Claude's documented optional-property limit.
    """
    bounds = frozenset({
        "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
        "minLength", "maxLength", "minItems", "maxItems", "uniqueItems",
    })

    def convert(value: object) -> object:
        if isinstance(value, list):
            return [convert(item) for item in cast(list[object], value)]
        if not isinstance(value, dict):
            return value
        mapping = cast(dict[str, object], value)
        if any(key in mapping for key in ("prefixItems", "$dynamicRef", "not", "if", "then", "else")):
            raise ValueError("Schema requires an unsupported Claude grammar feature")
        if "$ref" in mapping and not str(mapping["$ref"]).startswith("#/"):
            raise ValueError("Claude authoring permits only local schema references")
        # properties/$defs are maps of schema names, not themselves schemas.
        converted = {
            key: (
                {name: convert(item) for name, item in cast(dict[str, object], value).items()}
                if key in ("properties", "$defs", "definitions") and isinstance(value, dict)
                else convert(value)
            )
            for key, value in mapping.items() if key not in bounds and key != "default"
        }
        limits = {key: value for key, value in mapping.items() if key in bounds}
        if limits:
            converted["description"] = (
                str(mapping.get("description", "")) + " Domain constraints: " + str(limits)
            ).strip()
        if mapping.get("type") == "object":
            if mapping.get("additionalProperties", False) is not False:
                raise ValueError("Claude authoring requires closed object schemas")
            converted["additionalProperties"] = False
            properties = mapping.get("properties", {})
            if not isinstance(properties, dict):
                raise ValueError("Claude object properties must be an explicit mapping")
            converted["required"] = list(properties)
        return converted

    return cast(dict[str, object], convert(schema))
