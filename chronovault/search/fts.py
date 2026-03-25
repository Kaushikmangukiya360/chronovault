"""Encrypted full-text search index for collections."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from chronovault.storage.store import JsonStore
from chronovault.utils import now_epoch

_STOPWORDS = {
    "a",
    "an",
    "and",
    "the",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "is",
    "are",
}


class FullTextIndex:
    """Maintain encrypted inverted index of hashed tokens to record IDs."""

    def __init__(self, store: JsonStore, file_path: Path, org_id: str, tenant_token: str) -> None:
        self.store = store
        self.file_path = file_path
        self.org_id = org_id
        self.tenant_token = tenant_token

    def _read_payload(self) -> dict[str, Any]:
        payload = self.store.read_encrypted_json(
            file_path=self.file_path,
            tenant_token=self.tenant_token,
            org_id=self.org_id,
        )
        if not isinstance(payload.get("tokens"), dict):
            payload["tokens"] = {}
        if not isinstance(payload.get("fields"), list):
            payload["fields"] = []
        return payload

    def _write_payload(self, payload: dict[str, Any]) -> None:
        self.store.write_encrypted_json(
            file_path=self.file_path,
            payload=payload,
            tenant_token=self.tenant_token,
            org_id=self.org_id,
            timestamp=now_epoch(),
            purpose="fts",
        )

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _tokenize(self, value: str) -> list[str]:
        raw = re.findall(r"[a-z0-9]+", value.lower())
        return [t for t in raw if t and t not in _STOPWORDS]

    def _extract(self, record: dict[str, Any], field: str) -> Any:
        current: Any = record
        for part in field.split("."):
            if not isinstance(current, dict):
                return None
            current = current.get(part)
        return current

    def _tokens_for_record(self, record: dict[str, Any], fields: list[str]) -> set[str]:
        tokens: set[str] = set()
        for field in fields:
            value = self._extract(record, field)
            if isinstance(value, str):
                tokens.update(self._tokenize(value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        tokens.update(self._tokenize(item))
        return tokens

    def rebuild(self, records: list[dict[str, Any]], fields: list[str]) -> None:
        """Rebuild full-text index from records and configured fields."""
        inverted: dict[str, list[str]] = {}
        for record in records:
            rid = str(record.get("_id", ""))
            if not rid:
                continue
            hashed_terms = {self._hash_token(t) for t in self._tokens_for_record(record, fields)}
            for token_hash in hashed_terms:
                inverted.setdefault(token_hash, []).append(rid)

        payload = {
            "enabled": bool(fields),
            "fields": list(fields),
            "tokens": inverted,
        }
        self._write_payload(payload)

    def disable(self) -> None:
        """Disable and clear full-text index."""
        self._write_payload({"enabled": False, "fields": [], "tokens": {}})

    def search_scores(self, query_text: str) -> dict[str, float]:
        """Return record-id to score map for query text."""
        payload = self._read_payload()
        if not payload.get("enabled"):
            return {}

        terms = self._tokenize(query_text)
        if not terms:
            return {}

        counts: dict[str, int] = {}
        tokens = payload.get("tokens", {})
        for term in terms:
            term_hash = self._hash_token(term)
            ids = tokens.get(term_hash, [])
            if not isinstance(ids, list):
                continue
            for rid in ids:
                rid = str(rid)
                counts[rid] = counts.get(rid, 0) + 1

        total = len(terms)
        return {rid: hit / total for rid, hit in counts.items()}
