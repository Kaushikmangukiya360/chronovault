import socket
import time

from fastapi.testclient import TestClient
import grpc
import pytest
from google.protobuf import struct_pb2

import chronovault as cv
from chronovault.access.grpc_server import GrpcRequest
from chronovault.access.proto import chronovault_service_pb2
from chronovault.access.grpc_transport import GrpcTransportClient
from chronovault.access.linker import Linker
from chronovault.access.server import build_app


def test_grpc_server_token_scoped_ops(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-grpc", path=str(tmp_path))
    grpc = db.grpc_server()

    connect_resp = grpc.handle(GrpcRequest(method="connect", params={}, token="root-secret"))
    assert connect_resp["ok"] is True

    insert_resp = grpc.handle(
        GrpcRequest(
            method="insert",
            params={"collection": "users", "record": {"name": "Alice", "age": 30}},
            token="root-secret",
        )
    )
    assert insert_resp["ok"] is True

    find_resp = grpc.handle(
        GrpcRequest(
            method="find",
            params={"collection": "users", "query": {"name": "Alice"}},
            token="root-secret",
        )
    )
    assert len(find_resp["records"]) == 1


def test_rest_grpc_parity_for_access_data(tmp_path) -> None:
    db = cv.connect(token="root-secret", org_id="org-parity", path=str(tmp_path))
    db.invoices.insert({"n": 1, "status": "paid"})

    linker = Linker(
        store=db._store,
        tokens_path=db._tenant_root / "tokens.json",
        org_id=db.org_id,
        tenant_token=db.token,
    )

    app = build_app(linker=linker, read_collection_data=lambda name: db._collection(name).find({}))
    client = TestClient(app)

    link = linker.generate_link(
        collection="invoices",
        ttl=60,
        ip="testclient",
        permissions=["read"],
        single_use=False,
    )
    token = link.split("t=", 1)[1]

    rest_resp = client.get("/access", params={"t": token})
    assert rest_resp.status_code == 200
    rest_records = rest_resp.json()["records"]

    grpc = db.grpc_server()
    grpc_resp = grpc.handle(
        GrpcRequest(
            method="find",
            params={"collection": "invoices", "query": {}},
            token="root-secret",
        )
    )
    grpc_records = grpc_resp["records"]

    assert rest_records == grpc_records


def test_grpc_transport_server_client_roundtrip(tmp_path) -> None:
    pytest.importorskip("grpc")

    db = cv.connect(token="root-secret", org_id="org-grpc-net", path=str(tmp_path))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    server = db.serve_grpc(host="127.0.0.1", port=port, background=True, max_workers=4)
    client = GrpcTransportClient(host="127.0.0.1", port=port, timeout=3.0)

    try:
        for _ in range(20):
            try:
                health = client.health(token="root-secret")
                if health.get("ok"):
                    break
            except Exception:  # noqa: BLE001
                time.sleep(0.05)
        else:
            assert False, "grpc transport server did not become ready"

        insert = client.insert(
            token="root-secret",
            collection="users",
            record={"name": "Alice", "age": 30},
        )
        assert insert.get("ok") is True

        find = client.find(token="root-secret", collection="users", query={"name": "Alice"})
        assert find.get("ok") is True
        assert len(find.get("records", [])) == 1
    finally:
        client.close()
        server.stop()


def test_grpc_transport_rejects_missing_token_metadata(tmp_path) -> None:
    pytest.importorskip("grpc")

    db = cv.connect(token="root-secret", org_id="org-grpc-auth", path=str(tmp_path))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    server = db.serve_grpc(host="127.0.0.1", port=port, background=True, max_workers=2, require_token_metadata=True)

    channel = grpc.insecure_channel(f"127.0.0.1:{port}")
    rpc = channel.unary_unary(
        "/chronovault.api.v1.ChronoVaultService/Health",
        request_serializer=chronovault_service_pb2.HealthRequest.SerializeToString,
        response_deserializer=struct_pb2.Struct.FromString,
    )

    payload = chronovault_service_pb2.HealthRequest(token="root-secret", source_ip="127.0.0.1")

    try:
        with pytest.raises(grpc.RpcError) as exc_info:
            rpc(payload, timeout=2.0)
        assert exc_info.value.code() == grpc.StatusCode.UNAUTHENTICATED
    finally:
        channel.close()
        server.stop()


def test_grpc_transport_rejects_metadata_token_mismatch(tmp_path) -> None:
    pytest.importorskip("grpc")

    db = cv.connect(token="root-secret", org_id="org-grpc-auth-mismatch", path=str(tmp_path))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    server = db.serve_grpc(host="127.0.0.1", port=port, background=True, max_workers=2, require_token_metadata=True)

    channel = grpc.insecure_channel(f"127.0.0.1:{port}")
    rpc = channel.unary_unary(
        "/chronovault.api.v1.ChronoVaultService/Health",
        request_serializer=chronovault_service_pb2.HealthRequest.SerializeToString,
        response_deserializer=struct_pb2.Struct.FromString,
    )

    payload = chronovault_service_pb2.HealthRequest(token="root-secret", source_ip="127.0.0.1")

    try:
        with pytest.raises(grpc.RpcError) as exc_info:
            rpc(
                payload,
                timeout=2.0,
                metadata=[("x-chronovault-token", "wrong-token"), ("x-chronovault-source-ip", "127.0.0.1")],
            )
        assert exc_info.value.code() == grpc.StatusCode.UNAUTHENTICATED
    finally:
        channel.close()
        server.stop()
