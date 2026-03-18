# FastAPI Integration

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

```python
from fastapi import FastAPI
from chronovault.integrations.fastapi import CVDepends

app = FastAPI()

@app.get("/users")
async def get_users(db = CVDepends(token="...", org="acme-corp")):
    return db.users.find({}).limit(100).execute()
```

Prefer dependency-based injection so each request has explicit auth context.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
