# Key Derivation Flow Diagram

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

```mermaid
flowchart TD
    A[token] --> D[IKM = org_id:token]
    B[org_id] --> D
    C[timestamp] --> E[salt bytes]
    D --> F[HKDF-SHA256]
    E --> F
    G[info = chronovault-v1:org:ts] --> F
    F --> H[32-byte AES key]
    H --> I[encrypt/decrypt]
```

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
