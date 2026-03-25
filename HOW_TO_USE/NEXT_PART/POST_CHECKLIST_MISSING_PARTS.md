# Post-Checklist Missing Parts (Enterprise Backlog)

## Why this document exists
The current checklist is fully completed for the scoped implementation plan. This document tracks additional enterprise-grade gaps that remain if ChronoVault aims to be a production replacement for large-scale database platforms.

## Remaining high-priority gaps

### 1) Production gRPC transport
Status: Mostly implemented
- Protobuf contracts and generated Python stubs are implemented.
- grpcio network transport server/client is implemented.
- Token-scoped metadata auth checks and TLS/mTLS runtime configuration are implemented.
- Remaining: certificate-backed transport integration tests for TLS/mTLS handshake paths.

Target:
- Add certificate fixture suite and end-to-end TLS/mTLS transport tests.

### 2) Migration execution engine
Status: Partially implemented
- Migration version tracking exists.
- Missing migration discovery and execution from migration files/functions.

Target:
- Add migration loader from migrations directory.
- Execute deterministic up/down functions with idempotency guard.
- Add rollback safety and migration dry-run mode.

### 3) CLI advanced lifecycle coverage
Status: Partially implemented
- Core CLI commands exist.
- Missing richer commands for index/schema lifecycle breadth and diagnostics.

Target:
- Add `index create/drop/list` command family.
- Add `schema set/get/drop` command family.
- Add `stats` and transaction diagnostics commands.

### 4) Django integration completeness
Status: Skeleton only
- Wrapper skeleton exists but not full backend behavior.

Target:
- Implement required backend interfaces for practical model/query lifecycle.
- Add compatibility tests with sample Django project.

### 5) FastAPI integration depth
Status: Basic helper implemented
- Dependency helper exists.
- Missing middleware/auth integration package patterns.

Target:
- Add helper for request token extraction and scoped DB context.
- Add examples for per-request tenancy and role mapping.

### 6) Performance and scale hardening
Status: Partial
- Basic sharding and cache exist.
- Missing benchmark suite and load-focused tuning strategy.

Target:
- Add benchmark scripts for CRUD/query/search/backup paths.
- Add profile-driven optimization report for hot paths.

### 7) Security hardening beyond current scope
Status: Partial
- Core crypto design and IP/token controls are implemented.
- Missing advanced deployment hardening patterns.

Target:
- Add optional encrypted-only export policy mode.
- Add key/token rotation policy automation guidance.
- Add security threat simulation test scenarios.

### 8) Visualization and dashboard support
Status: Not implemented
- No visualization-focused data export layer.
- No dashboard integration examples for operational monitoring.

Target:
- Add chart-ready payload APIs for audit trends, query latency, shard utilization, and tenant growth.
- Add example visualization pipeline (FastAPI + frontend chart client).
- Add operational dashboards guide for incident response and capacity planning.

## Suggested execution order
1. Migration execution engine
2. CLI advanced lifecycle coverage
3. Django integration completeness
4. FastAPI integration depth
5. Performance and scale hardening
6. Security hardening advanced controls
7. Visualization and dashboard support

## Validation targets
- Maintain full regression pass (`python -m pytest -q`) after each milestone.
- Keep operational docs synchronized with each new deployment capability.
