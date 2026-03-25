"""Production gRPC transport for ChronoVault.

This module uses generated protobuf service stubs/messages from
`chronovault_service.proto` and exposes a grpcio network server/client pair.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import grpc
from google.protobuf import struct_pb2

from chronovault.access.grpc_server import GrpcRequest, GrpcServer
from chronovault.access.proto import chronovault_service_pb2
from chronovault.access.proto import chronovault_service_pb2_grpc


def _to_struct(payload: dict[str, Any]) -> struct_pb2.Struct:
    msg = struct_pb2.Struct()
    msg.update(payload)
    return msg


def _from_struct(message: struct_pb2.Struct) -> dict[str, Any]:
    return dict(message)


class GrpcTransportServer:
    """grpcio transport server wrapping the token-scoped in-process handler."""

    def __init__(
        self,
        handler: GrpcServer,
        host: str = "0.0.0.0",
        port: int = 50051,
        max_workers: int = 10,
        require_token_metadata: bool = True,
        tls_cert_chain_path: str | None = None,
        tls_private_key_path: str | None = None,
        tls_root_cert_path: str | None = None,
        tls_require_client_auth: bool = False,
    ) -> None:
        self.handler = handler
        self.host = host
        self.port = int(port)
        self.max_workers = int(max_workers)
        self.require_token_metadata = bool(require_token_metadata)
        self.tls_cert_chain_path = tls_cert_chain_path
        self.tls_private_key_path = tls_private_key_path
        self.tls_root_cert_path = tls_root_cert_path
        self.tls_require_client_auth = bool(tls_require_client_auth)
        self._server: grpc.Server | None = None

    @staticmethod
    def _metadata_map(context: grpc.ServicerContext) -> dict[str, str]:
        metadata = context.invocation_metadata() or []
        return {str(k).lower(): str(v) for k, v in metadata}

    def _apply_auth_metadata(self, request: struct_pb2.Struct, context: grpc.ServicerContext) -> tuple[bool, struct_pb2.Struct]:
        metadata = self._metadata_map(context)
        meta_token = metadata.get("x-chronovault-token", "")
        meta_ip = metadata.get("x-chronovault-source-ip", "")

        body = _from_struct(request)
        body_token = str(body.get("token", ""))

        if self.require_token_metadata and not meta_token:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("missing x-chronovault-token metadata")
            return False, request

        if meta_token and body_token and meta_token != body_token:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("token mismatch between metadata and request payload")
            return False, request

        if meta_token and not body_token:
            body["token"] = meta_token
        if meta_ip and not body.get("source_ip"):
            body["source_ip"] = meta_ip

        return True, _to_struct(body)

    def _safe_handle(self, method: str, request: GrpcRequest, context: grpc.ServicerContext) -> struct_pb2.Struct:
        try:
            response = self.handler.handle(request)
            return _to_struct(response)
        except Exception as exc:  # noqa: BLE001
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"rpc {method} failed: {type(exc).__name__}")
            return _to_struct({"ok": False, "error": "rpc request failed"})

    def _unauthenticated(self) -> struct_pb2.Struct:
        return _to_struct({"ok": False, "error": "unauthenticated"})

    def _make_request(self, token: str, source_ip: str, method: str, params: dict[str, Any]) -> GrpcRequest:
        return GrpcRequest(method=method, params=params, token=token, source_ip=source_ip)

    class _Servicer(chronovault_service_pb2_grpc.ChronoVaultServiceServicer):
        def __init__(self, outer: "GrpcTransportServer") -> None:
            self.outer = outer

        def Connect(self, request: chronovault_service_pb2.ConnectRequest, context: grpc.ServicerContext) -> struct_pb2.Struct:
            ok, patched = self.outer._apply_auth_metadata(_to_struct({"token": request.token, "source_ip": request.source_ip}), context)
            if not ok:
                return self.outer._unauthenticated()
            body = _from_struct(patched)
            envelope = self.outer._make_request(
                token=str(body.get("token", "")),
                source_ip=str(body.get("source_ip", "127.0.0.1")),
                method="connect",
                params={},
            )
            return self.outer._safe_handle("Connect", envelope, context)

        def Insert(self, request: chronovault_service_pb2.WriteRequest, context: grpc.ServicerContext) -> struct_pb2.Struct:
            ok, patched = self.outer._apply_auth_metadata(
                _to_struct(
                    {
                        "token": request.token,
                        "source_ip": request.source_ip,
                        "collection": request.collection,
                        "record": _from_struct(request.record),
                    }
                ),
                context,
            )
            if not ok:
                return self.outer._unauthenticated()
            body = _from_struct(patched)
            envelope = self.outer._make_request(
                token=str(body.get("token", "")),
                source_ip=str(body.get("source_ip", "127.0.0.1")),
                method="insert",
                params={"collection": str(body.get("collection", "")), "record": dict(body.get("record", {}))},
            )
            return self.outer._safe_handle("Insert", envelope, context)

        def Find(self, request: chronovault_service_pb2.QueryRequest, context: grpc.ServicerContext) -> struct_pb2.Struct:
            ok, patched = self.outer._apply_auth_metadata(
                _to_struct(
                    {
                        "token": request.token,
                        "source_ip": request.source_ip,
                        "collection": request.collection,
                        "query": _from_struct(request.query),
                    }
                ),
                context,
            )
            if not ok:
                return self.outer._unauthenticated()
            body = _from_struct(patched)
            envelope = self.outer._make_request(
                token=str(body.get("token", "")),
                source_ip=str(body.get("source_ip", "127.0.0.1")),
                method="find",
                params={"collection": str(body.get("collection", "")), "query": dict(body.get("query", {}))},
            )
            return self.outer._safe_handle("Find", envelope, context)

        def Delete(self, request: chronovault_service_pb2.QueryRequest, context: grpc.ServicerContext) -> struct_pb2.Struct:
            ok, patched = self.outer._apply_auth_metadata(
                _to_struct(
                    {
                        "token": request.token,
                        "source_ip": request.source_ip,
                        "collection": request.collection,
                        "query": _from_struct(request.query),
                    }
                ),
                context,
            )
            if not ok:
                return self.outer._unauthenticated()
            body = _from_struct(patched)
            envelope = self.outer._make_request(
                token=str(body.get("token", "")),
                source_ip=str(body.get("source_ip", "127.0.0.1")),
                method="delete",
                params={"collection": str(body.get("collection", "")), "query": dict(body.get("query", {}))},
            )
            return self.outer._safe_handle("Delete", envelope, context)

        def Health(self, request: chronovault_service_pb2.HealthRequest, context: grpc.ServicerContext) -> struct_pb2.Struct:
            ok, patched = self.outer._apply_auth_metadata(_to_struct({"token": request.token, "source_ip": request.source_ip}), context)
            if not ok:
                return self.outer._unauthenticated()
            body = _from_struct(patched)
            envelope = self.outer._make_request(
                token=str(body.get("token", "")),
                source_ip=str(body.get("source_ip", "127.0.0.1")),
                method="health",
                params={},
            )
            return self.outer._safe_handle("Health", envelope, context)

    def start(self) -> str:
        """Start gRPC server and return bound endpoint string."""
        if self._server is not None:
            return self.endpoint

        server = grpc.server(ThreadPoolExecutor(max_workers=self.max_workers))
        chronovault_service_pb2_grpc.add_ChronoVaultServiceServicer_to_server(self._Servicer(self), server)
        if self.tls_cert_chain_path and self.tls_private_key_path:
            cert_chain = Path(self.tls_cert_chain_path).read_bytes()
            private_key = Path(self.tls_private_key_path).read_bytes()
            root_certs = None
            if self.tls_root_cert_path:
                root_certs = Path(self.tls_root_cert_path).read_bytes()
            credentials = grpc.ssl_server_credentials(
                [(private_key, cert_chain)],
                root_certificates=root_certs,
                require_client_auth=self.tls_require_client_auth,
            )
            server.add_secure_port(self.endpoint, credentials)
        else:
            server.add_insecure_port(self.endpoint)
        server.start()
        self._server = server
        return self.endpoint

    @property
    def endpoint(self) -> str:
        return f"{self.host}:{self.port}"

    def stop(self, grace: float = 1.0) -> None:
        """Stop server if it is running."""
        if self._server is not None:
            self._server.stop(grace)
            self._server = None


class GrpcTransportClient:
    """Small grpcio client for ChronoVaultService unary RPCs."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 50051,
        timeout: float = 5.0,
        use_tls: bool = False,
        tls_root_cert_path: str | None = None,
        tls_client_cert_chain_path: str | None = None,
        tls_client_private_key_path: str | None = None,
    ) -> None:
        self.target = f"{host}:{int(port)}"
        self.timeout = float(timeout)
        if use_tls:
            root = Path(tls_root_cert_path).read_bytes() if tls_root_cert_path else None
            cert_chain = Path(tls_client_cert_chain_path).read_bytes() if tls_client_cert_chain_path else None
            private_key = Path(tls_client_private_key_path).read_bytes() if tls_client_private_key_path else None
            credentials = grpc.ssl_channel_credentials(
                root_certificates=root,
                private_key=private_key,
                certificate_chain=cert_chain,
            )
            self._channel = grpc.secure_channel(self.target, credentials)
        else:
            self._channel = grpc.insecure_channel(self.target)
        self._stub = chronovault_service_pb2_grpc.ChronoVaultServiceStub(self._channel)

    def _call(self, rpc: Any, message: Any, token: str, source_ip: str) -> dict[str, Any]:
        metadata = []
        token = str(token).strip()
        source_ip = str(source_ip).strip()
        if token:
            metadata.append(("x-chronovault-token", token))
        if source_ip:
            metadata.append(("x-chronovault-source-ip", source_ip))
        response = rpc(message, timeout=self.timeout, metadata=metadata)
        return _from_struct(response)

    def connect(self, token: str, source_ip: str = "127.0.0.1") -> dict[str, Any]:
        request = chronovault_service_pb2.ConnectRequest(token=token, source_ip=source_ip)
        return self._call(self._stub.Connect, request, token=token, source_ip=source_ip)

    def insert(self, token: str, collection: str, record: dict[str, Any], source_ip: str = "127.0.0.1") -> dict[str, Any]:
        record_struct = _to_struct(dict(record))
        request = chronovault_service_pb2.WriteRequest(
            token=token,
            source_ip=source_ip,
            collection=collection,
            record=record_struct,
        )
        return self._call(self._stub.Insert, request, token=token, source_ip=source_ip)

    def find(self, token: str, collection: str, query: dict[str, Any], source_ip: str = "127.0.0.1") -> dict[str, Any]:
        query_struct = _to_struct(dict(query))
        request = chronovault_service_pb2.QueryRequest(
            token=token,
            source_ip=source_ip,
            collection=collection,
            query=query_struct,
        )
        return self._call(self._stub.Find, request, token=token, source_ip=source_ip)

    def delete(self, token: str, collection: str, query: dict[str, Any], source_ip: str = "127.0.0.1") -> dict[str, Any]:
        query_struct = _to_struct(dict(query))
        request = chronovault_service_pb2.QueryRequest(
            token=token,
            source_ip=source_ip,
            collection=collection,
            query=query_struct,
        )
        return self._call(self._stub.Delete, request, token=token, source_ip=source_ip)

    def health(self, token: str, source_ip: str = "127.0.0.1") -> dict[str, Any]:
        request = chronovault_service_pb2.HealthRequest(token=token, source_ip=source_ip)
        return self._call(self._stub.Health, request, token=token, source_ip=source_ip)

    def close(self) -> None:
        self._channel.close()
