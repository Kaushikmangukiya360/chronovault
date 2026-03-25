"""ORM field descriptors for ChronoVault models."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID


class BaseField:
    """Base descriptor for ORM fields."""

    def __init__(self, required: bool = False, default: Any = None) -> None:
        self.required = required
        self.default = default
        self.name = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        if instance is None:
            return self
        if self.name in instance._data:
            return instance._data[self.name]
        return self.default() if callable(self.default) else self.default

    def __set__(self, instance: Any, value: Any) -> None:
        self.validate(value)
        instance._data[self.name] = value

    def validate(self, value: Any) -> None:
        _ = value


class StringField(BaseField):
    def __init__(self, required: bool = False, default: Any = None, max_length: int | None = None, enum: list[str] | None = None) -> None:
        super().__init__(required=required, default=default)
        self.max_length = max_length
        self.enum = enum or []

    def validate(self, value: Any) -> None:
        if value is None:
            return
        if not isinstance(value, str):
            raise TypeError("expected string")
        if self.max_length is not None and len(value) > self.max_length:
            raise ValueError("string too long")
        if self.enum and value not in self.enum:
            raise ValueError("value not in enum")


class IntField(BaseField):
    def __init__(self, required: bool = False, default: Any = None, minimum: int | None = None, maximum: int | None = None) -> None:
        super().__init__(required=required, default=default)
        self.minimum = minimum
        self.maximum = maximum

    def validate(self, value: Any) -> None:
        if value is None:
            return
        if not isinstance(value, int):
            raise TypeError("expected int")
        if self.minimum is not None and value < self.minimum:
            raise ValueError("value below minimum")
        if self.maximum is not None and value > self.maximum:
            raise ValueError("value above maximum")


class FloatField(BaseField):
    def validate(self, value: Any) -> None:
        if value is None:
            return
        if not isinstance(value, (int, float)):
            raise TypeError("expected float")


class BoolField(BaseField):
    def validate(self, value: Any) -> None:
        if value is None:
            return
        if not isinstance(value, bool):
            raise TypeError("expected bool")


class EmailField(StringField):
    def validate(self, value: Any) -> None:
        super().validate(value)
        if value is None:
            return
        if "@" not in value:
            raise ValueError("invalid email")


class DateTimeField(BaseField):
    def validate(self, value: Any) -> None:
        if value is None:
            return
        if isinstance(value, datetime):
            return
        if isinstance(value, str):
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return
        raise TypeError("expected datetime or ISO string")


class UUIDField(BaseField):
    def validate(self, value: Any) -> None:
        if value is None:
            return
        if isinstance(value, str):
            UUID(value)
            return
        raise TypeError("expected uuid string")


class ListField(BaseField):
    def __init__(self, item_field: BaseField, required: bool = False, default: Any = None) -> None:
        super().__init__(required=required, default=default if default is not None else list)
        self.item_field = item_field

    def validate(self, value: Any) -> None:
        if value is None:
            return
        if not isinstance(value, list):
            raise TypeError("expected list")
        for item in value:
            self.item_field.validate(item)


class DictField(BaseField):
    def validate(self, value: Any) -> None:
        if value is None:
            return
        if not isinstance(value, dict):
            raise TypeError("expected dict")
