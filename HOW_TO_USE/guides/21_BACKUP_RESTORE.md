# 21 Backup and Restore

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

Backups are exported as encrypted JSON bundles.

```python
db.backup(output_path="backup_2026_03.json", include_audit=True)
```

Restore policy:

```python
db.restore(input_path="backup_2026_03.json", force=False)
```

- `force=False` refuses overwrite of existing tenant data.
- Restoring requires matching token + `org_id` context.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
