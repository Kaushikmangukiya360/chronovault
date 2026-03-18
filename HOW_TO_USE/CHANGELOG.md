# Changelog

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

All notable changes to chronovault are documented here.  
Format based on Keep a Changelog. Versioning follows Semantic Versioning.

## [Unreleased]

- gRPC server support
- Django backend adapter
- Full-text search scoring improvements

## [1.0.0] — 2026-03-18

### Added

- AES-256-GCM encryption for all data files
- Time-keyed HKDF-SHA256 key derivation
- Multi-tenant isolation with org_id namespacing
- RBAC access control: admin, editor, viewer
- IP binding on service tokens
- Immutable audit log with chain hash
- Rich query engine with 13 operators
- Chainable QueryBuilder: sort, limit, skip, project
- Aggregation pipeline: $match $group $sort $limit
- Cross-collection joins: inner, left, right
- Field indexing with unique constraint support
- JSON schema validation on insert/update
- Full-text search with encrypted inverted index
- ACID transactions with JSON write-ahead log
- Shard management: 10,000 records per file
- LRU cache for decrypted shards (30s TTL)
- HMAC-signed access links with TTL
- Versioned migration system
- Encrypted backup and restore
- FastAPI HTTP daemon server
- ORM model layer
- Full CLI with 25+ commands
- Complete test suite

### Security

- Zero plaintext on disk — every file encrypted
- Key never stored — derived and discarded per operation
- GCM authentication tag — tamper detection on every read
- Zero-knowledge design — platform operator cannot read data

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
