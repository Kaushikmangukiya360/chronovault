# ChronoVault — Full Code Review: Bugs, Issues & Feature Gaps

> Reviewed every line of every file across all modules, tests, CI, and documentation.
> Branch: `main_work` · Language: Python 3.10+ · License: MIT

---

## Part 1 — Confirmed Bugs

### BUG-01 · `validate()` Never Marks Single-Use Tokens as Consumed
**File:** `chronovault/tenant/tokens.py` — `TokenService.validate()`

`validate()` checks `matched["used"]` and raises `TokenExpiredError` if the token was already consumed, but it **never calls `mark_used()`** itself. There is a separate `mark_used()` method that exists, but nothing in the public API flow ever calls it. The vault's `safe_call` and `_require` flows only call `validate()`. So a single-use token can be validated infinitely — it will never be marked as used unless the caller manually calls `mark_used()` afterwards, which no code in the codebase does.

**Fix:** Call `self.mark_used(token)` at the end of `validate()` when `matched["single_use"]` is True and validation passes.

---

### BUG-02 · `bulk_write()` Acquires Lock Per Operation, Causing Deadlock
**File:** `chronovault/storage/collection.py` — `Collection.bulk_write()`

`bulk_write()` loops over operations and calls `self.insert()`, `self.update()`, and `self.delete()` individually. Each of those methods calls `_acquire_rw()` which acquires a `FileLock`. Since `FileLock` from the `filelock` library is **not reentrant by default**, calling `bulk_write()` → `insert()` → `_acquire_rw()` will deadlock on the second operation because the lock is still held from the first operation in the same thread.

**Fix:** `bulk_write()` should acquire the lock once at the top, then call internal `_read_records()` / `_write_all()` methods directly, not the public `insert()`/`update()`/`delete()` wrappers.

---

### BUG-03 · `hmac.new()` Called Without Keyword Argument for `digestmod`
**File:** `chronovault/access/linker.py` — `Linker._sign()`

```python
digest = hmac.new(
    key=self.tenant_token.encode("utf-8"),
    msg=message.encode("utf-8"),
    digestmod=hashlib.sha256,
).hexdigest()
```

`hmac.new()` exists in Python's stdlib (it's an alias for `hmac.HMAC`), so this won't crash — but the **parameter name is `digestmod`, not a keyword-only arg**, and more critically the function signature is `hmac.new(key, msg=None, digestmod='')`. Passing `key=` as a keyword works, but it's non-idiomatic and fragile. The real risk here: if `digestmod` is ever accidentally omitted (e.g., during refactoring), Python 3.8+ raises a `RuntimeError` since `digestmod` is now mandatory. The canonical form is `hmac.new(key, msg, hashlib.sha256)` using positional args.

**Fix:** Use `hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()` or use `hmac.digest()`.

---

### BUG-04 · Dual Query Systems — `match_query` vs `match_record` — Inconsistent Results
**Files:** `chronovault/utils.py` (match_query) and `chronovault/query/operators.py` (match_record)

There are **two completely separate query evaluation systems** in the codebase:

- `match_query()` in `utils.py` — supports only `$gt` and `$in`, no nesting, no `$or`/`$and`/`$not`
- `match_record()` in `query/operators.py` — supports 13 operators, nested fields, `$or`, `$and`, `$not`, `$regex`, `$all`, `$size`, `$type`, etc.

`Collection.find()`, `Collection.update()`, `Collection.delete()`, and `Collection.upsert()` all use the **weak** `match_query()`. The `QueryBuilder` and `QueryEngine` use the **rich** `match_record()`. This means:

```python
# This works (goes via QueryBuilder → match_record):
db.users.find({"age": {"$gte": 18}}).execute()  # ✓

# This silently fails / returns wrong results (goes via Collection.find → match_query):
db.users.update({"age": {"$gte": 18}}, {"status": "adult"})  # ✗ $gte not supported
db.users.delete({"name": {"$regex": "^A"}})  # ✗ $regex ignored
```

Updates and deletes use a completely different (and far weaker) matcher than reads. This is a correctness bug — data will be silently wrong.

**Fix:** Replace `match_query()` usage in `collection.py` with `match_record()` from `query/operators.py`.

---

### BUG-05 · `join()` in `QueryBuilder` Bypasses RBAC — Reads Any Collection
**File:** `chronovault/query/builder.py` — `QueryBuilder.execute()`

```python
for spec in self._joins:
    foreign = self.collection.vault._collection(spec["collection"]).find({})
```

The join directly accesses `vault._collection(...)` and calls `.find({})` without going through `_require()`. A viewer-scoped token that only has access to `"orders"` can freely read `"users"`, `"payments"`, or any other collection by chaining `.join("users", ...)`. No permission check, no audit log entry.

**Fix:** Call `self.collection.vault._require(action="find", collection=spec["collection"])` before the join, and route through `safe_call` so the read is audited.

---

### BUG-06 · `AuditLogger` Has No Write Lock — Race Condition Under Concurrency
**File:** `chronovault/audit/logger.py`

`AuditLogger._read()` and `_write()` are not protected by any lock. Under concurrent usage (e.g., the 8-thread test in `test_concurrency.py` that inserts 40 records in parallel — each insert triggers an audit write), two threads can simultaneously read the same entry list, both append a new entry, and one will overwrite the other. The hash chain will also corrupt since `prev_hash` is computed from a stale state.

The `JsonStore` does have `_lock_for()` and lock-protected `write_encrypted_json()`, but it acquires a **per-file lock only during the actual write**, not across the read-compute-write cycle. Two threads can race between `_read()` and `_write()`.

**Fix:** Wrap the `append()` method with a `FileLock` (or reuse `JsonStore._lock_for()`) around the full read-modify-write cycle.

---

### BUG-07 · `Collection.exists()` Checks `data_000.json` but Shards May Start at a Different Number
**File:** `chronovault/storage/collection.py` — `Collection.exists()`

```python
def exists(self) -> bool:
    return self.data_path.exists()  # data_path = data_000.json
```

`ShardManager.write_records()` always writes starting from shard 0 (`data_000.json`), so this is currently safe. However, `Collection.drop()` deletes shards by listing them — and if for any reason shard 0 was deleted but shard 1 remains, `exists()` returns `False` even though data is still on disk. More practically: the `create_collection()` method in `vault.py` calls `coll._write_all([])` which creates `data_000.json`, but if a collection was created with only metadata (no data), `exists()` returns False. This inconsistency will cause `drop_collection()` to raise `CollectionNotFoundError` even if the collection directory exists.

**Fix:** Change `exists()` to check `self.collection_dir.exists()` or `self.meta_path.exists()`.

---

### BUG-08 · `_v` (Version Field) Never Incremented on Update
**File:** `chronovault/storage/collection.py` — `Collection.update()`

Records are created with `_v = 1`. The field exists and is documented as a version counter, but `update()` never increments it — only `_updated` timestamp changes. This means document versioning is non-functional. Optimistic concurrency checks that rely on `_v` will never detect conflicts.

**Fix:** Add `record["_v"] = record.get("_v", 1) + 1` in the update loop.

---

### BUG-09 · `join_records()` Validates Join Type After Using It
**File:** `chronovault/query/join.py`

```python
join_type = join_type.lower()
# ... 40 lines of logic using join_type ...
if join_type not in {"inner", "left", "right", "outer"}:
    raise ValueError("unsupported join type")
if join_type == "inner":
    return [row for row in result if row.get(right_alias) is not None]
return result
```

The validation of `join_type` happens **after** the entire join has been computed. An unsupported type like `"cross"` will silently produce a result identical to a `"right"` join (since both fall through to `return result`) before raising `ValueError`. The error is raised too late — after potentially expensive work — and the logic below the check is also wrong: the inner-join filter `row.get(right_alias) is not None` only runs for `"inner"`, meaning `"left"` and `"right"` types both return `result` which already includes unmatched rows. The inner filter at the bottom is therefore dead code for most types.

**Fix:** Validate `join_type` at the top of the function before any computation.

---

### BUG-10 · `ipaddress` Listed as a Dependency in `pyproject.toml`
**File:** `pyproject.toml`

```toml
dependencies = [
    ...
    "ipaddress",
    ...
]
```

`ipaddress` is a **Python standard library module since Python 3.3**. It does not exist as a separate PyPI package (there was an old backport, but it is unmaintained and archived). Listing it as a dependency will cause a pip warning or failure on some environments.

**Fix:** Remove `"ipaddress"` from the dependencies list.

---

### BUG-11 · `__version__` Is Missing from the Package
**File:** `chronovault/__init__.py`

The `pyproject.toml` declares `version = "1.0.0"`, but `chronovault/__init__.py` does not expose `__version__`. The README smoke test instructs users to run `python -c "import chronovault; print(chronovault.__version__)"` — this will raise `AttributeError`.

**Fix:** Add `__version__ = "1.0.0"` to `__init__.py`, or use `importlib.metadata.version("chronovault")`.

---

### BUG-12 · `_CollectionFacade.count()` Has Wrong RBAC Action
**File:** `chronovault/core/vault.py` — `_CollectionFacade.count()`

```python
def count(self, query: dict[str, Any] | None = None) -> int:
    self.vault._require(action="read", collection=self.name)
```

The `IAM.ACTION_MIN_ROLE` table maps `"read"` to `"viewer"`, which is correct. But `find()` uses `action="find"` which is also mapped to `"viewer"`. The inconsistency here is that `count()` uses `"read"` while logically identical operations like `find()` use `"find"`. This is not a crash, but it shows the IAM action namespace is ad hoc and could lead to real bugs if someone changes the mapping for `"read"` without realising `count()` depends on it.

---

## Part 2 — Design Issues & Code Quality Problems

### ISSUE-01 · No CI Test Step — Tests Are Never Run Automatically
**File:** `.github/workflows/python-publish.yml`

The CI workflow only builds and publishes to PyPI on release. There is **no test job** — `pytest` is never run automatically on push or pull request. 16 test files exist, but they provide zero CI safety guarantee. Any broken commit can be published directly to PyPI.

**Fix:** Add a separate `test` job that runs on `push` and `pull_request` to all branches, running `pip install -e ".[dev]"` followed by `pytest`.

---

### ISSUE-02 · Token Is Passed and Stored in Plaintext Throughout
**File:** `chronovault/core/vault.py`, `chronovault/tenant/tokens.py`

The raw token string is stored as `self.token` on the `ChronoVault` instance and passed to every storage and cipher call. This means the token lives in Python's heap for the entire session. In a long-running process, this is a standard trade-off — but there is no mechanism to wipe or rotate the in-memory token. For an "enterprise" database claiming security-first design, this deserves explicit documentation and ideally a `SecureString` wrapper or at minimum a comment.

---

### ISSUE-03 · `redacted_error_message()` Swallows All Error Context from Audit Log
**File:** `chronovault/utils.py`

```python
def redacted_error_message(err: Exception) -> str:
    _ = err
    return "operation failed"
```

Every error written to the audit log — whether it's a schema validation failure, a disk IO error, or a permission denial — gets logged as `"operation failed"`. This makes audit logs useless for debugging production incidents. The intent is clearly to avoid leaking internals, but the right approach is to allow safe error categories (e.g., the exception class name) while redacting message content.

---

### ISSUE-04 · Shard Cache Is Per-`ShardManager` Instance, Not Per-Collection
**File:** `chronovault/storage/shard.py`

Each `Collection` instantiation creates a new `ShardManager`, which creates a new `_cache`. Since `_CollectionFacade` creates a new `Collection` object on every method call (`vault._collection(name)` in `core/vault.py`), the shard cache is **never reused between calls**. All the cache invalidation logic and the `CACHE_TTL_SECONDS`/`CACHE_MAX_SHARDS` constants are effectively dead.

**Fix:** Cache `Collection` or `ShardManager` instances at the `ChronoVault` level, keyed by collection name.

---

### ISSUE-05 · `_CollectionFacade` Is Not Thread-Safe When Shared Across Threads
**File:** `chronovault/core/vault.py`

The `ChronoVault.__getattr__` creates a new `_CollectionFacade` on each attribute access, which is safe. But if a user stores a reference to `db.users` and shares it across threads, the facade itself holds a reference to the vault which shares `_audit`, `_tokens`, and `_tenant_root`. The audit logger has no lock (see BUG-06), so concurrent facade usage leads to data races.

---

### ISSUE-06 · Aggregator `$sort` Is Not Stable Across Python Versions
**File:** `chronovault/query/aggregator.py`

The `$sort` stage uses Python's `list.sort()` which is stable. However, the multi-field sort applies each field independently in a reversed loop:

```python
for field, direction in reversed(sort_fields):
    out.sort(key=lambda r: self._extract(r, field), ...)
```

This is correct for multi-key stable sort, but `self._extract(r, field)` returns `None` for missing fields — and comparing `None < int` raises `TypeError` in Python 3. Any record missing the sort field will crash the aggregation. There is no `None`-safe comparator.

**Fix:** Use a sentinel like `(0, None)` tuple or provide a `key_func` that handles `None`.

---

### ISSUE-07 · README Points to Wrong Clone Path
**File:** `readme.md`

```bash
git clone https://github.com/kaushikmangukiya360/chronovault.git
cd chronovault/chron/chronovault  # <-- does not exist
```

The directory `chron/` does not exist in the repo. The correct path after cloning is just `cd chronovault/`.

---

### ISSUE-08 · `ensure_ip_allowed()` Returns `False` for Empty Allowlist
**File:** `chronovault/utils.py`

```python
def ensure_ip_allowed(source_ip: str, ip_allowlist: list[str]) -> bool:
    if not ip_allowlist:
        return False
```

An empty IP allowlist returns `False` (deny all), but `validate_ip_allowlist()` raises `ValueError` for an empty list. These two functions have inconsistent empty-list semantics. The token validator uses `matched.get("ip_allowlist", ["*"])` as a default, so in practice this is never reached — but it is a latent footgun.

---

### ISSUE-09 · `TokenService.validate()` Raises `UnauthorizedIPError` for Collection Scope Mismatch
**File:** `chronovault/tenant/tokens.py`

```python
if collection is not None and "*" not in allowed_collections and collection not in allowed_collections:
    raise UnauthorizedIPError("token collection scope does not allow requested collection")
```

A collection-scope violation raises `UnauthorizedIPError` — the same exception as an IP binding failure. The correct exception is `PermissionDeniedError`. This makes it impossible for callers to distinguish between "wrong IP" and "wrong collection scope" errors.

**Fix:** Raise `PermissionDeniedError` for collection scope violations.

---

### ISSUE-10 · `ChronoVault.serve()` Blocks the Calling Thread
**File:** `chronovault/core/vault.py` — `ChronoVault.serve()`

`uvicorn.run()` is called directly in `serve()` — this is a blocking call that never returns. There is no option to run the server in a background thread, get back a handle to shut it down, or configure it as an async server. For any integration testing or embedding use-case this makes `serve()` unusable without spawning a subprocess.

---

## Part 3 — Missing Features Referenced in Docs/Examples but Not Implemented

### MISSING-01 · ORM Layer Does Not Exist
**File:** `HOW_TO_USE/examples/11_orm_models.py`

```python
from chronovault.orm import Model, StringField, IntField  # ImportError
```

The example file imports from `chronovault.orm`, which has **no corresponding module**. There is no `orm.py` or `orm/` package. The guide `HOW_TO_USE/guides/19_ORM.md` documents this as a feature.

---

### MISSING-02 · Transaction Support Does Not Exist
**File:** `HOW_TO_USE/examples/10_transactions_demo.py`, `HOW_TO_USE/guides/11_TRANSACTIONS.md`

The example comments: *"Transaction manager API is release/profile dependent."* There is no transaction module, no `begin()`/`commit()`/`rollback()` API, and no `TransactionError`/`TransactionConflictError` usage anywhere (both exception classes are defined but never raised). The exceptions file defines `TransactionError` and `TransactionConflictError`, hinting at planned work that was never completed.

---

### MISSING-03 · Backup and Restore Are Not Implemented
**File:** `HOW_TO_USE/guides/21_BACKUP_RESTORE.md`

`BackupError` and `RestoreError` are defined in `exceptions.py` but never used. There is no `backup()` or `restore()` method on `ChronoVault`.

---

### MISSING-04 · Migration System Is Not Implemented
**File:** `HOW_TO_USE/guides/20_MIGRATIONS.md`

`MigrationError` is defined but never used. No migration runner, no schema versioning, no `migrate()` method exists.

---

### MISSING-05 · Full-Text Search Is Not Actually Full-Text Search
**File:** `chronovault/query/builder.py` — `QueryBuilder.search()`

The `.search()` method performs a naive in-memory substring scan across all string-type values. There is no inverted index, no tokenization, no stemming, no ranking beyond hit-count ratio, and no persistence. The guide `HOW_TO_USE/guides/10_FULL_TEXT_SEARCH.md` describes it as a first-class feature. `FullTextSearchError` is defined but never raised by this implementation.

---

### MISSING-06 · Django Integration Does Not Work
**File:** `HOW_TO_USE/integrations/DJANGO_INTEGRATION.md`, `HOW_TO_USE/examples/12_django_app.py`

The Django integration example and guide describe a DB backend for Django's ORM layer. This requires implementing Django's database backend interface (`DatabaseWrapper`, `DatabaseCreation`, etc.). No such implementation exists in the package.

---

### MISSING-07 · gRPC Integration Does Not Exist
**File:** `HOW_TO_USE/integrations/GRPC_INTEGRATION.md`

A gRPC server integration is documented but there is no `.proto` file, no gRPC server implementation, and no `grpc` dependency in `pyproject.toml`.

---

### MISSING-08 · `_v` Document Versioning Is Non-Functional
As noted in BUG-08, the `_v` field is initialised to `1` on insert but never incremented on update. Optimistic locking and change-history features that `_v` implies don't work.

---

### MISSING-09 · No `$lookup` / Pipeline Join in Aggregator
**File:** `chronovault/query/aggregator.py`

The aggregation pipeline supports `$match`, `$group`, `$sort`, `$limit`, `$skip`, `$project`, `$unwind`, `$count`, and `$addFields`. MongoDB-style `$lookup` (cross-collection join in a pipeline) is not supported. The join feature only exists on the `QueryBuilder` level, not in aggregation.

---

### MISSING-10 · No Index-Accelerated Query Execution
**File:** `chronovault/query/engine.py`, `chronovault/storage/index.py`

`IndexManager` maintains field-value hash maps (index entries). `IndexManager.lookup()` can return candidate record IDs for a given field/value. But `QueryEngine.execute()` never uses `lookup()` — it always does a full sequential scan of all shards. Indexes exist and are maintained on write, but are **never consulted on read**. They provide zero query performance benefit today.

---

## Part 4 — Feature Ideas Worth Implementing

### FEATURE-01 · Pagination Cursor / Bookmark API
Currently, `skip()` + `limit()` requires re-scanning from the start on each call. A cursor-based pagination token (encoding the last seen `_id` and sort position) would be far more efficient for large collections.

### FEATURE-02 · TTL-Based Automatic Record Expiry
Each record could carry a `_expires_at` field, and a background sweep (or on-read filter) could automatically purge expired records. This is useful for session data, cache-layer use cases, and time-bounded audit staging.

### FEATURE-03 · Encrypted Field-Level Access Control
Rather than only collection-level RBAC, field-level encryption with per-field keys would allow a viewer role to read a record without seeing sensitive fields (e.g., `salary`, `ssn`), which are decryptable only by admin-role tokens.

### FEATURE-04 · Change Streams / Webhooks
An event subscription API (`db.users.on("insert", callback)`) would let application code react to data changes without polling. This pairs naturally with the existing audit log infrastructure.

### FEATURE-05 · Index-Backed Query Execution (Wire up existing IndexManager)
The `IndexManager.lookup()` method exists but is never called by `QueryEngine`. Adding an index-lookup fast path for exact-match and `$in` queries would dramatically improve performance on large sharded collections.

### FEATURE-06 · Proper Full-Text Search with an Inverted Index
Replace the current substring scan with a real inverted index: tokenise string fields at write time, store term → record ID mappings, and support BM25 or TF-IDF scoring at query time.

### FEATURE-07 · Schema Migration Runner
Implement the documented migration system: a `migrations/` directory, version tracking in encrypted tenant metadata, up/down migration functions, and a `db.migrate()` call or CLI `chronovault migrate` command.

### FEATURE-08 · Streaming / Async API
The current API is fully synchronous. An `async def` variant or an async context manager (`async with db.users.find({})` as an async generator) would allow use in async frameworks (FastAPI, Starlette) without blocking the event loop.

### FEATURE-09 · Encrypted Backup / Restore
Implement `db.backup(output_path)` that exports all encrypted shards and metadata as a portable archive, and `db.restore(archive_path)` that re-imports them — both using the existing encryption primitives.

### FEATURE-10 · Key Derivation Caching with Epoch Granularity
`derive_key()` is called on every read and write, and HKDF-SHA256 is computationally cheap but not free. Keys could be cached in a bounded LRU keyed by `(org_id, tenant_token_hash, epoch_bucket)` to avoid redundant derivations during bulk reads of same-epoch shards.

---

## Summary Table

| Category | Count |
|---|---|
| Confirmed bugs (correctness / crash / security) | 12 |
| Design / code quality issues | 10 |
| Documented features not implemented | 10 |
| Suggested new features | 10 |

**Highest priority to fix:** BUG-01 (single-use tokens never consumed), BUG-02 (bulk_write deadlock), BUG-04 (two query systems), BUG-05 (join bypasses RBAC), BUG-06 (audit race condition), ISSUE-01 (no CI tests).