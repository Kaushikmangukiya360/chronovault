"""Transaction context manager with WAL-backed staged operations."""

from __future__ import annotations

from typing import Any

from chronovault.exceptions import TransactionError
from chronovault.transaction.wal import WriteAheadLog


class _TransactionCollectionFacade:
    """Collection facade used inside transaction contexts."""

    def __init__(self, tx: "TransactionContext", name: str) -> None:
        self.tx = tx
        self.name = name

    def insert(self, record: dict[str, Any]) -> None:
        self.tx._stage(self.name, "insert", {"record": dict(record)})

    def insert_many(self, documents: list[dict[str, Any]]) -> None:
        self.tx._stage(self.name, "insert_many", {"documents": [dict(d) for d in documents]})

    def update(self, query: dict[str, Any], updates: dict[str, Any]) -> None:
        self.tx._stage(self.name, "update", {"query": dict(query), "updates": dict(updates)})

    def update_many(self, query: dict[str, Any], updates: dict[str, Any]) -> None:
        self.update(query, updates)

    def delete(self, query: dict[str, Any]) -> None:
        self.tx._stage(self.name, "delete", {"query": dict(query)})

    def delete_many(self, query: dict[str, Any]) -> None:
        self.delete(query)

    def upsert(self, query: dict[str, Any], updates: dict[str, Any]) -> None:
        self.tx._stage(self.name, "upsert", {"query": dict(query), "updates": dict(updates)})


class TransactionContext:
    """Context manager that stages write operations and commits atomically by sequence."""

    def __init__(self, vault: Any, wal: WriteAheadLog) -> None:
        self.vault = vault
        self.wal = wal
        self.tx_id: str | None = None
        self._active = False

    def __enter__(self) -> "TransactionContext":
        self.tx_id = self.wal.begin()
        self._active = True
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        if exc is not None:
            self.rollback()
            return False
        self.commit()
        return False

    def __getattr__(self, name: str) -> _TransactionCollectionFacade:
        if name.startswith("_"):
            raise AttributeError(name)
        return _TransactionCollectionFacade(self, name)

    def _stage(self, collection: str, action: str, payload: dict[str, Any]) -> None:
        if not self._active or self.tx_id is None:
            raise TransactionError("transaction is not active")
        operation = {
            "collection": collection,
            "action": action,
            "payload": payload,
        }
        self.wal.append_operation(self.tx_id, operation)

    def commit(self) -> None:
        """Apply all staged operations in order and mark transaction committed."""
        if not self._active or self.tx_id is None:
            raise TransactionError("transaction is not active")

        operations = self.wal.get_operations(self.tx_id)
        try:
            for op in operations:
                collection_name = str(op.get("collection"))
                action = str(op.get("action"))
                payload = op.get("payload", {})
                coll = self.vault._collection(collection_name)

                if action == "insert":
                    coll.insert(payload.get("record", {}))
                elif action == "insert_many":
                    coll.insert_many(payload.get("documents", []))
                elif action == "update":
                    coll.update(payload.get("query", {}), payload.get("updates", {}))
                elif action == "delete":
                    coll.delete(payload.get("query", {}))
                elif action == "upsert":
                    coll.upsert(payload.get("query", {}), payload.get("updates", {}))
                else:
                    raise TransactionError("unsupported transaction action")
            self.wal.set_status(self.tx_id, "committed")
        except Exception as exc:  # noqa: BLE001
            self.wal.set_status(self.tx_id, "rolled_back")
            self._active = False
            raise TransactionError("transaction commit failed") from exc

        self._active = False

    def rollback(self) -> None:
        """Mark current transaction as rolled back."""
        if not self._active or self.tx_id is None:
            return
        self.wal.set_status(self.tx_id, "rolled_back")
        self._active = False


class TransactionManager:
    """Factory for transaction contexts."""

    def __init__(self, vault: Any, wal: WriteAheadLog) -> None:
        self.vault = vault
        self.wal = wal

    def start(self) -> TransactionContext:
        """Return a new transaction context."""
        return TransactionContext(vault=self.vault, wal=self.wal)
