# Encryption Flow Diagram

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

```mermaid
sequenceDiagram
    participant App
    participant Vault
    participant IAM
    participant KDE
    participant Cipher
    participant Store
    participant Disk

    App->>Vault: insert(record)
    Vault->>IAM: validate token/role/ip
    IAM-->>Vault: allowed
    Vault->>KDE: derive_key(token, org_id, ts)
    KDE-->>Cipher: 32-byte key
    Vault->>Cipher: encrypt(payload)
    Cipher-->>Store: envelope(v, org_id, purpose, ts, nonce, tag, ct)
    Store->>Disk: write .tmp + os.replace
    Disk-->>Vault: write complete
    Vault-->>App: record_id
```

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
