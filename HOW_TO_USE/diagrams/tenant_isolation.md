# Tenant Isolation Diagram

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

```mermaid
graph LR
    A[acme-corp] --> AP[tenants/acme-corp/*]
    B[beta-saas] --> BP[tenants/beta-saas/*]
    C[gamma-health] --> CP[tenants/gamma-health/*]

    A --> AK[HKDF org=acme]
    B --> BK[HKDF org=beta]
    C --> CK[HKDF org=gamma]

    AK --> AP
    BK --> BP
    CK --> CP
```

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
