"""Collection CRUD operations for encrypted JSON records."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any

from filelock import FileLock, Timeout

from chronovault.exceptions import VaultLockTimeoutError
from chronovault.search.fts import FullTextIndex
from chronovault.query.operators import match_record
from chronovault.schema.validator import SchemaValidator
from chronovault.storage.index import IndexManager
from chronovault.storage.shard import ShardManager
from chronovault.storage.store import JsonStore
from chronovault.utils import now_epoch, now_iso, uuid4_str


class Collection:
    """Handle encrypted CRUD operations for a single collection."""

    def __init__(
        self,
        store: JsonStore,
        tenant_root: Path,
        org_id: str,
        tenant_token: str,
        name: str,
    ) -> None:
        """Initialize collection with tenant scope and token context."""
        self.store = store
        self.tenant_root = tenant_root
        self.org_id = org_id
        self.tenant_token = tenant_token
        self.name = name

        self.collection_dir = tenant_root / "collections" / name
        self.data_path = self.collection_dir / "data_000.json"
        self.index_path = self.collection_dir / "index.json"
        self.fts_path = self.collection_dir / "fts.json"
        self.meta_path = self.collection_dir / "meta.json"
        self._rw_lock = FileLock(str(self.collection_dir / ".rw.lock"))
        self.shards = ShardManager(
            store=self.store,
            collection_dir=self.collection_dir,
            org_id=self.org_id,
            tenant_token=self.tenant_token,
        )

        self.index_manager = IndexManager(store=self.store, file_path=self.index_path, org_id=self.org_id)
        self.fts_index = FullTextIndex(
            store=self.store,
            file_path=self.fts_path,
            org_id=self.org_id,
            tenant_token=self.tenant_token,
        )
        self.schema_validator = SchemaValidator()

    def _read_meta(self) -> dict[str, Any]:
        return self.store.read_encrypted_json(
            file_path=self.meta_path,
            tenant_token=self.tenant_token,
            org_id=self.org_id,
        )

    def _schema(self) -> dict[str, Any] | None:
        meta = self._read_meta()
        schema = meta.get("schema")
        if isinstance(schema, dict):
            return schema
        return None

    def _read_records(self) -> list[dict[str, Any]]:
        return self.shards.read_all_records()

    def _write_all(self, records: list[dict[str, Any]]) -> None:
        ts = now_epoch()
        existing_meta = self._read_meta()
        shard_count, total_records = self.shards.write_records(records)
        index_map = self.index_manager.write(
            tenant_token=self.tenant_token,
            timestamp=ts,
            records=records,
        )
        self.store.write_encrypted_json(
            file_path=self.meta_path,
            payload={
                "collection": self.name,
                "record_count": total_records,
                "index_count": len(index_map),
                "shard_count": shard_count,
                "updated_at": now_iso(),
                "ts": ts,
                "schema": existing_meta.get("schema"),
                "fts_fields": existing_meta.get("fts_fields", []),
            },
            tenant_token=self.tenant_token,
            org_id=self.org_id,
            timestamp=ts,
            purpose="meta",
        )
        fts_fields = existing_meta.get("fts_fields", [])
        if isinstance(fts_fields, list) and fts_fields:
            self.fts_index.rebuild(records=records, fields=[str(f) for f in fts_fields])

    @contextmanager
    def _acquire_rw(self) -> Any:
        try:
            with self._rw_lock.acquire(timeout=self.store.lock_timeout):
                yield
        except Timeout as exc:
            raise VaultLockTimeoutError("collection lock acquisition timed out") from exc

    def insert(self, record: dict[str, Any]) -> str:
        """Insert one record and return generated record ID."""
        with self._acquire_rw():
            records = self._read_records()
            now = now_iso()
            rid = uuid4_str()

            stored = dict(record)
            stored["_id"] = rid
            stored["_created"] = now
            stored["_updated"] = now
            stored["_v"] = int(stored.get("_v", 1))

            schema = self._schema()
            if schema:
                self.schema_validator.validate(stored, schema)
            records.append(stored)

            self._write_all(records)
            return rid

    def insert_many(self, documents: list[dict[str, Any]]) -> list[str]:
        """Insert multiple records and return generated record IDs."""
        with self._acquire_rw():
            ids: list[str] = []
            records = self._read_records()
            now = now_iso()
            schema = self._schema()

            for doc in documents:
                rid = uuid4_str()
                stored = dict(doc)
                stored["_id"] = rid
                stored["_created"] = now
                stored["_updated"] = now
                stored["_v"] = int(stored.get("_v", 1))
                if schema:
                    self.schema_validator.validate(stored, schema)
                records.append(stored)
                ids.append(rid)

            self._write_all(records)
            return ids

    def find(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        """Find records matching query with exact, $gt, and $in operators."""
        records = self._read_records()
        return [dict(r) for r in records if match_record(r, query)]

    def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        """Find first matching record or return None."""
        results = self.find(query)
        return results[0] if results else None

    def update(self, query: dict[str, Any], updates: dict[str, Any]) -> int:
        """Update records matching query and return number of updated records."""
        with self._acquire_rw():
            records = self._read_records()
            now = now_iso()
            count = 0
            schema = self._schema()

            for record in records:
                if match_record(record, query):
                    for key, value in updates.items():
                        if key != "_id":
                            record[key] = value
                    record["_v"] = int(record.get("_v", 1)) + 1
                    record["_updated"] = now
                    if schema:
                        self.schema_validator.validate(record, schema)
                    count += 1

            if count:
                self._write_all(records)
            return count

    def delete(self, query: dict[str, Any]) -> int:
        """Delete records matching query and return number of deleted records."""
        with self._acquire_rw():
            records = self._read_records()
            kept = [r for r in records if not match_record(r, query)]
            count = len(records) - len(kept)
            if count:
                self._write_all(kept)
            return count

    def update_many(self, query: dict[str, Any], updates: dict[str, Any]) -> int:
        """Alias for update across all matching records."""
        return self.update(query, updates)

    def delete_many(self, query: dict[str, Any]) -> int:
        """Alias for delete across all matching records."""
        return self.delete(query)

    def upsert(self, query: dict[str, Any], updates: dict[str, Any]) -> str:
        """Update first matching record or insert a new merged document."""
        with self._acquire_rw():
            records = self._read_records()
            now = now_iso()
            schema = self._schema()

            for record in records:
                if match_record(record, query):
                    for key, value in updates.items():
                        if key != "_id":
                            record[key] = value
                    record["_v"] = int(record.get("_v", 1)) + 1
                    record["_updated"] = now
                    if schema:
                        self.schema_validator.validate(record, schema)
                    self._write_all(records)
                    return str(record.get("_id"))

            new_doc = dict(query)
            new_doc.update(updates)
            rid = uuid4_str()
            new_doc["_id"] = rid
            new_doc["_created"] = now
            new_doc["_updated"] = now
            new_doc["_v"] = int(new_doc.get("_v", 1))
            if schema:
                self.schema_validator.validate(new_doc, schema)
            records.append(new_doc)
            self._write_all(records)
            return rid

    def bulk_write(self, operations: list[dict[str, Any]]) -> dict[str, int]:
        """Execute ordered bulk operations and return operation counters."""
        inserted = 0
        updated = 0
        deleted = 0
        with self._acquire_rw():
            records = self._read_records()
            now = now_iso()
            schema = self._schema()
            dirty = False

            for op in operations:
                if "insert" in op:
                    rid = uuid4_str()
                    stored = dict(op["insert"])
                    stored["_id"] = rid
                    stored["_created"] = now
                    stored["_updated"] = now
                    stored["_v"] = int(stored.get("_v", 1))
                    if schema:
                        self.schema_validator.validate(stored, schema)
                    records.append(stored)
                    inserted += 1
                    dirty = True
                elif "update" in op:
                    spec = op["update"]
                    for record in records:
                        if match_record(record, spec.get("filter", {})):
                            for key, value in spec.get("set", {}).items():
                                if key != "_id":
                                    record[key] = value
                            record["_v"] = int(record.get("_v", 1)) + 1
                            record["_updated"] = now
                            if schema:
                                self.schema_validator.validate(record, schema)
                            updated += 1
                            dirty = True
                elif "delete" in op:
                    spec = op["delete"]
                    kept = [r for r in records if not match_record(r, spec.get("filter", {}))]
                    removed = len(records) - len(kept)
                    if removed:
                        deleted += removed
                        dirty = True
                        records = kept

            if dirty:
                self._write_all(records)
        return {"inserted": inserted, "updated": updated, "deleted": deleted}

    def count(self) -> int:
        """Return number of records in the collection."""
        return len(self._read_records())

    def rotate_key(self) -> None:
        """Re-encrypt collection data with a fresh epoch-derived key."""
        with self._acquire_rw():
            self._write_all(self._read_records())

    def exists(self) -> bool:
        """Return True if collection data file exists."""
        return self.collection_dir.exists() and self.meta_path.exists()

    def drop(self) -> None:
        """Remove all collection files from disk."""
        for path in (self.meta_path, self.index_path, self.fts_path):
            if path.exists():
                path.unlink()
        for path in self.shards.list_shards():
            if path.exists():
                path.unlink()
        if self.collection_dir.exists():
            try:
                self.collection_dir.rmdir()
            except OSError:
                pass

    def set_schema(self, schema: dict[str, Any]) -> None:
        """Persist collection JSON schema in encrypted meta.json."""
        meta = self._read_meta()
        meta["schema"] = dict(schema)
        meta.setdefault("collection", self.name)
        meta.setdefault("record_count", self.count())
        meta.setdefault("index_count", len(self.index_manager.read(self.tenant_token)))
        meta.setdefault("shard_count", max(1, len(self.shards.list_shards())))
        meta["updated_at"] = now_iso()
        meta["ts"] = now_epoch()
        self.store.write_encrypted_json(
            file_path=self.meta_path,
            payload=meta,
            tenant_token=self.tenant_token,
            org_id=self.org_id,
            timestamp=now_epoch(),
            purpose="meta",
        )

    def get_schema(self) -> dict[str, Any] | None:
        """Return collection schema from encrypted meta.json."""
        return self._schema()

    def drop_schema(self) -> None:
        """Remove collection schema from encrypted metadata."""
        meta = self._read_meta()
        if "schema" in meta:
            meta.pop("schema")
            meta["updated_at"] = now_iso()
            meta["ts"] = now_epoch()
            self.store.write_encrypted_json(
                file_path=self.meta_path,
                payload=meta,
                tenant_token=self.tenant_token,
                org_id=self.org_id,
                timestamp=now_epoch(),
                purpose="meta",
            )

    def enable_fts(self, fields: list[str]) -> None:
        """Enable full-text index on selected fields and rebuild index."""
        safe_fields = [str(f) for f in fields if str(f).strip()]
        meta = self._read_meta()
        meta["fts_fields"] = safe_fields
        meta["updated_at"] = now_iso()
        meta["ts"] = now_epoch()
        self.store.write_encrypted_json(
            file_path=self.meta_path,
            payload=meta,
            tenant_token=self.tenant_token,
            org_id=self.org_id,
            timestamp=now_epoch(),
            purpose="meta",
        )
        self.fts_index.rebuild(records=self._read_records(), fields=safe_fields)

    def disable_fts(self) -> None:
        """Disable and clear full-text index for this collection."""
        meta = self._read_meta()
        meta["fts_fields"] = []
        meta["updated_at"] = now_iso()
        meta["ts"] = now_epoch()
        self.store.write_encrypted_json(
            file_path=self.meta_path,
            payload=meta,
            tenant_token=self.tenant_token,
            org_id=self.org_id,
            timestamp=now_epoch(),
            purpose="meta",
        )
        self.fts_index.disable()

    def search_scores(self, query_text: str) -> dict[str, float]:
        """Return _id to score map for full-text query."""
        return self.fts_index.search_scores(query_text)
