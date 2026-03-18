# Django Integration

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

Configure backend entry in Django settings:

```python
DATABASES = {
    "default": {
        "ENGINE": "chronovault.integrations.django",
        "TOKEN": "your-token",
        "ORG_ID": "acme-corp",
        "BASE_PATH": "/var/lib/chronovault",
    }
}
```

Use only trusted process environments for token injection.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
