# Shard System

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

Shards cap file growth and keep encrypted file operations manageable.

- Naming: `data_{shard:03d}.json`
- Capacity: `SHARD_SIZE = 10_000`
- Read: parallel scan with bounded workers
- Cache: TTL-LRU for decrypted shard records

```python
# conceptual behavior
# data_000.json: records 0-9999
# data_001.json: records 10000-19999
```

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
