# 13 Access Control

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

Roles:

- `admin`: full control (tokens, rotation, audit, compliance)
- `editor`: read + write workloads
- `viewer`: read only

```python
svc = db.issue_token(
    name="billing-svc",
    role="viewer",
    collections=["invoices"],
    ip_allowlist=["10.0.0.0/8"],
    ttl=None,
)
```

Every API call validates token, role, IP scope, and collection scope.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
