"""Immutable encrypted audit logger with chain-hash integrity."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from filelock import FileLock
from filelock import Timeout

from chronovault.exceptions import AuditIntegrityError
from chronovault.storage.store import JsonStore
from chronovault.utils import now_epoch, now_iso, uuid4_str


class AuditLogger:
    """Append-only tenant audit log protected by hash chaining."""

    def __init__(self, store: JsonStore, file_path: Path, org_id: str, tenant_token: str) -> None:
        """Initialize audit logger for tenant and token context."""
        self.store = store
        self.file_path = file_path
        self.org_id = org_id
        self.tenant_token = tenant_token
        self._append_lock = FileLock(str(self.file_path) + ".append.lock")

    def _read(self) -> list[dict[str, Any]]:
        payload = self.store.read_encrypted_json(
            file_path=self.file_path,
            tenant_token=self.tenant_token,
            org_id=self.org_id,
        )
        entries = payload.get("entries", [])
        if not isinstance(entries, list):
            return []
        return [e for e in entries if isinstance(e, dict)]

    def _write(self, entries: list[dict[str, Any]]) -> None:
        self.store.write_encrypted_json(
            file_path=self.file_path,
            payload={"entries": entries},
            tenant_token=self.tenant_token,
            org_id=self.org_id,
            timestamp=now_epoch(),
            purpose="audit",
        )

    @staticmethod
    def _entry_hash(entry: dict[str, Any]) -> str:
        base = {
            "event_id": entry.get("event_id"),
            "event": entry.get("event"),
            "tenant_id": entry.get("tenant_id"),
            "actor": entry.get("actor"),
            "collection": entry.get("collection"),
            "record_id": entry.get("record_id"),
            "ip": entry.get("ip"),
            "timestamp": entry.get("timestamp"),
            "key_epoch": entry.get("key_epoch"),
            "result": entry.get("result"),
            "error": entry.get("error"),
            "prev_hash": entry.get("prev_hash"),
        }
        encoded = json.dumps(base, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def append(
        self,
        event: str,
        actor: str,
        collection: str | None,
        record_id: str | None,
        ip: str,
        result: str,
        error: str | None = None,
    ) -> None:
        """Append one immutable audit event with chained integrity hash."""
        try:
            with self._append_lock.acquire(timeout=self.store.lock_timeout):
                entries = self._read()
                prev_hash = entries[-1].get("chain_hash") if entries else "0" * 64

                entry = {
                    "event_id": uuid4_str(),
                    "event": event,
                    "tenant_id": self.org_id,
                    "actor": actor,
                    "collection": collection,
                    "record_id": record_id,
                    "ip": ip,
                    "timestamp": now_iso(),
                    "key_epoch": now_epoch(),
                    "result": result,
                    "error": error,
                    "prev_hash": prev_hash,
                }
                entry["chain_hash"] = self._entry_hash(entry)
                entries.append(entry)
                self._write(entries)
        except Timeout as exc:
            raise AuditIntegrityError("audit append lock timeout") from exc

    def tail(self, n: int = 100) -> list[dict[str, Any]]:
        """Return the most recent N audit entries."""
        return self._read()[-n:]

    def filter(self, event: str | None = None, collection: str | None = None) -> list[dict[str, Any]]:
        """Return audit entries matching optional event and collection filters."""
        entries = self._read()
        if event is not None:
            entries = [e for e in entries if e.get("event") == event]
        if collection is not None:
            entries = [e for e in entries if e.get("collection") == collection]
        return entries

    def verify_integrity(self) -> bool:
        """Verify full chain-hash integrity for audit entries."""
        entries = self._read()
        prev_hash = "0" * 64
        for entry in entries:
            if entry.get("prev_hash") != prev_hash:
                raise AuditIntegrityError("audit chain previous hash mismatch")
            expected = self._entry_hash(entry)
            if entry.get("chain_hash") != expected:
                raise AuditIntegrityError("audit chain hash mismatch")
            prev_hash = str(entry.get("chain_hash"))
        return True

    def export(self, output: str, encrypted: bool = False) -> None:
        """Export audit entries to a JSON file path.

        By default this exports plaintext JSON for external review. Set
        encrypted=True to write an encrypted envelope instead.
        """
        entries = self._read()
        if encrypted:
            self.store.write_encrypted_json(
                file_path=Path(output),
                payload={"entries": entries},
                tenant_token=self.tenant_token,
                org_id=self.org_id,
                timestamp=now_epoch(),
                purpose="audit_export",
            )
            return
        with open(output, "w", encoding="utf-8") as fh:
            json.dump({"entries": entries}, fh, indent=2, ensure_ascii=True)
