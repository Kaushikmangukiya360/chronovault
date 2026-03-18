# Exceptions Reference

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

| Exception | Raised When | Typical Handling |
|---|---|---|
| VaultError | Base class for all vault errors | Catch for top-level fallback |
| AuthenticationError | Invalid token credentials | Rotate token, verify auth source |
| UnauthorizedIPError | Source IP not allowlisted | Update allowlist or request path |
| PermissionDeniedError | Role lacks action permission | Use scoped admin flow |
| TokenExpiredError | TTL exceeded | Re-issue token |
| TokenRevokedError | Revoked token used | Replace credential |
| InvalidTokenError | Invalid role/format on issuance | Correct token request fields |
| CollectionNotFoundError | Missing collection | Create or fix collection name |
| RecordNotFoundError | Missing target record | Re-check filter semantics |
| VaultLockTimeoutError | Lock timeout on write | Retry with backoff |
| TamperDetectedError | GCM/auth envelope mismatch | Investigate file integrity |
| AuditIntegrityError | Audit chain hash mismatch | Trigger incident response |
| TenantNotFoundError | Missing tenant root/config | Bootstrap tenant correctly |
| TenantAlreadyExistsError | Duplicate create | Reuse existing tenant |
| SchemaValidationError | Record fails schema rules | Correct payload |
| IndexAlreadyExistsError | Duplicate index create | Skip or rename index |
| IndexNotFoundError | Missing index drop/read | Check index list first |
| UniqueConstraintError | Unique index collision | Handle duplicates upstream |
| TransactionError | General transaction failure | Retry or rollback |
| TransactionConflictError | Serializable conflict | Retry transaction |
| ShardError | Shard read/write failure | Repair shard and restore |
| MigrationError | Migration invalid/failing | Fix migration code and rerun |
| BackupError | Backup export failed | Verify path and permissions |
| RestoreError | Restore import failed | Check token/org compatibility |
| QueryError | Invalid operator/filter | Validate query syntax |
| FullTextSearchError | FTS index/query issue | Rebuild FTS index |
| ServerConnectionError | Daemon communication failed | Check host/port/token |

```python
try:
    rows = db.users.find({"email": "alice@example.com"}).execute()
except Exception as exc:
    print(type(exc).__name__, str(exc))
```

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
