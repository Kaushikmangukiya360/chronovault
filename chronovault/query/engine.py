"""Query execution pipeline for in-memory decrypted records."""

from __future__ import annotations

from typing import Any

from chronovault.query.operators import get_nested_value, match_record


class QueryEngine:
    """Execute filter, sorting, pagination, and projection over records."""

    def match(self, record: dict[str, Any], filter: dict[str, Any]) -> bool:
        """Return True when one record matches the provided filter."""
        return match_record(record, filter)

    def execute(
        self,
        records: list[dict[str, Any]],
        filter: dict[str, Any],
        sort_field: str | list[tuple[str, int]] | None = None,
        sort_dir: int = 1,
        limit: int | None = None,
        skip: int = 0,
        projection: dict[str, int] | None = None,
    ) -> list[dict[str, Any]]:
        """Run filter -> sort -> skip -> limit -> project pipeline."""
        result = [dict(r) for r in records if self.match(r, filter)]

        sort_spec: list[tuple[str, int]] = []
        if isinstance(sort_field, list):
            sort_spec = [(str(field), 1 if int(direction) >= 0 else -1) for field, direction in sort_field]
        elif isinstance(sort_field, str):
            sort_spec = [(sort_field, 1 if int(sort_dir) >= 0 else -1)]

        for field, direction in reversed(sort_spec):
            result.sort(
                key=lambda rec: get_nested_value(rec, field)[1],
                reverse=direction < 0,
            )

        if skip > 0:
            result = result[skip:]
        if limit is not None:
            result = result[:limit]

        if projection is not None:
            result = [self._project_record(record, projection) for record in result]

        return result

    def _project_record(self, record: dict[str, Any], projection: dict[str, int]) -> dict[str, Any]:
        include_keys = [k for k, v in projection.items() if int(v) == 1]
        exclude_keys = [k for k, v in projection.items() if int(v) == 0]

        if include_keys:
            projected: dict[str, Any] = {}
            for path in include_keys:
                exists, value = get_nested_value(record, path)
                if exists:
                    self._assign_dotted(projected, path, value)
            if projection.get("_id", 1) == 1 and "_id" in record:
                projected["_id"] = record["_id"]
            return projected

        projected = dict(record)
        for path in exclude_keys:
            self._remove_dotted(projected, path)
        return projected

    def _assign_dotted(self, root: dict[str, Any], path: str, value: Any) -> None:
        parts = path.split(".")
        current = root
        for part in parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value

    def _remove_dotted(self, root: dict[str, Any], path: str) -> None:
        parts = path.split(".")
        current: Any = root
        for part in parts[:-1]:
            if not isinstance(current, dict) or part not in current:
                return
            current = current[part]
        if isinstance(current, dict):
            current.pop(parts[-1], None)
