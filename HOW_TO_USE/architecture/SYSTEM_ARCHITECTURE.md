# System Architecture

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

## Table of Contents

- Layered Architecture Diagram
- Request Lifecycle Diagram
- Component Dependency Map
- Layer Walkthrough

## Layered Architecture Diagram

```mermaid
graph TD
    A[Your App] --> B[Public API]
    B --> C[IAM Layer]
    C --> D[Query Engine]
    D --> E[Key Derivation Engine]
    E --> F[AES-256-GCM Cipher]
    F --> G[Storage Layer]
    G --> H[Encrypted JSON Files]
```

## Request Lifecycle Diagram

```mermaid
flowchart TD
    A[db.users.insert] --> B[Validate Token and Role]
    B --> C[Validate IP and Scope]
    C --> D[Validate Schema]
    D --> E[Derive HKDF Key]
    E --> F[Encrypt Payload with AES-GCM]
    F --> G[Acquire FileLock]
    G --> H[Write .tmp Envelope]
    H --> I[os.replace to Final File]
    I --> J[Update Index and Meta]
    J --> K[Append Audit Event]
    K --> L[Return Record ID]
```

## Component Map

```mermaid
graph LR
    V[core/vault.py] --> C[storage/collection.py]
    V --> T[tenant/tokens.py]
    V --> A[audit/logger.py]
    V --> Q[query/builder.py]
    C --> S[storage/store.py]
    C --> I[storage/index.py]
    C --> SH[storage/shard.py]
    S --> CI[core/cipher.py]
    CI --> K[core/kde.py]
    Q --> QE[query/engine.py]
    QE --> OP[query/operators.py]
```

## Layer Walkthrough

### Public API Layer

`connect()` initializes the vault context, provisions tenant structure if missing, and validates access token state. Collection access is proxy-based (`db.users`) and delegates to collection operations with IAM checks.

### IAM Layer

Token validation covers hash lookup, revocation status, expiry, IP allowlist, and collection scoping. RBAC gates each action.

### Query Layer

The query engine handles operator matching and transforms results through sort/pagination/projection. Builder chaining keeps callsites readable and deterministic.

### Cryptography Layer

HKDF derives a 32-byte key from token + org + epoch. Cipher layer uses AES-256-GCM with random nonce and integrity tag.

### Storage Layer

Writes are lock-protected, atomic (`.tmp` then `os.replace`), and permission tightened to owner-only. Data is partitioned into shards and can be scanned in parallel.

### Persistence Layer

All persisted artifacts are JSON files with encrypted payload envelopes.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
