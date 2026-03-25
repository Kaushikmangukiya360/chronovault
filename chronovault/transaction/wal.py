"""Encrypted write-ahead-log management for transaction durability."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from chronovault.exceptions import TransactionConflictError
from chronovault.storage.store import JsonStore
from chronovault.utils import now_epoch, now_iso, uuid4_str


class WriteAheadLog:
    """Manage encrypted WAL entries for one tenant."""

    def __init__(self, store: JsonStore, wal_path: Path, org_id: str, tenant_token: str) -> None:
        self.store = store
        self.wal_path = wal_path
        self.org_id = org_id
        self.tenant_token = tenant_token

    def _read_payload(self) -> dict[str, Any]:
        payload = self.store.read_encrypted_json(
            file_path=self.wal_path,
            tenant_token=self.tenant_token,
            org_id=self.org_id,
        )
        entries = payload.get("entries")
        if not isinstance(entries, list):
            payload["entries"] = []
        return payload

    def _write_payload(self, payload: dict[str, Any]) -> None:
        self.store.write_encrypted_json(
            file_path=self.wal_path,
            payload=payload,
            tenant_token=self.tenant_token,
            org_id=self.org_id,
            timestamp=now_epoch(),
            purpose="wal",
        )

    def begin(self) -> str:
        """Create a new pending transaction in WAL and return tx_id."""
        payload = self._read_payload()
        if any(entry.get("status") == "pending" for entry in payload.get("entries", [])):
            raise TransactionConflictError("another transaction is already pending")
        tx_id = uuid4_str()
        payload["entries"].append(
            {
                "tx_id": tx_id,
                "status": "pending",
                "created_at": now_iso(),
                "updated_at": now_iso(),
                "operations": [],
            }
        )
        self._write_payload(payload)
        return tx_id

    def append_operation(self, tx_id: str, operation: dict[str, Any]) -> None:
        """Append one operation to a pending WAL transaction entry."""
        payload = self._read_payload()
        for entry in payload["entries"]:
            if entry.get("tx_id") == tx_id:
                ops = entry.get("operations", [])
                if not isinstance(ops, list):
                    ops = []
                ops.append(dict(operation))
                entry["operations"] = ops
                entry["updated_at"] = now_iso()
                break
        self._write_payload(payload)

    def set_status(self, tx_id: str, status: str) -> None:
        """Set transaction status to committed or rolled_back."""
        payload = self._read_payload()
        for entry in payload["entries"]:
            if entry.get("tx_id") == tx_id:
                entry["status"] = status
                entry["updated_at"] = now_iso()
                break
        self._write_payload(payload)

    def get_operations(self, tx_id: str) -> list[dict[str, Any]]:
        """Return operations for one transaction id."""
        payload = self._read_payload()
        for entry in payload["entries"]:
            if entry.get("tx_id") == tx_id:
                ops = entry.get("operations", [])
                return [dict(op) for op in ops if isinstance(op, dict)]
        return []

    def pending(self) -> list[dict[str, Any]]:
        """Return all pending transaction entries."""
        payload = self._read_payload()
        result: list[dict[str, Any]] = []
        for entry in payload.get("entries", []):
            if entry.get("status") == "pending":
                result.append(dict(entry))
        return result

    def recover_pending(self) -> int:
        """Mark all stale pending transactions as rolled back and return count."""
        payload = self._read_payload()
        recovered = 0
        for entry in payload.get("entries", []):
            if entry.get("status") == "pending":
                entry["status"] = "rolled_back"
                entry["updated_at"] = now_iso()
                recovered += 1
        if recovered:
            self._write_payload(payload)
        return recovered
