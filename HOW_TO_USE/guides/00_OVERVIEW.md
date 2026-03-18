# 00 Overview

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

## Table of Contents

- [What chronovault Is](#what-chronovault-is)
- [The Problem It Solves](#the-problem-it-solves)
- [Core Innovation: Time-Keyed Encryption](#core-innovation-time-keyed-encryption)
- [Who Should Use It](#who-should-use-it)
- [What It Replaces and What It Does Not](#what-it-replaces-and-what-it-does-not)
- [Design Philosophy](#design-philosophy)

## What chronovault Is

chronovault is a Python package that gives you an encrypted, multi-tenant data layer using only local JSON files. It is not a hosted service and not a remote managed database. You install it with pip, import it in your application, and use it directly.

The storage engine writes AES-256-GCM encrypted envelopes to disk. Each file still has a `.json` extension, but record payloads are encrypted ciphertext. This includes collection data, indexes, token metadata, audit logs, tenant config, migration status, and transaction logs.

Core properties:

- No Docker requirement for local mode.
- No SQL/NoSQL server dependency.
- Works fully offline.
- Cross-platform (Linux, macOS, Windows).
- Designed for SaaS and enterprise internal systems.

> **Warning:** Losing your token makes data permanently unrecoverable. There is no reset mechanism.

## The Problem It Solves

Most systems are secured at the perimeter and monitored in transit, but fail at rest. Traditional deployments often store plaintext records in database files or snapshots. If those snapshots leak, your customers are exposed.

Common failure paths chronovault addresses:

- Backup leak: encrypted JSON envelopes are useless without your token and tenant context.
- Misconfigured database server: core operations can run locally with no exposed DB port.
- Overprivileged admin: role-scoped tokens + tenant-scoped key derivation reduce blast radius.
- Silent corruption: authenticated encryption catches tampering before plaintext is returned.

In practical terms, chronovault shifts your baseline from “protect a plaintext DB” to “store only ciphertext by default.”

## Core Innovation: Time-Keyed Encryption

Your token is your long-lived secret. chronovault combines that with `org_id` and the current Unix second to derive a per-second AES key via HKDF-SHA256.

Conceptually:

1. Build input material from `org_id:token`.
2. Use timestamp (seconds) as HKDF salt.
3. Use `chronovault-v1:{org_id}:{ts}` as HKDF info.
4. Derive 32-byte key for AES-256-GCM.
5. Encrypt/decrypt.
6. Discard key from scope.

This means keys evolve continuously over time.

> **Security:** The derived key is never stored anywhere. It is created, used, and discarded within a single function call.

## Who Should Use It

chronovault is a strong fit when you need local durability and strict at-rest secrecy with low operational overhead.

Best-fit teams:

- SaaS products storing customer PII.
- Healthcare and life-science teams handling sensitive records.
- Fintech/internal finance tools requiring immutable auditability.
- API platforms that need scoped service tokens and IP allowlists.

## What It Replaces and What It Does Not

What it can replace well:

- SQLite-style local persistence.
- Document-oriented CRUD workloads.
- Many operational reporting use cases with indexes and aggregation.

What it does not target as a first choice:

- Large analytical warehouses.
- Graph-native workloads.
- Ultra-low-latency distributed query clusters.

## Design Philosophy

- Security is foundational, not bolt-on.
- Plaintext at rest is unacceptable.
- Tampering must fail loudly.
- Writes must be atomic and lock-protected.
- Every critical operation should be auditable.
- Tenant boundaries are cryptographic and filesystem-level.

```python
import chronovault as cv

# Minimal mental model: connect, write, query.
db = cv.connect(token="<secure-token>", org_id="acme", path="~/.chronovault")
_id = db.users.insert({"name": "Alice", "role": "admin"})
print(db.users.find({"_id": _id}).execute())
```

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
