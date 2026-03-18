# Transaction Flow Diagram

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

```mermaid
sequenceDiagram
    participant App
    participant TX
    participant WAL
    participant Store

    App->>TX: begin
    TX->>WAL: write pending entry
    App->>TX: operations
    TX->>WAL: append op snapshots
    alt commit
      TX->>Store: apply all changes
      TX->>WAL: status=committed
    else rollback
      TX->>Store: restore before snapshots
      TX->>WAL: status=rolled_back
    end
```

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
