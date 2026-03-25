"""Main ChronoVault orchestration class and collection facade."""

from __future__ import annotations

import json
import importlib
import importlib.metadata
import threading
from pathlib import Path
from typing import Any

import uvicorn

from chronovault.access.linker import Linker
from chronovault.access.server import build_app
from chronovault.access.grpc_server import GrpcServer
from chronovault.access.grpc_transport import GrpcTransportClient, GrpcTransportServer
from chronovault.audit.logger import AuditLogger
from chronovault.backup.manager import BackupManager
from chronovault.core.rekeyer import Rekeyer
from chronovault.exceptions import CollectionNotFoundError, PermissionDeniedError
from chronovault.query.aggregator import Aggregator
from chronovault.query.builder import QueryBuilder
from chronovault.schema.migration import MigrationManager
from chronovault.storage.collection import Collection
from chronovault.storage.store import JsonStore
from chronovault.tenant.iam import IAM
from chronovault.tenant.manager import TenantManager
from chronovault.tenant.tokens import TokenService
from chronovault.transaction.manager import TransactionManager
from chronovault.transaction.wal import WriteAheadLog
from chronovault.utils import now_epoch, redacted_error_message


class _AuditProxy:
    """RBAC-checked audit API exposed at db.audit_log."""

    def __init__(self, vault: "ChronoVault") -> None:
        self.vault = vault

    def tail(self, n: int = 100) -> list[dict[str, Any]]:
        """Return N newest audit entries."""
        self.vault._require(action="audit.read")
        return self.vault._audit.tail(n=n)

    def filter(self, event: str | None = None, collection: str | None = None) -> list[dict[str, Any]]:
        """Return filtered audit entries."""
        self.vault._require(action="audit.read")
        return self.vault._audit.filter(event=event, collection=collection)

    def verify_integrity(self) -> bool:
        """Verify audit hash chain integrity."""
        self.vault._require(action="audit.read")
        return self.vault._audit.verify_integrity()

    def export(self, output: str, encrypted: bool = False) -> None:
        """Export audit entries to a file.

        Set encrypted=True to keep export encrypted at rest.
        """
        self.vault._require(action="audit.read")
        self.vault._audit.export(output=output, encrypted=encrypted)


class _CollectionFacade:
    """RBAC-aware collection access wrapper available via db.<collection>."""

    def __init__(self, vault: "ChronoVault", name: str) -> None:
        self.vault = vault
        self.name = name

    def insert(self, record: dict[str, Any]) -> str:
        """Insert one document and return record ID."""
        return self.vault.safe_call(
            event="collection.write",
            collection=self.name,
            fn=lambda: (
                self.vault._require(action="write", collection=self.name),
                self.vault._collection(self.name).insert(record),
            )[1],
        )

    def insert_many(self, documents: list[dict[str, Any]]) -> list[str]:
        """Insert many documents and return record IDs."""
        return self.vault.safe_call(
            event="collection.write",
            collection=self.name,
            fn=lambda: (
                self.vault._require(action="write", collection=self.name),
                self.vault._collection(self.name).insert_many(documents),
            )[1],
        )

    def find(self, query: dict[str, Any]) -> QueryBuilder:
        """Return chainable query builder initialized with filter."""
        self.vault._require(action="find", collection=self.name)
        return QueryBuilder(self).find(query)

    def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        """Return first document matching query."""
        self.vault._require(action="find", collection=self.name)
        return QueryBuilder(self).find_one(query).first()

    def update(self, query: dict[str, Any], updates: dict[str, Any]) -> int:
        """Update matching documents and return count."""
        return self.vault.safe_call(
            event="collection.update",
            collection=self.name,
            fn=lambda: (
                self.vault._require(action="update", collection=self.name),
                self.vault._collection(self.name).update(query, updates),
            )[1],
        )

    def update_many(self, query: dict[str, Any], updates: dict[str, Any]) -> int:
        """Update all matching documents and return count."""
        return self.update(query, updates)

    def delete(self, query: dict[str, Any]) -> int:
        """Delete matching documents and return count."""
        return self.vault.safe_call(
            event="collection.delete",
            collection=self.name,
            fn=lambda: (
                self.vault._require(action="delete", collection=self.name),
                self.vault._collection(self.name).delete(query),
            )[1],
        )

    def delete_many(self, query: dict[str, Any]) -> int:
        """Delete all matching documents and return count."""
        return self.delete(query)

    def upsert(self, query: dict[str, Any], updates: dict[str, Any]) -> str:
        """Update first match or insert merged document and return record ID."""
        return self.vault.safe_call(
            event="collection.upsert",
            collection=self.name,
            fn=lambda: (
                self.vault._require(action="write", collection=self.name),
                self.vault._collection(self.name).upsert(query, updates),
            )[1],
        )

    def bulk_write(self, operations: list[dict[str, Any]]) -> dict[str, int]:
        """Run ordered bulk write operations and return counters."""
        return self.vault.safe_call(
            event="collection.bulk",
            collection=self.name,
            fn=lambda: (
                self.vault._require(action="write", collection=self.name),
                self.vault._collection(self.name).bulk_write(operations),
            )[1],
        )

    def count(self, query: dict[str, Any] | None = None) -> int:
        """Return document count in collection."""
        self.vault._require(action="find", collection=self.name)
        return QueryBuilder(self).find(query or {}).count()

    def _raw_records(self) -> list[dict[str, Any]]:
        """Return full decrypted records for query builder operations."""
        return self.vault.safe_call(
            event="collection.read",
            collection=self.name,
            fn=lambda: self.vault._collection(self.name).find({}),
        )

    def _fts_search(self, text: str) -> dict[str, float]:
        """Return FTS score map for this collection."""
        self.vault._require(action="read", collection=self.name)
        return self.vault._collection(self.name).search_scores(text)

    def rotate_key(self) -> None:
        """Rotate collection encryption key epoch."""
        self.vault.safe_call(
            event="key.rotate",
            collection=self.name,
            fn=lambda: (
                self.vault._require(action="rotate", collection=self.name),
                self.vault._rekeyer.rotate_collection(self.name),
            )[1],
        )

    def create_index(self, fields: str | list[str], unique: bool = False) -> str:
        """Create field or compound index for the collection."""
        self.vault._require(action="write", collection=self.name)
        return self.vault.safe_call(
            event="index.create",
            collection=self.name,
            fn=lambda: self.vault._collection(self.name).index_manager.create_index(
                tenant_token=self.vault.token,
                fields=fields,
                unique=unique,
            ),
        )

    def drop_index(self, name: str) -> None:
        """Drop index by name from the collection."""
        self.vault._require(action="write", collection=self.name)
        self.vault.safe_call(
            event="index.drop",
            collection=self.name,
            fn=lambda: self.vault._collection(self.name).index_manager.drop_index(
                tenant_token=self.vault.token,
                name=name,
            ),
        )

    def list_indexes(self) -> dict[str, Any]:
        """List collection index metadata."""
        self.vault._require(action="read", collection=self.name)
        return self.vault._collection(self.name).index_manager.list_indexes(tenant_token=self.vault.token)

    def aggregate(self, pipeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Run aggregation pipeline on collection records."""
        self.vault._require(action="read", collection=self.name)
        records = self._raw_records()
        return Aggregator().run(records=records, pipeline=pipeline)

    def set_schema(self, schema: dict[str, Any]) -> None:
        """Set collection schema used to validate future writes."""
        self.vault._require(action="write", collection=self.name)
        self.vault._collection(self.name).set_schema(schema)

    def get_schema(self) -> dict[str, Any] | None:
        """Get collection schema from encrypted metadata."""
        self.vault._require(action="read", collection=self.name)
        return self.vault._collection(self.name).get_schema()

    def drop_schema(self) -> None:
        """Drop collection schema from metadata."""
        self.vault._require(action="write", collection=self.name)
        self.vault._collection(self.name).drop_schema()

    def enable_fts(self, fields: list[str]) -> None:
        """Enable full-text indexing for selected fields."""
        self.vault._require(action="write", collection=self.name)
        self.vault._collection(self.name).enable_fts(fields)

    def disable_fts(self) -> None:
        """Disable full-text indexing for this collection."""
        self.vault._require(action="write", collection=self.name)
        self.vault._collection(self.name).disable_fts()

    def search(self, text: str) -> QueryBuilder:
        """Start a search query pipeline for this collection."""
        self.vault._require(action="read", collection=self.name)
        return QueryBuilder(self).find({}).search(text)


class ChronoVault:
    """Enterprise time-keyed encrypted JSON database engine."""

    def __init__(
        self,
        token: str,
        org_id: str,
        path: str,
        role: str = "admin",
        ip_allowlist: list[str] | None = None,
        tls: bool = False,
        source_ip: str = "127.0.0.1",
    ) -> None:
        """Initialize or connect to a tenant vault."""
        self.org_id = org_id
        self.token = token
        self.source_ip = source_ip

        self._store = JsonStore(lock_timeout=10)
        self._tenants = TenantManager(store=self._store, base_path=Path(path).expanduser())
        self._tenant_root = self._tenants.ensure(
            org_id=org_id,
            tenant_token=token,
            role=role,
            ip_allowlist=ip_allowlist,
            tls=tls,
        )

        self._tokens = TokenService(
            store=self._store,
            tokens_path=self._tenant_root / "tokens.json",
            org_id=self.org_id,
            tenant_token=self.token,
        )
        token_meta = self._tokens.validate(token=token, source_ip=source_ip)
        self._role = token_meta["role"]

        self._audit = AuditLogger(
            store=self._store,
            file_path=self._tenant_root / "audit.json",
            org_id=self.org_id,
            tenant_token=self.token,
        )
        self._rekeyer = Rekeyer(
            store=self._store,
            tenant_root=self._tenant_root,
            org_id=self.org_id,
            tenant_token=self.token,
        )
        self._wal = WriteAheadLog(
            store=self._store,
            wal_path=self._tenant_root / "wal.json",
            org_id=self.org_id,
            tenant_token=self.token,
        )
        self._wal.recover_pending()
        self._transactions = TransactionManager(vault=self, wal=self._wal)
        self._migrations = MigrationManager(
            store=self._store,
            file_path=self._tenant_root / "migrations.json",
            org_id=self.org_id,
            tenant_token=self.token,
            migrations_dir=self._tenant_root / "migrations",
            collection_factory=self._collection,
        )
        self._backup = BackupManager(
            store=self._store,
            tenant_root=self._tenant_root,
            org_id=self.org_id,
            tenant_token=self.token,
        )
        self._collections_cache: dict[str, Collection] = {}

        self.audit_log = _AuditProxy(self)

    def _collection(self, name: str) -> Collection:
        cached = self._collections_cache.get(name)
        if cached is not None:
            return cached
        collection = Collection(
            store=self._store,
            tenant_root=self._tenant_root,
            org_id=self.org_id,
            tenant_token=self.token,
            name=name,
        )
        self._collections_cache[name] = collection
        return collection

    def _require(self, action: str, collection: str | None = None) -> None:
        token_meta = self._tokens.validate(token=self.token, source_ip=self.source_ip, collection=collection)
        IAM.assert_allowed(role=token_meta["role"], action=action)

    def __getattr__(self, name: str) -> _CollectionFacade:
        """Return dynamic collection facade for attribute-based API."""
        if name.startswith("_"):
            raise AttributeError(name)
        return _CollectionFacade(vault=self, name=name)

    def list_collections(self) -> list[str]:
        """List tenant collection names."""
        self._require(action="read")
        root = self._tenant_root / "collections"
        if not root.exists():
            return []
        return sorted([p.name for p in root.iterdir() if p.is_dir()])

    def create_collection(self, name: str) -> None:
        """Create an empty collection directory and encrypted metadata files."""
        self._require(action="write", collection=name)
        coll = self._collection(name)
        if not coll.collection_dir.exists():
            self._store.ensure_dir(coll.collection_dir)
        if not coll.meta_path.exists():
            coll._write_all([])

    def rename_collection(self, old_name: str, new_name: str) -> None:
        """Rename collection directory and preserve encrypted payload files."""
        self._require(action="write", collection=old_name)
        old = self._tenant_root / "collections" / old_name
        new = self._tenant_root / "collections" / new_name
        if not old.exists():
            raise CollectionNotFoundError("collection not found")
        old.rename(new)

    def drop_collection(self, name: str) -> None:
        """Drop collection files from disk."""
        self._require(action="delete", collection=name)
        coll = self._collection(name)
        if not coll.exists():
            raise CollectionNotFoundError("collection not found")
        coll.drop()
        self._audit.append(
            event="collection.drop",
            actor="token:self",
            collection=name,
            record_id=None,
            ip=self.source_ip,
            result="success",
            error=None,
        )

    def collection_exists(self, name: str) -> bool:
        """Return whether collection exists."""
        self._require(action="read", collection=name)
        return self._collection(name).exists()

    def rotate_all_keys(self) -> None:
        """Rotate encryption key epoch for all collections."""
        self._require(action="rotate")
        self._rekeyer.rotate_all()

    def issue_token(
        self,
        name: str,
        role: str,
        collections: list[str] | None = None,
        ip_allowlist: list[str] | None = None,
        ttl: int | None = None,
    ) -> str:
        """Issue a new tenant token and return secret once."""
        self._require(action="token.issue")
        secret = self._tokens.issue_token(
            name=name,
            role=role,
            collections=collections,
            ip_allowlist=ip_allowlist,
            ttl=ttl,
        )
        self._audit.append(
            event="token.issue",
            actor="token:self",
            collection=None,
            record_id=None,
            ip=self.source_ip,
            result="success",
            error=None,
        )
        return secret

    def revoke_token(self, name: str) -> None:
        """Revoke tenant token by name."""
        self._require(action="token.revoke")
        self._tokens.revoke_token(name)
        self._audit.append(
            event="token.revoke",
            actor="token:self",
            collection=None,
            record_id=None,
            ip=self.source_ip,
            result="success",
            error=None,
        )

    def list_tokens(self) -> list[dict[str, Any]]:
        """List token metadata without token secrets."""
        self._require(action="token.issue")
        return self._tokens.list_tokens()

    def generate_link(
        self,
        collection: str,
        ttl: int,
        ip: str,
        permissions: list[str],
        single_use: bool = True,
        base_url: str = "http://127.0.0.1:8471",
    ) -> str:
        """Generate signed access link for collection reads."""
        self._require(action="read", collection=collection)
        linker = Linker(
            store=self._store,
            tokens_path=self._tenant_root / "tokens.json",
            org_id=self.org_id,
            tenant_token=self.token,
            base_url=base_url,
        )
        return linker.generate_link(
            collection=collection,
            ttl=ttl,
            ip=ip,
            permissions=permissions,
            single_use=single_use,
        )

    def serve(self, port: int = 8471, host: str = "0.0.0.0", background: bool = False) -> Any:
        """Serve signed-link access endpoint with FastAPI/Uvicorn.

        Set background=True to start server in a daemon thread and return
        server/thread handles for embedded use cases.
        """
        linker = Linker(
            store=self._store,
            tokens_path=self._tenant_root / "tokens.json",
            org_id=self.org_id,
            tenant_token=self.token,
            base_url=f"http://{host}:{port}",
        )

        def _read_collection(name: str) -> list[dict[str, Any]]:
            self._require(action="read", collection=name)
            return self._collection(name).find({})

        app = build_app(linker=linker, read_collection_data=_read_collection)
        if background:
            config = uvicorn.Config(app=app, host=host, port=port)
            server = uvicorn.Server(config=config)
            thread = threading.Thread(target=server.run, daemon=True)
            thread.start()
            return {"server": server, "thread": thread}
        uvicorn.run(app, host=host, port=port)
        return None

    def grpc_server(self) -> GrpcServer:
        """Return gRPC-style token-scoped server handler."""
        self._require(action="read")
        return GrpcServer(
            store=self._store,
            tenant_root=self._tenant_root,
            org_id=self.org_id,
            tenant_token=self.token,
        )

    def serve_grpc(
        self,
        port: int = 50051,
        host: str = "0.0.0.0",
        background: bool = False,
        max_workers: int = 10,
        require_token_metadata: bool = True,
        tls_cert_chain_path: str | None = None,
        tls_private_key_path: str | None = None,
        tls_root_cert_path: str | None = None,
        tls_require_client_auth: bool = False,
    ) -> Any:
        """Start grpcio network transport server for token-scoped RPC methods."""
        self._require(action="read")
        transport = GrpcTransportServer(
            handler=self.grpc_server(),
            host=host,
            port=port,
            max_workers=max_workers,
            require_token_metadata=require_token_metadata,
            tls_cert_chain_path=tls_cert_chain_path,
            tls_private_key_path=tls_private_key_path,
            tls_root_cert_path=tls_root_cert_path,
            tls_require_client_auth=tls_require_client_auth,
        )
        transport.start()
        if background:
            return transport
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            transport.stop()
        return None

    @staticmethod
    def grpc_client(
        host: str = "127.0.0.1",
        port: int = 50051,
        timeout: float = 5.0,
        use_tls: bool = False,
        tls_root_cert_path: str | None = None,
        tls_client_cert_chain_path: str | None = None,
        tls_client_private_key_path: str | None = None,
    ) -> GrpcTransportClient:
        """Create grpcio transport client for ChronoVaultService."""
        return GrpcTransportClient(
            host=host,
            port=port,
            timeout=timeout,
            use_tls=use_tls,
            tls_root_cert_path=tls_root_cert_path,
            tls_client_cert_chain_path=tls_client_cert_chain_path,
            tls_client_private_key_path=tls_client_private_key_path,
        )

    def export_compliance_report(self, output: str, encrypted: bool = False) -> None:
        """Export high-level tenant compliance report JSON.

        Set encrypted=True to keep the report encrypted on disk.
        """
        self._require(action="compliance")
        report = {
            "tenant": self.tenant_info(),
            "collections": self.list_collections(),
            "tokens": self.list_tokens(),
            "audit_ok": self.audit_log.verify_integrity(),
        }
        if encrypted:
            self._store.write_encrypted_json(
                file_path=Path(output),
                payload=report,
                tenant_token=self.token,
                org_id=self.org_id,
                timestamp=now_epoch(),
                purpose="compliance_report",
            )
            return
        with open(output, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=True)

    def transaction(self) -> Any:
        """Start a WAL-backed transaction context manager."""
        self._require(action="write")
        return self._transactions.start()

    def health_check(self) -> dict[str, Any]:
        """Return a basic health report for collections and WAL state."""
        self._require(action="read")
        read_errors = 0
        for name in self.list_collections():
            try:
                _ = self._collection(name).count()
            except Exception:  # noqa: BLE001
                read_errors += 1
        pending_wal = len(self._wal.pending())
        return {
            "org_id": self.org_id,
            "collections_checked": len(self.list_collections()),
            "read_errors": read_errors,
            "pending_wal": pending_wal,
            "healthy": read_errors == 0 and pending_wal == 0,
        }

    @staticmethod
    def preflight_check() -> dict[str, Any]:
        """Validate required runtime dependencies and return status details."""
        required = ["cryptography", "filelock", "fastapi", "uvicorn", "click", "rich", "grpc", "google.protobuf"]
        installed: dict[str, str] = {}
        missing: list[str] = []

        for name in required:
            try:
                module = importlib.import_module(name)
                try:
                    version = importlib.metadata.version(name)
                except importlib.metadata.PackageNotFoundError:
                    version = getattr(module, "__version__", "unknown")
                installed[name] = str(version)
            except Exception:  # noqa: BLE001
                missing.append(name)

        return {
            "ok": len(missing) == 0,
            "installed": installed,
            "missing": missing,
        }

    def backup(self, output_path: str, include_audit: bool = True) -> None:
        """Export tenant snapshot into one encrypted backup file."""
        self._require(action="compliance")
        self._backup.export(output_path=output_path, include_audit=include_audit)

    def restore(self, input_path: str, force: bool = False) -> None:
        """Restore tenant snapshot from encrypted backup file."""
        self._require(action="compliance")
        self._backup.restore(input_path=input_path, force=force)
        self._collections_cache.clear()

    def migrate(self, collection: str, direction: str, version: int | None = None) -> dict[str, Any]:
        """Apply migration direction for one collection and return status."""
        self._require(action="compliance")
        return self._migrations.apply(collection=collection, direction=direction, version=version)

    def migration_status(self) -> dict[str, Any]:
        """Return migration status for all collections."""
        self._require(action="compliance")
        return self._migrations.status()

    def tenant_info(self) -> dict[str, Any]:
        """Return non-secret tenant metadata."""
        self._require(action="read")
        return self._tenants.tenant_info(org_id=self.org_id, tenant_token=self.token)

    def safe_call(self, event: str, fn: callable, collection: str | None = None, record_id: str | None = None) -> Any:
        """Execute function and append success/denied/error audit event."""
        try:
            result = fn()
            self._audit.append(
                event=event,
                actor="token:self",
                collection=collection,
                record_id=record_id,
                ip=self.source_ip,
                result="success",
                error=None,
            )
            return result
        except PermissionDeniedError as exc:
            self._audit.append(
                event=event,
                actor="token:self",
                collection=collection,
                record_id=record_id,
                ip=self.source_ip,
                result="denied",
                error=redacted_error_message(exc),
            )
            raise
        except Exception as exc:  # noqa: BLE001
            self._audit.append(
                event=event,
                actor="token:self",
                collection=collection,
                record_id=record_id,
                ip=self.source_ip,
                result="error",
                error=redacted_error_message(exc),
            )
            raise
