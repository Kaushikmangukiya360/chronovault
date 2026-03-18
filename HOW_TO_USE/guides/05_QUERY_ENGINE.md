# 05 Query Engine

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

chronovault query execution is in-memory on decrypted records and follows a deterministic pipeline:

1. Filter
2. Sort
3. Skip
4. Limit
5. Project

```python
results = (
    db.users
    .find({"age": {"$gte": 18}, "country": "India"})
    .sort([("age", -1), ("name", 1)])
    .skip(0)
    .limit(20)
    .project({"name": 1, "email": 1, "_id": 0})
    .execute()
)
```

Supported operators include `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin`, `$exists`, `$regex`, `$or`, `$and`, `$not`, `$all`, `$size`, `$type`.

Nested path example:

```python
db.users.find({"address.city": "Mumbai"}).execute()
```

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
