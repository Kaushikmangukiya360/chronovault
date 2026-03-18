# 17 Access Links

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

Generate signed, time-limited links for controlled data access.

```python
link = db.generate_link(
    collection="invoices",
    ttl=300,
    ip="203.0.113.5",
    permissions=["read"],
    single_use=True,
)
print(link)
```

```python
db.serve(port=8471, host="0.0.0.0")
```

Links are HMAC signed and validated using constant-time comparison.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
