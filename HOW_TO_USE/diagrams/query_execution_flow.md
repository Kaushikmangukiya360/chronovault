# Query Execution Flow Diagram

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

```mermaid
flowchart TD
    A[filter dict] --> B[parse operators]
    B --> C{indexed field?}
    C -->|yes| D[index lookup]
    C -->|no| E[scan shards]
    D --> F[decrypt matched records]
    E --> F
    F --> G[apply filter]
    G --> H[sort]
    H --> I[skip]
    I --> J[limit]
    J --> K[projection]
    K --> L[return]
```

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
