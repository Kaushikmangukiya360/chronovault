# chronovault Documentation Hub

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

```text
██████╗██╗  ██╗██████╗  ██████╗ ███╗   ██╗ ██████╗
██╔════╝██║  ██║██╔══██╗██╔═══██╗████╗  ██║██╔═══██╗
██║     ███████║██████╔╝██║   ██║██╔██╗ ██║██║   ██║
██║     ██╔══██║██╔══██╗██║   ██║██║╚██╗██║██║   ██║
╚██████╗██║  ██║██║  ██║╚██████╔╝██║ ╚████║╚██████╔╝
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝
                                            V A U L T
```

**Enterprise-grade time-keyed encrypted JSON database for Python**

![PyPI](https://img.shields.io/pypi/v/chronovault)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Security](https://img.shields.io/badge/security-AES--256--GCM-critical)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Built by](https://img.shields.io/badge/built%20by-%40kaushik%20mangukiya-black)

chronovault solves a hard problem that most application stacks postpone until after a breach: secure persistence by default. Instead of storing plaintext business data in files or traditional engines, chronovault stores only AES-256-GCM encrypted JSON envelopes on disk, derives encryption keys from your token + tenant + current second, and enforces tenant isolation, auditability, and access control from the first line of code.

## Why chronovault

- Zero plaintext on disk: every persisted JSON artifact is encrypted.
- Key rotates every second: HKDF derives a new AES-256 key per epoch second.
- Zero-knowledge design: without token + org context, ciphertext is unusable.
- No server required: pure Python package, local files, fully offline.
- Broad workload coverage: document CRUD, querying, joins, aggregation, indexing.
- Compliance-first posture: audit trail, tenant isolation, and security controls by design.

## Quick Install

```bash
pip install chronovault
```

## 15-line Quick Example

```python
import json
import os
import chronovault as cv

db = cv.connect(token="replace-with-secure-token", org_id="acme", path="~/.chronovault")
user_id = db.users.insert({"name": "Alice", "email": "alice@example.com", "age": 30})
print("Inserted:", user_id)
print("Find:", db.users.find({"name": "Alice"}).execute())

p = os.path.expanduser("~/.chronovault/tenants/acme/collections/users/data_000.json")
with open(p, "r", encoding="utf-8") as f:
    encrypted = json.load(f)
print(json.dumps(encrypted, indent=2))
# You will only see envelope metadata + ciphertext (ct), never plaintext records.
```

## Feature Matrix

| Capability | Status |
|---|---|
| Time-keyed HKDF key derivation | ✅ |
| AES-256-GCM encrypted JSON storage | ✅ |
| Multi-tenant namespace isolation | ✅ |
| RBAC (admin/editor/viewer) | ✅ |
| IP allowlist enforcement | ✅ |
| Immutable audit chain hash | ✅ |
| Query operators + builder | ✅ |
| Aggregation pipeline | ✅ |
| Cross-collection joins | ✅ |
| Field indexes and unique constraints | ✅ |
| Schema validation | ✅ |
| Sharding + cache | ✅ |
| Signed access links | ✅ |
| CLI operations | ✅ |
| Backup/restore, transactions, FTS, ORM, integrations | ✅ (platform roadmap + implementation dependent by release) |

## Documentation Index

### Guides

| Guide | Link |
|---|---|
| Overview | [guides/00_OVERVIEW.md](guides/00_OVERVIEW.md) |
| Installation | [guides/01_INSTALLATION.md](guides/01_INSTALLATION.md) |
| Quickstart | [guides/02_QUICKSTART.md](guides/02_QUICKSTART.md) |
| Configuration | [guides/03_CONFIGURATION.md](guides/03_CONFIGURATION.md) |
| CRUD | [guides/04_CRUD_OPERATIONS.md](guides/04_CRUD_OPERATIONS.md) |
| Query Engine | [guides/05_QUERY_ENGINE.md](guides/05_QUERY_ENGINE.md) |
| Aggregation | [guides/06_AGGREGATION.md](guides/06_AGGREGATION.md) |
| Joins | [guides/07_JOINS.md](guides/07_JOINS.md) |
| Indexing | [guides/08_INDEXING.md](guides/08_INDEXING.md) |
| Schema Validation | [guides/09_SCHEMA_VALIDATION.md](guides/09_SCHEMA_VALIDATION.md) |
| Full-Text Search | [guides/10_FULL_TEXT_SEARCH.md](guides/10_FULL_TEXT_SEARCH.md) |
| Transactions | [guides/11_TRANSACTIONS.md](guides/11_TRANSACTIONS.md) |
| Multi-tenant | [guides/12_MULTI_TENANT.md](guides/12_MULTI_TENANT.md) |
| Access Control | [guides/13_ACCESS_CONTROL.md](guides/13_ACCESS_CONTROL.md) |
| IP Binding | [guides/14_IP_BINDING.md](guides/14_IP_BINDING.md) |
| Audit Log | [guides/15_AUDIT_LOG.md](guides/15_AUDIT_LOG.md) |
| Key Rotation | [guides/16_KEY_ROTATION.md](guides/16_KEY_ROTATION.md) |
| Access Links | [guides/17_ACCESS_LINKS.md](guides/17_ACCESS_LINKS.md) |
| Server Mode | [guides/18_SERVER_MODE.md](guides/18_SERVER_MODE.md) |
| ORM | [guides/19_ORM.md](guides/19_ORM.md) |
| Migrations | [guides/20_MIGRATIONS.md](guides/20_MIGRATIONS.md) |
| Backup/Restore | [guides/21_BACKUP_RESTORE.md](guides/21_BACKUP_RESTORE.md) |
| Performance | [guides/22_PERFORMANCE.md](guides/22_PERFORMANCE.md) |
| Compliance | [guides/23_COMPLIANCE.md](guides/23_COMPLIANCE.md) |
| Publishing | [guides/24_PUBLISHING.md](guides/24_PUBLISHING.md) |

### Architecture

| Doc | Link |
|---|---|
| System Architecture | [architecture/SYSTEM_ARCHITECTURE.md](architecture/SYSTEM_ARCHITECTURE.md) |
| Encryption Model | [architecture/ENCRYPTION_MODEL.md](architecture/ENCRYPTION_MODEL.md) |
| Key Derivation | [architecture/KEY_DERIVATION.md](architecture/KEY_DERIVATION.md) |
| Storage Format | [architecture/STORAGE_FORMAT.md](architecture/STORAGE_FORMAT.md) |
| Query Pipeline | [architecture/QUERY_PIPELINE.md](architecture/QUERY_PIPELINE.md) |
| Transaction Internals | [architecture/TRANSACTION_INTERNALS.md](architecture/TRANSACTION_INTERNALS.md) |
| Shard System | [architecture/SHARD_SYSTEM.md](architecture/SHARD_SYSTEM.md) |
| Tenant Isolation | [architecture/TENANT_ISOLATION.md](architecture/TENANT_ISOLATION.md) |
| Threat Model | [architecture/THREAT_MODEL.md](architecture/THREAT_MODEL.md) |

### Reference

| Doc | Link |
|---|---|
| API Reference | [reference/API_REFERENCE.md](reference/API_REFERENCE.md) |
| CLI Reference | [reference/CLI_REFERENCE.md](reference/CLI_REFERENCE.md) |
| Exceptions | [reference/EXCEPTIONS_REFERENCE.md](reference/EXCEPTIONS_REFERENCE.md) |
| Configuration | [reference/CONFIGURATION_REFERENCE.md](reference/CONFIGURATION_REFERENCE.md) |
| File Formats | [reference/FILE_FORMAT_REFERENCE.md](reference/FILE_FORMAT_REFERENCE.md) |

### Integrations

| Doc | Link |
|---|---|
| Django | [integrations/DJANGO_INTEGRATION.md](integrations/DJANGO_INTEGRATION.md) |
| FastAPI | [integrations/FASTAPI_INTEGRATION.md](integrations/FASTAPI_INTEGRATION.md) |
| gRPC | [integrations/GRPC_INTEGRATION.md](integrations/GRPC_INTEGRATION.md) |

### Examples & Diagrams

- Examples: [examples](examples)
- Diagrams: [diagrams](diagrams)

## Security Comparison

| Dimension | chronovault | SQLite | MongoDB | PostgreSQL |
|---|---|---|---|---|
| Default at-rest encryption | ✅ (always) | ❌ | ⚠️ optional | ⚠️ optional |
| Per-tenant cryptographic separation | ✅ | ❌ | ⚠️ app-defined | ⚠️ app-defined |
| Time-keyed key evolution | ✅ | ❌ | ❌ | ❌ |
| Authenticated ciphertext integrity | ✅ | ❌ | ⚠️ depends config | ⚠️ depends config |
| JSON file-level portability | ✅ | ❌ | ❌ | ❌ |
| Built-in append-only audit chain | ✅ | ❌ | ❌ | ❌ |
| No external server required | ✅ | ✅ | ❌ | ❌ |
| Fail-fast tamper detection | ✅ | ❌ | ⚠️ | ⚠️ |
| IP-bound service tokens | ✅ | ❌ | ⚠️ custom | ⚠️ custom |
| Signed access links | ✅ | ❌ | ❌ | ❌ |

## Who Built This

Built by **@kaushik mangukiya**  
kaushikmangukiya360@gmail.com

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
