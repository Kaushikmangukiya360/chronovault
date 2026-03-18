"""In-memory cross-collection join helpers."""

from __future__ import annotations

from typing import Any


def join_records(
    left: list[dict[str, Any]],
    right: list[dict[str, Any]],
    right_alias: str,
    on: str,
    foreign_key: str,
    join_type: str = "inner",
) -> list[dict[str, Any]]:
    """Join two record sets on key fields using inner/left/right semantics."""
    join_type = join_type.lower()
    right_index: dict[Any, list[dict[str, Any]]] = {}
    for row in right:
        key = row.get(foreign_key)
        right_index.setdefault(key, []).append(row)

    result: list[dict[str, Any]] = []
    matched_right_ids: set[int] = set()

    for lrow in left:
        key = lrow.get(on)
        matches = right_index.get(key, [])
        if matches:
            for rrow in matches:
                merged = dict(lrow)
                merged[right_alias] = dict(rrow)
                result.append(merged)
                matched_right_ids.add(id(rrow))
        elif join_type in {"left", "outer"}:
            merged = dict(lrow)
            merged[right_alias] = None
            result.append(merged)

    if join_type in {"right", "outer"}:
        for rrow in right:
            if id(rrow) in matched_right_ids:
                continue
            merged = {right_alias: dict(rrow)}
            result.append(merged)

    if join_type not in {"inner", "left", "right", "outer"}:
        raise ValueError("unsupported join type")
    if join_type == "inner":
        return [row for row in result if row.get(right_alias) is not None]
    return result
