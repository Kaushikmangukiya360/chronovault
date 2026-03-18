# 08 Indexing

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

Indexes speed up lookups and enforce uniqueness.

```python
db.users.create_index("email", unique=True)
db.users.create_index("age")
db.users.create_index(["country", "city"])
print(db.users.list_indexes())
db.users.drop_index("age")
```

Index design:

- Field values are hashed (SHA-256) before index keying.
- Unique indexes reject duplicates with `UniqueConstraintError`.
- Index files are encrypted at rest.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
