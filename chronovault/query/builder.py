"""Chainable query builder API for collection filtering and pagination."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from chronovault.query.engine import QueryEngine
from chronovault.query.join import join_records


class QueryBuilder:
    """Chainable query builder that executes against collection records."""

    def __init__(self, collection: Any) -> None:
        """Initialize a builder bound to one collection facade."""
        self.collection = collection
        self.engine = QueryEngine()
        self._filter: dict[str, Any] = {}
        self._find_one = False
        self._sort_field: str | list[tuple[str, int]] | None = None
        self._sort_dir = 1
        self._limit: int | None = None
        self._skip = 0
        self._projection: dict[str, int] | None = None
        self._joins: list[dict[str, str]] = []
        self._search_text: str | None = None

    def find(self, filter: dict[str, Any] | None = None) -> "QueryBuilder":
        """Set filter and return builder for chained calls."""
        self._find_one = False
        self._filter = filter or {}
        return self

    def find_one(self, filter: dict[str, Any] | None = None) -> "QueryBuilder":
        """Set filter for first matching record mode."""
        self._find_one = True
        self._filter = filter or {}
        self._limit = 1
        return self

    def sort(self, field: str | list[tuple[str, int]], direction: int = 1) -> "QueryBuilder":
        """Sort by one field or multiple (field, direction) tuples."""
        self._sort_field = field
        self._sort_dir = 1 if int(direction) >= 0 else -1
        return self

    def limit(self, n: int) -> "QueryBuilder":
        """Limit output rows to at most n records."""
        self._limit = max(0, int(n))
        return self

    def skip(self, n: int) -> "QueryBuilder":
        """Skip first n records after sorting."""
        self._skip = max(0, int(n))
        return self

    def project(self, fields: dict[str, int]) -> "QueryBuilder":
        """Apply include/exclude projection map."""
        self._projection = dict(fields)
        return self

    def join(
        self,
        collection: str,
        on: str,
        foreign_key: str,
        join_type: str = "inner",
    ) -> "QueryBuilder":
        """Join current results with another collection in memory."""
        self._joins.append(
            {
                "collection": collection,
                "on": on,
                "foreign_key": foreign_key,
                "join_type": join_type,
            }
        )
        return self

    def search(self, text: str) -> "QueryBuilder":
        """Apply in-memory keyword scoring filter to current result set."""
        self._search_text = text.strip()
        return self

    def count(self) -> int:
        """Return count for current filter query."""
        records = self.collection._raw_records()
        return len(self.engine.execute(records=records, filter=self._filter))

    def execute(self) -> list[dict[str, Any]]:
        """Execute query pipeline and return list of records."""
        records = self.collection._raw_records()
        result = self.engine.execute(
            records=records,
            filter=self._filter,
            sort_field=self._sort_field,
            sort_dir=self._sort_dir,
            limit=self._limit,
            skip=self._skip,
            projection=None,
        )

        if self._search_text:
            score_map = self.collection._fts_search(self._search_text)
            if score_map:
                scored: list[dict[str, Any]] = []
                for row in result:
                    rid = str(row.get("_id", ""))
                    score = score_map.get(rid)
                    if score is None:
                        continue
                    item = dict(row)
                    item["_score"] = score
                    scored.append(item)
                result = scored
            else:
                terms = [t for t in self._search_text.lower().split() if t]
                if terms:
                    scored = []
                    for row in result:
                        haystack = " ".join(str(v).lower() for v in row.values() if isinstance(v, (str, int, float)))
                        hits = sum(1 for t in terms if t in haystack)
                        if hits:
                            item = dict(row)
                            item["_score"] = hits / len(terms)
                            scored.append(item)
                    result = scored

        for spec in self._joins:
            foreign_collection = str(spec["collection"])
            foreign = self.collection.vault.safe_call(
                event="collection.read",
                collection=foreign_collection,
                fn=lambda: (
                    self.collection.vault._require(action="find", collection=foreign_collection),
                    self.collection.vault._collection(foreign_collection).find({}),
                )[1],
            )
            result = join_records(
                left=result,
                right=foreign,
                right_alias=foreign_collection,
                on=spec["on"],
                foreign_key=spec["foreign_key"],
                join_type=spec["join_type"],
            )

        if self._projection is not None:
            result = [self.engine._project_record(record, self._projection) for record in result]

        if self._find_one:
            return result[:1]
        return result

    def first(self) -> dict[str, Any] | None:
        """Return first matching record or None."""
        rows = self.find_one(self._filter).execute()
        return rows[0] if rows else None

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """Iterate lazily over executed query results."""
        for row in self.execute():
            yield row

    def __len__(self) -> int:
        """Return executed result length for compatibility with list-like usage."""
        return len(self.execute())

    def __getitem__(self, index: int) -> dict[str, Any]:
        """Return indexed item from executed results."""
        return self.execute()[index]
