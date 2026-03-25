# ChronoVault Gaps and Next Part Plan

## Purpose
This document tracks what is already strong in ChronoVault, what is still missing for full enterprise goals, and what to build next in execution order.

For additional enterprise backlog after checklist completion, see:
- [POST_CHECKLIST_MISSING_PARTS.md](POST_CHECKLIST_MISSING_PARTS.md)

## Current Baseline (What Exists)
ChronoVault already has these core capabilities:
- Time-keyed encryption using HKDF + AES-GCM
- Encrypted JSON storage envelopes on disk
- Collection CRUD APIs
- Query builder with filtering, sorting, projection, joins, aggregation
- Schema validation (core constraints)
- Token issuance, revocation, TTL, and IP allowlist checks
- Audit log with chain-hash verification
- Link generation and validation with HMAC
- CLI for core admin operations
- Shard manager and cache foundations

## Confirmed Gaps (Missing or Partial)

### Current State Summary
- Initial roadmap checklist is completed and validated.
- This document now focuses on what remains for enterprise-grade completion.
- Detailed post-checklist backlog: [POST_CHECKLIST_MISSING_PARTS.md](POST_CHECKLIST_MISSING_PARTS.md)

### 1) Transactions and WAL (Partial)
Status: Implemented (current checklist scope)
- Transaction context manager with commit/rollback semantics: Implemented
- WAL-based startup pending-transaction recovery: Implemented
- Conflict handling for concurrent transaction updates: Implemented (pending transaction guard)

Why it matters:
- Without this, ChronoVault cannot claim strong ACID behavior for multi-step writes.

### 2) Full-Text Search Module (Missing)
Status: Implemented (core)
- Dedicated search package with tokenized inverted index: Implemented
- Query text relevance scoring pipeline: Implemented

Why it matters:
- Required to replace most Mongo-like document search usage.

### 3) Migration System (Missing)
Status: Partially implemented
- Migration registry/tracking manager: Implemented
- Up/down migration status tracking per collection: Implemented
- Versioned data transformation runner from migration files: Not implemented

Why it matters:
- Schema/version evolution is essential in SaaS/MNC lifecycle upgrades.

### 4) Backup/Restore Manager (Missing)
Status: Implemented
- First-class encrypted backup export/import pipeline: Implemented
- Overwrite-safe restore flow with force protection: Implemented

Why it matters:
- Business continuity and disaster recovery are mandatory at enterprise scale.

### 5) ORM Layer (Missing)
Status: Implemented (base)
- Model base class and field classes: Implemented
- Model-driven save/find/delete workflow: Implemented

Why it matters:
- Important for developer adoption and app-integration speed.

### 6) Framework Integrations (Missing)
Status: Partially implemented
- Django backend adapter skeleton: Implemented
- FastAPI dependency/helper integration module: Implemented

Why it matters:
- Needed for real production adoption in existing service stacks.

### 7) gRPC Server Mode
Status: Implemented (transport baseline)
- grpc_server component: Implemented (in-process handler module)
- Production protobuf contracts: Implemented
- Generated protobuf stubs and servicer wiring: Implemented
- grpcio network transport server/client: Implemented
- Token-scoped metadata auth checks: Implemented
- TLS/mTLS runtime configuration: Implemented
- Remaining: certificate-backed integration tests for TLS/mTLS handshake paths

Why it matters:
- Many enterprise internal services prefer gRPC over REST.

### 8) CLI Coverage (Partial)
Status: Partially implemented
- Existing CLI supports init/status/collections list/audit/token/rotate/serve/export-report/health/backup/restore/migrate
- Missing advanced commands for stats detail, index lifecycle breadth, schema lifecycle breadth, and transaction diagnostics

Why it matters:
- Platform operators need full lifecycle commands for production operations.

### 9) Security Hardening Opportunities (Partial)
Status: Partial
- Export commands can intentionally produce plaintext export artifacts
- Token-hash comparison path now uses constant-time comparison
- Collection-scope denial now uses permission-denied semantics

Why it matters:
- Enterprise security posture benefits from strict and consistent behavior across all auth and export paths.

### 10) Environment Reliability Gap (Operational)
Status: Mitigated for current workflow
- Startup dependency preflight command added
- Deterministic CI workflow added for Python 3.10 and 3.11

Why it matters:
- Release confidence requires deterministic environment setup and dependency health checks.

### 11) Visualization and Observability UX (Missing)
Status: Not implemented
- No first-class visualization module for timelines, shard heatmaps, query metrics, or tenant usage views.
- No dashboard-oriented export for analytics/monitoring pipelines.

Why it matters:
- Teams operating ChronoVault at scale need visual diagnostics for performance, security events, and growth planning.

## Next Part Build Order (Recommended)

### Phase F: Production Transport
1. Completed: protobuf/gRPC network transport server and generated stubs.
2. Completed: token-scoped auth checks and TLS/mTLS runtime configuration.
3. Remaining: add certificate-based TLS/mTLS integration tests.

### Phase G: Migration Execution
1. Execute real migration files/functions beyond version tracking.
2. Add dry-run and rollback-safe execution semantics.

### Phase H: CLI and Integrations Completion
1. Add remaining CLI lifecycle commands (index/schema/stats/diagnostics).
2. Complete Django backend beyond skeleton.
3. Expand FastAPI integration patterns for request-scoped tenancy.

### Phase I: Hardening and Performance
1. Add benchmark and profiling suites.
2. Add advanced security policy controls and threat simulation tests.

### Phase K: Visualization
1. Add visualization data exporter (audit trends, shard distribution, query mix, tenant growth).
2. Add dashboard integration examples (FastAPI endpoint + chart-ready payloads).
3. Add guide and operational playbook for visualization workflows.

## Definition of Done for Full Enterprise Milestone
ChronoVault can be considered enterprise-complete when all below are true:
- Transactions and WAL recovery are live and tested
- Backup/restore and migration workflows are complete
- FTS and ORM are available for application developers
- REST and gRPC service modes are both available
- CLI supports full lifecycle operation flows
- Security hardening checklist is fully green
- Test matrix passes in a clean reproducible environment

## Practical Recommendation
For immediate production pilot:
- Use current ChronoVault for encrypted JSON CRUD workloads with strict token/IP controls
- Do not yet market as a full PostgreSQL/Mongo replacement until post-checklist phases are completed
- Prioritize production gRPC transport, migration execution engine, and visualization tooling

## Traceability to Current Code
Reference implementation files already present:
- [chronovault/core/vault.py](../../chronovault/core/vault.py)
- [chronovault/storage/collection.py](../../chronovault/storage/collection.py)
- [chronovault/query/operators.py](../../chronovault/query/operators.py)
- [chronovault/query/aggregator.py](../../chronovault/query/aggregator.py)
- [chronovault/query/join.py](../../chronovault/query/join.py)
- [chronovault/tenant/tokens.py](../../chronovault/tenant/tokens.py)
- [chronovault/audit/logger.py](../../chronovault/audit/logger.py)
- [chronovault/access/linker.py](../../chronovault/access/linker.py)
- [chronovault/cli.py](../../chronovault/cli.py)

---
Generated as Next Part planning documentation for ChronoVault evolution.
