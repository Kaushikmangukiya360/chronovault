# 10 Full Text Search

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

Use full-text search for tokenized keyword retrieval.

```python
db.products.enable_fts(fields=["name", "description"])
rows = (
    db.products
    .search("wireless bluetooth headphones")
    .sort("_score", -1)
    .limit(10)
    .execute()
)
```

Combined search and filtering:

```python
db.products.find({"category": "electronics"}).search("wireless").execute()
```

FTS index stores hashed tokens and is encrypted at rest.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
