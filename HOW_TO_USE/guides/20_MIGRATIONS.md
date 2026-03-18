# 20 Migrations

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

Use versioned migrations for safe schema evolution.

```python
from chronovault.schema.migration import migration

@migration(version=1, description="Add phone field")
def up(collection):
    for rec in collection.find({}).execute():
        if "phone" not in rec:
            collection.update({"_id": rec["_id"]}, {"phone": None})
```

CLI workflow:

```bash
chronovault migrate up --org acme --token <token> --col users
chronovault migrate status --org acme --token <token>
```

Migrations are tracked in encrypted `migrations.json` and are idempotent by version.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
