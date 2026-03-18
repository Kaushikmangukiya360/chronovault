# Storage Format

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

## Common Envelope

All files persist as encrypted JSON envelopes:

```json
{
  "v": 1,
  "org_id": "acme-corp",
  "purpose": "data|index|audit|tokens|config|meta",
  "ts": 1710000000,
  "nonce": "...",
  "tag": "...",
  "ct": "..."
}
```

## File Catalog

| Path | Purpose | Writer |
|---|---|---|
| tenants/{org}/config.json | tenant config | tenant manager |
| tenants/{org}/tokens.json | token metadata | token service |
| tenants/{org}/audit.json | immutable audit | audit logger |
| tenants/{org}/wal.json | transaction WAL | transaction manager |
| tenants/{org}/keys_meta.json | key rotation history | rekeyer |
| tenants/{org}/migrations.json | migration status | migration runner |
| collections/{col}/meta.json | schema and collection metadata | collection layer |
| collections/{col}/index.json | hashed index map | index manager |
| collections/{col}/fts.json | hashed token inverted index | FTS module |
| collections/{col}/data_000.json | shard payload | shard manager |

## data_000 Plaintext Payload Example

```json
{
  "records": [
    {
      "_id": "uuid4-string",
      "_created": "2026-03-18T10:00:00Z",
      "_updated": "2026-03-18T10:00:00Z",
      "_v": 1,
      "name": "Alice",
      "email": "alice@example.com",
      "age": 30
    }
  ],
  "shard": 0,
  "total_shards": 1
}
```

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
