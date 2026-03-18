# 22 Performance

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

Performance tuning checklist:

- Create indexes on high-cardinality filter fields.
- Use projection to reduce payload size.
- Use `.limit()` aggressively for UI endpoints.
- Enable FTS only on relevant text fields.
- Keep shard count balanced and monitor growth.

```python
# Good pattern for paginated APIs
page = db.orders.find({"status": "paid"}).sort("_created", -1).skip(200).limit(50).project({"amount": 1, "user_id": 1}).execute()
```

Shard scanning is parallelized with bounded workers. Decrypted shard cache TTL reduces repeated decrypt overhead for read-heavy workloads.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
