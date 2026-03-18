"""Query operator evaluation with nested-field support."""

from __future__ import annotations

import re
from typing import Any

from chronovault.exceptions import QueryError


TYPE_MAP = {
    "string": str,
    "str": str,
    "integer": int,
    "int": int,
    "float": float,
    "number": (int, float),
    "bool": bool,
    "boolean": bool,
    "list": list,
    "array": list,
    "dict": dict,
    "object": dict,
    "none": type(None),
    "null": type(None),
}


def get_nested_value(document: dict[str, Any], path: str) -> tuple[bool, Any]:
    """Return (exists, value) for dotted path from nested dict documents."""
    current: Any = document
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def _op_eq(record_value: Any, operand: Any) -> bool:
    return record_value == operand


def _op_ne(record_value: Any, operand: Any) -> bool:
    return record_value != operand


def _op_gt(record_value: Any, operand: Any) -> bool:
    return record_value is not None and record_value > operand


def _op_gte(record_value: Any, operand: Any) -> bool:
    return record_value is not None and record_value >= operand


def _op_lt(record_value: Any, operand: Any) -> bool:
    return record_value is not None and record_value < operand


def _op_lte(record_value: Any, operand: Any) -> bool:
    return record_value is not None and record_value <= operand


def _op_in(record_value: Any, operand: Any) -> bool:
    if not isinstance(operand, list):
        raise QueryError("$in requires a list operand")
    return record_value in operand


def _op_nin(record_value: Any, operand: Any) -> bool:
    if not isinstance(operand, list):
        raise QueryError("$nin requires a list operand")
    return record_value not in operand


def _op_exists(field_exists: bool, operand: Any) -> bool:
    return field_exists is bool(operand)


def _op_regex(record_value: Any, operand: Any) -> bool:
    if operand is None:
        return False
    return re.search(str(operand), str(record_value)) is not None


def _op_all(record_value: Any, operand: Any) -> bool:
    if not isinstance(record_value, list) or not isinstance(operand, list):
        return False
    return all(item in record_value for item in operand)


def _op_size(record_value: Any, operand: Any) -> bool:
    if not isinstance(record_value, list):
        return False
    return len(record_value) == int(operand)


def _op_type(record_value: Any, operand: Any) -> bool:
    key = str(operand).lower()
    expected_type = TYPE_MAP.get(key)
    if expected_type is None:
        raise QueryError("unsupported $type operand")
    return isinstance(record_value, expected_type)


FIELD_OPERATORS = {
    "$eq": _op_eq,
    "$ne": _op_ne,
    "$gt": _op_gt,
    "$gte": _op_gte,
    "$lt": _op_lt,
    "$lte": _op_lte,
    "$in": _op_in,
    "$nin": _op_nin,
    "$regex": _op_regex,
    "$all": _op_all,
    "$size": _op_size,
    "$type": _op_type,
}


def _match_field(record: dict[str, Any], field: str, expression: Any) -> bool:
    exists, value = get_nested_value(record, field)

    if not isinstance(expression, dict):
        return _op_eq(value, expression) if exists else False

    for op, operand in expression.items():
        if op == "$exists":
            if not _op_exists(exists, operand):
                return False
            continue

        if op == "$not":
            if _match_field(record, field, operand):
                return False
            continue

        fn = FIELD_OPERATORS.get(op)
        if fn is None:
            raise QueryError(f"unsupported operator: {op}")
        if not exists:
            return False
        if not fn(value, operand):
            return False

    return True


def match_record(record: dict[str, Any], filter_query: dict[str, Any]) -> bool:
    """Evaluate a filter query with logical and field operators."""
    if not filter_query:
        return True

    for key, expression in filter_query.items():
        if key == "$or":
            if not isinstance(expression, list):
                raise QueryError("$or expects list of subqueries")
            if not any(match_record(record, sub) for sub in expression):
                return False
            continue

        if key == "$and":
            if not isinstance(expression, list):
                raise QueryError("$and expects list of subqueries")
            if not all(match_record(record, sub) for sub in expression):
                return False
            continue

        if key == "$not":
            if not isinstance(expression, dict):
                raise QueryError("$not expects subquery object")
            if match_record(record, expression):
                return False
            continue

        if not _match_field(record, key, expression):
            return False

    return True
