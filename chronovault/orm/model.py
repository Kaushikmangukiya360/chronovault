"""Minimal ORM model layer for ChronoVault."""

from __future__ import annotations

from typing import Any

from chronovault.orm.fields import BaseField


class ModelMeta(type):
    """Collect field descriptors from model classes."""

    def __new__(mcls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> type:
        cls = super().__new__(mcls, name, bases, namespace)
        fields: dict[str, BaseField] = {}
        for base in reversed(bases):
            fields.update(getattr(base, "__fields__", {}))
        for k, v in namespace.items():
            if isinstance(v, BaseField):
                fields[k] = v
        cls.__fields__ = fields
        return cls


class Model(metaclass=ModelMeta):
    """Base model for collection-oriented persistence."""

    __collection__ = ""

    def __init__(self, **kwargs: Any) -> None:
        self._data: dict[str, Any] = {}
        self._id: str | None = kwargs.pop("_id", None)

        for name, field in self.__fields__.items():
            if name in kwargs:
                setattr(self, name, kwargs[name])
            else:
                default = field.default() if callable(field.default) else field.default
                if default is not None:
                    setattr(self, name, default)
                elif field.required:
                    raise ValueError(f"missing required field: {name}")

    @classmethod
    def _collection(cls, db: Any) -> Any:
        if not cls.__collection__:
            raise ValueError("__collection__ must be set")
        return getattr(db, cls.__collection__)

    def to_dict(self) -> dict[str, Any]:
        payload = dict(self._data)
        if self._id:
            payload["_id"] = self._id
        return payload

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "Model":
        data = {k: v for k, v in record.items() if not k.startswith("_")}
        obj = cls(_id=record.get("_id"), **data)
        obj._id = record.get("_id")
        return obj

    def save(self, db: Any) -> "Model":
        coll = self._collection(db)
        data = dict(self._data)
        if self._id:
            coll.update({"_id": self._id}, data)
            return self
        rid = coll.insert(data)
        self._id = rid
        return self

    def delete(self, db: Any) -> int:
        if not self._id:
            return 0
        coll = self._collection(db)
        return coll.delete({"_id": self._id})

    @classmethod
    def find(cls, db: Any, query: dict[str, Any]) -> list["Model"]:
        coll = cls._collection(db)
        return [cls.from_record(r) for r in coll.find(query).execute()]

    @classmethod
    def find_one(cls, db: Any, query: dict[str, Any]) -> "Model" | None:
        coll = cls._collection(db)
        row = coll.find_one(query)
        if row is None:
            return None
        return cls.from_record(row)
