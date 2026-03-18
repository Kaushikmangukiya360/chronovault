# API Reference

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

## Connection

### `cv.connect(token: str, org_id: str, path: str, role: str = "admin", ip_allowlist: list[str] | None = None, server_mode: bool = False, server_url: str | None = None, log_level: str = "WARNING") -> ChronoVault`

Creates a vault session for one tenant context.

```python
import chronovault as cv

db = cv.connect(token="<token>", org_id="acme", path="~/.chronovault")
```

## CRUD

- `db.<col>.insert(data: dict) -> str`
- `db.<col>.insert_many(data_list: list[dict]) -> list[str]`
- `db.<col>.upsert(filter: dict, data: dict) -> str`
- `db.<col>.bulk_write(operations: list[dict]) -> dict[str, int]`
- `db.<col>.find(filter: dict) -> QueryBuilder`
- `db.<col>.find_one(filter: dict) -> dict | None`
- `db.<col>.count(filter: dict | None = None) -> int`
- `db.<col>.update(filter: dict, data: dict) -> int`
- `db.<col>.update_many(filter: dict, data: dict) -> int`
- `db.<col>.delete(filter: dict) -> int`
- `db.<col>.delete_many(filter: dict) -> int`

## QueryBuilder

- `.sort(field, direction=1)`
- `.sort([(field, direction), ...])`
- `.limit(n)`
- `.skip(n)`
- `.project(fields_dict)`
- `.join(collection, on, foreign_key, join_type="inner")`
- `.search(query_string)`
- `.execute()`
- `.first()`
- `.count()`

## Aggregation

`db.<col>.aggregate(pipeline: list[dict]) -> list[dict]`

## Schema

- `set_schema(schema_dict)`
- `get_schema()`
- `drop_schema()`

## Indexes

- `create_index(field_or_fields, unique=False)`
- `drop_index(name)`
- `list_indexes()`

## Collection Admin

- `list_collections()`
- `create_collection(name)`
- `drop_collection(name)`
- `collection_exists(name)`
- `rename_collection(old, new)`

## Security/Admin

- `issue_token(...)`
- `revoke_token(name)`
- `list_tokens()`
- `generate_link(...)`
- `serve(port, host)`
- `audit_log.tail(n)`
- `audit_log.filter(...)`
- `audit_log.verify_integrity()`
- `audit_log.export(path)`
- `rotate_all_keys()`
- `tenant_info()`
- `export_compliance_report(output, standard="SOC2")`

> **Note:** Some advanced methods (FTS, WAL transactions, migration, backup/restore, ORM integrations) are version-gated by release and deployment profile.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
