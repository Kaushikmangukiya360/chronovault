# 14 IP Binding

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

Bind tokens to IPs or CIDRs for service-to-service control.

```python
tok = db.issue_token(
    name="report-svc",
    role="viewer",
    collections=["reports"],
    ip_allowlist=["192.168.10.0/24"],
    ttl=3600,
)
```

If the caller IP is outside allowlist, chronovault raises `UnauthorizedIPError`.

Use `ip_allowlist=["*"]` only where network controls are already strict.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
