"""Record index manager for ChronoVault collections."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from chronovault.exceptions import IndexAlreadyExistsError, IndexNotFoundError, UniqueConstraintError
from chronovault.storage.store import JsonStore
from chronovault.utils import now_epoch


class IndexManager:
    """Manage encrypted record index files for a collection."""

    def __init__(self, store: JsonStore, file_path: Path, org_id: str) -> None:
        """Initialize index manager with backing store and file path."""
        self.store = store
        self.file_path = file_path
        self.org_id = org_id

    @staticmethod
    def checksum(record: dict[str, Any]) -> str:
        """Return SHA-256 checksum for stable canonical record JSON."""
        payload = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _hash_value(value: Any) -> str:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _nested_value(record: dict[str, Any], path: str) -> tuple[bool, Any]:
        current: Any = record
        for part in path.split("."):
            if not isinstance(current, dict) or part not in current:
                return False, None
            current = current[part]
        return True, current

    def _read_payload(self, tenant_token: str) -> dict[str, Any]:
        payload = self.store.read_encrypted_json(
            file_path=self.file_path,
            tenant_token=tenant_token,
            org_id=self.org_id,
        )
        payload.setdefault("records", {})
        payload.setdefault("indexes", {})
        return payload

    def _write_payload(self, tenant_token: str, payload: dict[str, Any]) -> None:
        self.store.write_encrypted_json(
            file_path=self.file_path,
            payload=payload,
            tenant_token=tenant_token,
            org_id=self.org_id,
            timestamp=now_epoch(),
            purpose="index",
        )

    def read(self, tenant_token: str) -> dict[str, str]:
        """Read index map of record_id to checksum."""
        payload = self._read_payload(tenant_token)
        records = payload.get("records", {})
        if not isinstance(records, dict):
            return {}
        return {str(k): str(v) for k, v in records.items()}

    def create_index(self, tenant_token: str, fields: str | list[str], unique: bool = False) -> str:
        """Create index definition for one field or compound field list."""
        payload = self._read_payload(tenant_token)
        if isinstance(fields, list):
            name = ",".join(fields)
            index_fields = [str(f) for f in fields]
        else:
            name = str(fields)
            index_fields = [name]

        if name in payload["indexes"]:
            raise IndexAlreadyExistsError("index already exists")

        payload["indexes"][name] = {
            "type": "hash",
            "unique": bool(unique),
            "fields": index_fields,
            "entries": {},
        }
        self._write_payload(tenant_token, payload)
        return name

    def drop_index(self, tenant_token: str, name: str) -> None:
        """Drop an existing index definition by name."""
        payload = self._read_payload(tenant_token)
        if name not in payload["indexes"]:
            raise IndexNotFoundError("index not found")
        payload["indexes"].pop(name)
        self._write_payload(tenant_token, payload)

    def list_indexes(self, tenant_token: str) -> dict[str, Any]:
        """Return index definition metadata for the collection."""
        payload = self._read_payload(tenant_token)
        return dict(payload.get("indexes", {}))

    def lookup(self, tenant_token: str, field: str, value: Any) -> list[str]:
        """Return candidate record IDs from index for exact-value lookup."""
        payload = self._read_payload(tenant_token)
        idx = payload.get("indexes", {}).get(field)
        if not idx:
            return []
        hashed = self._hash_value(value)
        entries = idx.get("entries", {})
        ids = entries.get(hashed, [])
        return [str(i) for i in ids]

    def write(self, tenant_token: str, timestamp: int, records: list[dict[str, Any]]) -> dict[str, str]:
        """Write full index for provided records and return index map."""
        payload = self._read_payload(tenant_token)
        index_map: dict[str, str] = {}
        for record in records:
            rid = str(record.get("_id", ""))
            if not rid:
                continue
            index_map[rid] = self.checksum(record)

        definitions = payload.get("indexes", {})
        for name, spec in definitions.items():
            fields = spec.get("fields", [name])
            unique = bool(spec.get("unique", False))
            rebuilt: dict[str, list[str]] = {}
            for record in records:
                rid = str(record.get("_id", ""))
                if not rid:
                    continue

                values: list[Any] = []
                include = True
                for field in fields:
                    exists, val = self._nested_value(record, field)
                    if not exists:
                        include = False
                        break
                    values.append(val)
                if not include:
                    continue

                encoded = values[0] if len(values) == 1 else values
                h = self._hash_value(encoded)
                rebuilt.setdefault(h, []).append(rid)
                if unique and len(rebuilt[h]) > 1:
                    raise UniqueConstraintError("unique index violation")

            spec["entries"] = rebuilt

        payload["records"] = index_map
        payload["indexes"] = definitions
        self.store.write_encrypted_json(
            file_path=self.file_path,
            payload=payload,
            tenant_token=tenant_token,
            org_id=self.org_id,
            timestamp=timestamp,
            purpose="index",
        )
        return index_map
