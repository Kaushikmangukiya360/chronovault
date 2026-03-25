# Next Part Execution Checklist

## Goal
Track the next backlog after completing the initial roadmap.

## Phase F: Production gRPC Transport
- [x] Add protobuf contracts for connect/find/insert/update/delete/health
- [x] Generate Python stubs and wire service interfaces
- [x] Implement grpcio network server (not in-process handler only)
- [x] Add token-scoped auth interceptors for gRPC requests
- [x] Add TLS/mTLS runtime configuration for transport security
- [x] Add gRPC transport integration tests
- [ ] Add certificate-backed TLS/mTLS integration tests

## Phase G: Migration Execution Engine
- [ ] Add migration discovery loader from migrations directory
- [ ] Execute migration up/down callables with idempotency checks
- [ ] Add migration dry-run mode
- [ ] Add rollback safety checks and error reporting
- [ ] Add migration execution tests

## Phase H: CLI Lifecycle Expansion
- [ ] Add index command family: create/drop/list
- [ ] Add schema command family: set/get/drop
- [ ] Add stats command with shard/index/storage details
- [ ] Add transaction diagnostics command family
- [ ] Add CLI tests for all new command groups

## Phase I: Framework Integration Completion
- [ ] Complete Django backend behavior beyond skeleton interfaces
- [ ] Add Django compatibility tests with sample project
- [ ] Expand FastAPI integration with request token extraction
- [ ] Add per-request tenancy and role mapping helpers
- [ ] Add integration examples in HOW_TO_USE docs

## Phase J: Performance and Security Hardening
- [ ] Add benchmark suite for CRUD/query/search/backup workflows
- [ ] Add profile-driven optimization notes for hot paths
- [ ] Add optional encrypted-only export policy mode
- [ ] Add token/key rotation automation policy tools
- [ ] Add threat simulation tests for hardening validation

## Phase K: Visualization and Monitoring UX
- [ ] Add visualization exporter for audit trends and event rates
- [ ] Add shard and storage utilization visualization payloads
- [ ] Add query performance visualization payloads
- [ ] Add tenant growth and activity timeline payloads
- [ ] Add visualization integration examples (FastAPI/chart frontends)
- [ ] Add tests for visualization payload integrity

## Next Release Gate
- [ ] Full test suite remains green (`python -m pytest -q`)
- [x] New gRPC transport tests pass locally
- [ ] New gRPC transport tests pass in CI
- [ ] New CLI lifecycle commands documented and tested
- [ ] Integration docs updated for Django and FastAPI completion
- [ ] Performance benchmark report captured and reviewed
- [ ] Visualization docs and examples validated end-to-end

## Notes
Use this checklist with:
- [POST_CHECKLIST_MISSING_PARTS.md](POST_CHECKLIST_MISSING_PARTS.md)
- [SERVICE_MODE_OPERATIONS.md](SERVICE_MODE_OPERATIONS.md)
