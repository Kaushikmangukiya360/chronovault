"""Minimal JSON-schema validator for collection writes."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from uuid import UUID

from chronovault.exceptions import SchemaValidationError


class SchemaValidator:
    """Validate records against supported JSON schema keywords."""

    TYPE_MAP = {
        "object": dict,
        "string": str,
        "integer": int,
        "number": (int, float),
        "array": list,
        "boolean": bool,
    }

    def validate(self, record: dict[str, Any], schema: dict[str, Any]) -> None:
        """Validate one record and raise SchemaValidationError on first failure."""
        if not schema:
            return
        self._validate_node(record, schema, path="$")

    def _validate_node(self, value: Any, schema: dict[str, Any], path: str) -> None:
        stype = schema.get("type")
        if stype:
            expected = self.TYPE_MAP.get(stype)
            if expected is None or not isinstance(value, expected):
                raise SchemaValidationError(f"{path}: expected type {stype}")

        if isinstance(value, dict):
            required = schema.get("required", [])
            for field in required:
                if field not in value:
                    raise SchemaValidationError(f"{path}.{field}: required field missing")

            properties = schema.get("properties", {})
            additional = schema.get("additionalProperties", True)
            if additional is False:
                unknown = [k for k in value.keys() if k not in properties and not str(k).startswith("_")]
                if unknown:
                    raise SchemaValidationError(f"{path}.{unknown[0]}: additional property not allowed")

            for field, sub_schema in properties.items():
                if field in value:
                    self._validate_node(value[field], sub_schema, f"{path}.{field}")

        if isinstance(value, str):
            min_len = schema.get("minLength")
            max_len = schema.get("maxLength")
            pattern = schema.get("pattern")
            fmt = schema.get("format")
            enum = schema.get("enum")

            if min_len is not None and len(value) < int(min_len):
                raise SchemaValidationError(f"{path}: minLength violation")
            if max_len is not None and len(value) > int(max_len):
                raise SchemaValidationError(f"{path}: maxLength violation")
            if pattern is not None and re.search(str(pattern), value) is None:
                raise SchemaValidationError(f"{path}: pattern mismatch")
            if enum is not None and value not in enum:
                raise SchemaValidationError(f"{path}: enum violation")
            self._validate_format(value, fmt, path)

        if isinstance(value, (int, float)):
            minimum = schema.get("minimum")
            maximum = schema.get("maximum")
            enum = schema.get("enum")
            if minimum is not None and value < minimum:
                raise SchemaValidationError(f"{path}: below minimum")
            if maximum is not None and value > maximum:
                raise SchemaValidationError(f"{path}: above maximum")
            if enum is not None and value not in enum:
                raise SchemaValidationError(f"{path}: enum violation")

        if isinstance(value, list):
            items_schema = schema.get("items")
            if items_schema is not None:
                for idx, item in enumerate(value):
                    self._validate_node(item, items_schema, f"{path}[{idx}]")
            expected_size = schema.get("size")
            if expected_size is not None and len(value) != int(expected_size):
                raise SchemaValidationError(f"{path}: size mismatch")

    def _validate_format(self, value: str, fmt: Any, path: str) -> None:
        if fmt is None:
            return
        if fmt == "email":
            if re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value) is None:
                raise SchemaValidationError(f"{path}: invalid email format")
            return
        if fmt == "uuid":
            try:
                UUID(value)
            except Exception as exc:  # noqa: BLE001
                raise SchemaValidationError(f"{path}: invalid uuid format") from exc
            return
        if fmt == "date-time":
            try:
                datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError as exc:
                raise SchemaValidationError(f"{path}: invalid date-time format") from exc
