# Tenant Isolation

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

Tenant boundaries are implemented by directory namespaces and cryptographic derivation context.

```mermaid
graph TD
    A[acme-corp token] --> KA[HKDF acme]
    B[beta-saas token] --> KB[HKDF beta]
    C[gamma-health token] --> KC[HKDF gamma]
    KA --> DA[tenants/acme-corp/*]
    KB --> DB[tenants/beta-saas/*]
    KC --> DC[tenants/gamma-health/*]
```

Cross-tenant decryption fails because `org_id` changes derivation output even with similar token structure.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
