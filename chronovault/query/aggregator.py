"""Aggregation pipeline execution for collection records."""

from __future__ import annotations

from typing import Any

from chronovault.query.engine import QueryEngine


class Aggregator:
    """Execute Mongo-style aggregation stages over in-memory records."""

    def __init__(self) -> None:
        self.engine = QueryEngine()

    def run(self, records: list[dict[str, Any]], pipeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Run aggregation pipeline over records and return transformed output."""
        out = [dict(r) for r in records]
        for stage in pipeline:
            if "$match" in stage:
                out = [r for r in out if self.engine.match(r, stage["$match"])]
            elif "$group" in stage:
                out = self._group(out, stage["$group"])
            elif "$sort" in stage:
                spec = stage["$sort"]
                sort_fields = list(spec.items())
                for field, direction in reversed(sort_fields):
                    out.sort(key=lambda r: self._sort_key(self._extract(r, field)), reverse=int(direction) < 0)
            elif "$limit" in stage:
                out = out[: int(stage["$limit"])]
            elif "$skip" in stage:
                out = out[int(stage["$skip"]) :]
            elif "$project" in stage:
                out = [self.engine._project_record(r, stage["$project"]) for r in out]
            elif "$unwind" in stage:
                out = self._unwind(out, stage["$unwind"])
            elif "$count" in stage:
                out = [{str(stage["$count"]): len(out)}]
            elif "$addFields" in stage:
                for row in out:
                    for k, v in stage["$addFields"].items():
                        row[k] = self._resolve_expression(row, v)
            else:
                raise ValueError("unsupported aggregation stage")
        return out

    def _extract(self, row: dict[str, Any], expr: str) -> Any:
        if expr.startswith("$"):
            expr = expr[1:]
        current: Any = row
        for part in expr.split("."):
            if not isinstance(current, dict):
                return None
            current = current.get(part)
        return current

    def _sort_key(self, value: Any) -> tuple[int, Any]:
        if value is None:
            return (1, "")
        if isinstance(value, (int, float, bool, str)):
            return (0, value)
        return (0, str(value))

    def _resolve_expression(self, row: dict[str, Any], expr: Any) -> Any:
        if isinstance(expr, str) and expr.startswith("$"):
            return self._extract(row, expr)
        return expr

    def _unwind(self, rows: list[dict[str, Any]], path_expr: str) -> list[dict[str, Any]]:
        field = path_expr[1:] if path_expr.startswith("$") else path_expr
        out: list[dict[str, Any]] = []
        for row in rows:
            value = self._extract(row, field)
            if isinstance(value, list):
                for item in value:
                    copy = dict(row)
                    copy[field] = item
                    out.append(copy)
            else:
                out.append(dict(row))
        return out

    def _group(self, rows: list[dict[str, Any]], spec: dict[str, Any]) -> list[dict[str, Any]]:
        key_expr = spec.get("_id")
        groups: dict[Any, list[dict[str, Any]]] = {}
        for row in rows:
            key = self._resolve_expression(row, key_expr)
            groups.setdefault(key, []).append(row)

        output: list[dict[str, Any]] = []
        for key, members in groups.items():
            agg_row: dict[str, Any] = {"_id": key}
            for field, acc_spec in spec.items():
                if field == "_id":
                    continue
                op, source = next(iter(acc_spec.items()))
                values = [self._resolve_expression(m, source) for m in members]

                if op == "$sum":
                    agg_row[field] = sum((v if isinstance(v, (int, float)) else 0) for v in values)
                elif op == "$avg":
                    nums = [v for v in values if isinstance(v, (int, float))]
                    agg_row[field] = (sum(nums) / len(nums)) if nums else 0
                elif op == "$min":
                    agg_row[field] = min(values) if values else None
                elif op == "$max":
                    agg_row[field] = max(values) if values else None
                elif op == "$first":
                    agg_row[field] = values[0] if values else None
                elif op == "$last":
                    agg_row[field] = values[-1] if values else None
                elif op == "$push":
                    agg_row[field] = values
                else:
                    raise ValueError("unsupported accumulator")
            output.append(agg_row)
        return output
