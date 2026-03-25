"""gRPC-style access server for ChronoVault token-scoped operations.

This module provides a lightweight request handler with gRPC-like method
semantics without requiring protobuf toolchain setup.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from chronovault.exceptions import ServerConnectionError
from chronovault.storage.collection import Collection
from chronovault.storage.store import JsonStore
from chronovault.tenant.iam import IAM
from chronovault.tenant.tokens import TokenService


@dataclass
class GrpcRequest:
    """RPC request envelope."""

    method: str
    params: dict[str, Any]
    token: str
    source_ip: str = "127.0.0.1"


class GrpcServer:
    """Token-scoped gRPC-style handler for collection operations."""

    def __init__(self, store: JsonStore, tenant_root: Path, org_id: str, tenant_token: str) -> None:
        self.store = store
        self.tenant_root = tenant_root
        self.org_id = org_id
        self.tenant_token = tenant_token
        self.tokens = TokenService(
            store=store,
            tokens_path=tenant_root / "tokens.json",
            org_id=org_id,
            tenant_token=tenant_token,
        )

    def _collection(self, name: str) -> Collection:
        return Collection(
            store=self.store,
            tenant_root=self.tenant_root,
            org_id=self.org_id,
            tenant_token=self.tenant_token,
            name=name,
        )

    def _authorize(self, token: str, source_ip: str, action: str, collection: str | None = None) -> None:
        meta = self.tokens.validate(token=token, source_ip=source_ip, collection=collection)
        IAM.assert_allowed(role=str(meta.get("role", "viewer")), action=action)

    def handle(self, request: GrpcRequest) -> dict[str, Any]:
        """Handle one RPC-style request and return structured response."""
        method = request.method.strip().lower()
        params = dict(request.params)

        try:
            if method == "connect":
                self._authorize(request.token, request.source_ip, action="read")
                return {"ok": True, "org_id": self.org_id}

            if method == "insert":
                collection = str(params["collection"])
                record = dict(params.get("record", {}))
                self._authorize(request.token, request.source_ip, action="write", collection=collection)
                rid = self._collection(collection).insert(record)
                return {"ok": True, "record_id": rid}

            if method == "find":
                collection = str(params["collection"])
                query = dict(params.get("query", {}))
                self._authorize(request.token, request.source_ip, action="find", collection=collection)
                rows = self._collection(collection).find(query)
                return {"ok": True, "records": rows}

            if method == "delete":
                collection = str(params["collection"])
                query = dict(params.get("query", {}))
                self._authorize(request.token, request.source_ip, action="delete", collection=collection)
                count = self._collection(collection).delete(query)
                return {"ok": True, "deleted": count}

            if method == "health":
                self._authorize(request.token, request.source_ip, action="read")
                collections_root = self.tenant_root / "collections"
                collections = []
                if collections_root.exists():
                    collections = sorted([p.name for p in collections_root.iterdir() if p.is_dir()])
                return {"ok": True, "org_id": self.org_id, "collections": collections}

            raise ServerConnectionError("unsupported rpc method")
        except Exception as exc:  # noqa: BLE001
            raise ServerConnectionError("rpc request failed") from exc
