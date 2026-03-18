# 19 ORM

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

chronovault ORM offers model-based access in environments where explicit dict CRUD is verbose.

```python
from chronovault.orm import Model, StringField, IntField, EmailField

class User(Model):
    __collection__ = "users"
    name = StringField(required=True)
    email = EmailField(required=True, unique=True)
    age = IntField(minimum=0)
```

```python
u = User(name="Alice", email="alice@example.com", age=30)
u.save(db)
```

Use ORM for consistency, but keep raw APIs for performance-sensitive paths.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
