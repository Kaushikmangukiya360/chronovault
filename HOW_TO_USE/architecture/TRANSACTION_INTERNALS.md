# Transaction Internals

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

Transactions use an encrypted write-ahead log (`wal.json`) with operation snapshots.

```mermaid
sequenceDiagram
    participant App
    participant TX as Transaction Manager
    participant WAL as wal.json
    participant COL as Collections
    App->>TX: begin
    TX->>WAL: append pending tx
    App->>TX: mutate operations
    TX->>WAL: append before/after snapshots
    alt commit
      TX->>COL: apply operations atomically
      TX->>WAL: mark committed
    else rollback
      TX->>COL: restore before snapshots
      TX->>WAL: mark rolled_back
    end
```

Startup recovery checks pending entries and completes rollback/commit based on WAL state policy.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
