# 11 Transactions

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

chronovault transaction mode uses an encrypted write-ahead log for atomic commit/rollback.

```python
with db.transaction() as tx:
    tx.accounts.update({"_id": "acc_A"}, {"balance": 900})
    tx.accounts.update({"_id": "acc_B"}, {"balance": 1100})
    tx.ledger.insert({"from": "acc_A", "to": "acc_B", "amount": 100})
```

Behavior:

- WAL entry written first.
- Commit applies operation set atomically.
- Exceptions trigger rollback using before snapshots.
- Startup performs WAL recovery.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
