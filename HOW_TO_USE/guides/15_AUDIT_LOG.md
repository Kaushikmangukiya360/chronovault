# 15 Audit Log

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

Audit entries are append-only and chain-hashed.

```python
entries = db.audit_log.tail(n=100)
filtered = db.audit_log.filter(event="collection.write", collection="invoices")
ok = db.audit_log.verify_integrity()
db.audit_log.export("audit_export.json")
```

Each event includes `prev_hash` and `chain_hash`. Any tamper attempt breaks verification.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
