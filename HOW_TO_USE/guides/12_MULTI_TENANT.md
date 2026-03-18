# 12 Multi Tenant

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

Tenant isolation is enforced cryptographically and physically.

- Tenant path: `.../tenants/{org_id}`
- Key context includes `org_id`
- Separate tokens, audit, indexes, and collections per tenant

```python
acme = cv.connect(token="token-a", org_id="acme", path="~/.chronovault")
beta = cv.connect(token="token-b", org_id="beta", path="~/.chronovault")
```

A token from one tenant cannot decrypt files from another tenant.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
