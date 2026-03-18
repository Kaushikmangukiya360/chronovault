# Query Pipeline

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

```mermaid
flowchart TD
    A[Filter Dict] --> B[Parse Operators]
    B --> C[Index Check]
    C --> D[Shard Scan or Indexed Fetch]
    D --> E[Decrypt Candidate Records]
    E --> F[Apply Match]
    F --> G[Sort]
    G --> H[Skip]
    H --> I[Limit]
    I --> J[Projection]
    J --> K[Return Results]
```

Execution order is deterministic: filter, sort, skip, limit, project.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
