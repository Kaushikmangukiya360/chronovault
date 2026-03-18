# 04 CRUD Operations

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

## Create

```python
record_id = db.users.insert({"name": "Alice", "age": 30})
ids = db.users.insert_many([{"name": "Bob"}, {"name": "Carol"}])
```

## Read

```python
all_rows = db.users.find({}).execute()
one = db.users.find_one({"name": "Alice"})
count = db.users.count({"age": {"$gte": 18}})
```

## Update

```python
changed = db.users.update({"name": "Alice"}, {"age": 31})
changed_many = db.users.update_many({"role": "user"}, {"active": True})
```

## Upsert and Bulk

```python
db.users.upsert({"email": "x@y.com"}, {"name": "X", "age": 25})

result = db.users.bulk_write(
    [
        {"insert": {"name": "Dave"}},
        {"update": {"filter": {"name": "Bob"}, "set": {"age": 26}}},
        {"delete": {"filter": {"name": "Carol"}}},
    ]
)
print(result)
```

## Delete

```python
deleted = db.users.delete({"name": "Alice"})
deleted_many = db.users.delete_many({"active": False})
```

Operational notes:

- Writes are lock-protected and atomic.
- `_id`, `_created`, `_updated`, `_v` are managed metadata fields.
- Collection files remain encrypted JSON envelopes at rest.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
