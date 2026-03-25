# Service Mode Deployment and Operations

## Scope
This guide covers deployment and operations for ChronoVault service mode using REST access and grpcio transport server mode.

## Runtime Components
- REST signed-link service: [chronovault/access/server.py](../../chronovault/access/server.py)
- gRPC-style handler: [chronovault/access/grpc_server.py](../../chronovault/access/grpc_server.py)
- grpcio transport service: [chronovault/access/grpc_transport.py](../../chronovault/access/grpc_transport.py)
- Protobuf contract: [chronovault/access/proto/chronovault_service.proto](../../chronovault/access/proto/chronovault_service.proto)
- Vault orchestration: [chronovault/core/vault.py](../../chronovault/core/vault.py)

## Preflight
Run dependency checks before deployment:

```bash
chronovault preflight
```

Expected output:
- ok=true
- no missing dependencies

## Local Service Startup
Start REST service:

```bash
chronovault serve --org acme --token root-secret --path ~/.chronovault --host 0.0.0.0 --port 8471
```

Use signed links for controlled reads:
- Generate link from SDK: db.generate_link(...)
- Validate link through REST /access endpoint

## gRPC-style Operations
Use token-scoped RPC handler from SDK:

```python
grpc = db.grpc_server()
resp = grpc.handle(GrpcRequest(method="find", params={"collection": "users", "query": {}}, token="root-secret"))
```

Supported methods:
- connect
- insert
- find
- delete
- health

## gRPC Transport Startup
Run network grpcio transport daemon:

```bash
chronovault serve-grpc --org acme --token root-secret --path ~/.chronovault --host 0.0.0.0 --port 50051
```

Optional TLS/mTLS flags:
- `--tls-cert-chain`
- `--tls-private-key`
- `--tls-root-cert`
- `--tls-require-client-auth`

## Operational Checklist
- Run preflight before every release deployment
- Run full tests before rollout
- Verify health endpoint/command after startup
- Rotate keys periodically
- Backup before schema or migration changes

## Incident Response Basics
- Failed auth or IP violations: inspect encrypted audit log tail
- Recovery after interruption: WAL pending entries are recovered on startup
- Restore scenario: use encrypted backup restore with force guard

## Validation Commands
```bash
python -m pytest -q
chronovault health --org acme --token root-secret --path ~/.chronovault
```

## Notes
- Core operations remain offline and JSON-only storage.
- gRPC transport is available via protobuf plus grpcio network daemon.
- For full enterprise backlog after current completion scope, see [POST_CHECKLIST_MISSING_PARTS.md](POST_CHECKLIST_MISSING_PARTS.md).
