# chronovault

Enterprise time-keyed encrypted JSON database for Python.

chronovault is a multi-tenant encrypted data package that stores all data in local `.json` files and never uses SQL/NoSQL engines.

## Installation

```bash
pip install chronovault
```

For development with tests:

```bash
pip install -e .[dev]
```

## Quickstart (Simple Mode)

```python
import chronovault as cv

db = cv.connect(
    token="my-secret-token",
    org_id="my-org",
    path="~/.chronovault",
)

record_id = db.users.insert({"name": "Alice", "age": 30})
print(record_id)
print(db.users.find({"name": "Alice"}))
```

## Enterprise Mode

```python
import chronovault as cv

db = cv.connect(
    token="svc-token-abc123",
    org_id="acme-corp",
    path="/var/lib/chronovault",
    role="editor",
    ip_allowlist=["10.0.0.0/8"],
    tls=False,
)
```

### Collections and CRUD

```python
ids = db.users.insert_many([{"name": "Bob"}, {"name": "Carol"}])
rows = db.users.find({"name": {"$in": ["Bob", "Carol"]}})
count = db.users.update({"name": "Bob"}, {"age": 26})
removed = db.users.delete({"name": "Carol"})
n = db.users.count()
```

### Collection Management

```python
db.list_collections()
db.drop_collection("logs")
db.collection_exists("users")
```

### Key Rotation

```python
db.users.rotate_key()
db.rotate_all_keys()
```

### Token Management

```python
token = db.issue_token(
    name="billing-service",
    role="viewer",
    collections=["invoices"],
    ip_allowlist=["192.168.1.0/24"],
    ttl=None,
)

db.revoke_token("billing-service")
db.list_tokens()
```

### Access Links

```python
link = db.generate_link(
    collection="invoices",
    ttl=300,
    ip="203.0.113.5",
    permissions=["read"],
    single_use=True,
)

db.serve(port=8471, host="0.0.0.0")
```

### Audit and Compliance

```python
entries = db.audit_log.tail(n=100)
entries = db.audit_log.filter(event="collection.write", collection="invoices")
ok = db.audit_log.verify_integrity()
db.audit_log.export("audit_export.json")

db.export_compliance_report(output="report.json")
db.tenant_info()
```

## Security Model

chronovault applies the following controls:

- Time-keyed derivation: AES key derived every second using HKDF-SHA256 over `org_id`, token, and epoch.
- Authenticated encryption: AES-256-GCM with random 96-bit nonce and 128-bit tag.
- Tamper detection: invalid tag or malformed encrypted envelope raises `TamperDetectedError`.
- File locking: lock-protected writes via `filelock` plus atomic `os.replace`.
- Tenant isolation: each tenant has isolated directory, token registry, audit log, and key metadata.
- RBAC: `admin`, `editor`, `viewer` roles with action-level enforcement.
- IP binding: token access constrained by exact IP or CIDR allowlist.
- Immutable audit chain: append-only entries with previous-hash linking.
- HMAC links: signed, expiring link tokens validated with constant-time comparison.

## Filesystem Layout

```text
~/.chronovault/
└── tenants/
    └── {org_id}/
        ├── config.json
        ├── tokens.json
        ├── audit.json
        ├── keys_meta.json
        └── collections/
            └── {collection}/
                ├── meta.json
                ├── index.json
                └── data.json
```

All persisted artifacts remain `.json` files.

## Public API Reference

### Connect

```python
db = cv.connect(token, org_id, path, role="admin", ip_allowlist=["*"], tls=False)
```

### CRUD

- `db.<collection>.insert(record) -> str`
- `db.<collection>.insert_many(records) -> list[str]`
- `db.<collection>.find(query) -> list[dict]`
- `db.<collection>.find_one(query) -> dict | None`
- `db.<collection>.update(query, updates) -> int`
- `db.<collection>.delete(query) -> int`
- `db.<collection>.count() -> int`

Query operators supported:

- exact match: `{"key": "value"}`
- greater-than: `{"key": {"$gt": n}}`
- membership: `{"key": {"$in": [..]}}`

### Collection Admin

- `db.list_collections() -> list[str]`
- `db.drop_collection(name) -> None`
- `db.collection_exists(name) -> bool`

### Rekey

- `db.<collection>.rotate_key() -> None`
- `db.rotate_all_keys() -> None`

### Tokens

- `db.issue_token(name, role, collections=None, ip_allowlist=None, ttl=None) -> str`
- `db.revoke_token(name) -> None`
- `db.list_tokens() -> list[dict]`

### Links

- `db.generate_link(collection, ttl, ip, permissions, single_use=True) -> str`
- `db.serve(port=8471, host="0.0.0.0") -> None`

### Audit

- `db.audit_log.tail(n=100) -> list[dict]`
- `db.audit_log.filter(event=None, collection=None) -> list[dict]`
- `db.audit_log.verify_integrity() -> bool`
- `db.audit_log.export(path) -> None`

### Compliance

- `db.export_compliance_report(output) -> None`
- `db.tenant_info() -> dict`

## CLI Reference

```bash
chronovault init --org acme-corp --token <token> --path ~/.chronovault
chronovault status --org acme-corp --token <token>
chronovault collections list --org acme-corp --token <token>
chronovault audit tail --org acme-corp --token <token> --n 50
chronovault audit verify --org acme-corp --token <token>
chronovault token issue --org acme-corp --token <token> --name svc-billing --role viewer
chronovault token revoke --org acme-corp --token <token> --name svc-billing
chronovault rotate --org acme-corp --token <token> --collection users
chronovault serve --org acme-corp --token <token> --port 8471 --host 0.0.0.0
chronovault export-report --org acme-corp --token <token> --output report.json
```

## Exceptions

- `VaultError`
- `AuthenticationError`
- `UnauthorizedIPError`
- `PermissionDeniedError`
- `TokenExpiredError`
- `TokenRevokedError`
- `CollectionNotFoundError`
- `RecordNotFoundError`
- `VaultLockTimeoutError`
- `TamperDetectedError`
- `AuditIntegrityError`
- `TenantNotFoundError`
- `TenantAlreadyExistsError`
- `InvalidTokenError`

## Running Tests

```bash
pytest
```
