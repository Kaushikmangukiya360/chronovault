# 07 Joins

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

chronovault supports in-memory joins across collections.

```python
rows = (
    db.orders
    .find({"status": "paid"})
    .join("users", on="user_id", foreign_key="_id", join_type="inner")
    .project({"amount": 1, "users.name": 1, "users.email": 1})
    .execute()
)
```

Join types:

- `inner`: only rows with matches.
- `left`: all left rows; unmatched right is `None`.
- `right`: all right rows; unmatched left synthesized.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
