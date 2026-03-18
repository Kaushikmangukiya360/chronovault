# 09 Schema Validation

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

Schema validation runs before encryption on insert and update.

```python
db.users.set_schema({
    "type": "object",
    "required": ["name", "email"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "email": {"type": "string", "format": "email"},
        "age": {"type": "integer", "minimum": 0, "maximum": 150}
    },
    "additionalProperties": False
})
```

```python
db.users.insert({"name": "Alice", "email": "alice@example.com", "age": 30})
```

Violations raise `SchemaValidationError` with field-path detail.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
