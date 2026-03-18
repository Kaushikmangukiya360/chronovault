# Architecture Overview Diagram

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

```mermaid
graph TD
    APP[Application] --> API[chronovault API]
    API --> IAM[tenant/iam + tenant/tokens]
    API --> QB[query/builder]
    QB --> QE[query/engine]
    QE --> OP[query/operators]
    API --> AGG[query/aggregator]
    API --> JOIN[query/join]
    API --> COLL[storage/collection]
    COLL --> IDX[storage/index]
    COLL --> SHARD[storage/shard]
    COLL --> STORE[storage/store]
    STORE --> CIPHER[core/cipher]
    CIPHER --> KDE[core/kde]
    API --> AUDIT[audit/logger]
    API --> LINK[access/linker]
    STORE --> DISK[(Encrypted JSON Files)]
```

This diagram shows the module-level path from app calls to encrypted persistence.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
