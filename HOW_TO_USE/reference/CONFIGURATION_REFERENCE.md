# Configuration Reference

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

| Option | Scope | Default | Description |
|---|---|---|---|
| token | connect() | required | Tenant master secret |
| org_id | connect() | required | Tenant namespace and key context |
| path | connect() | required | Base data location |
| role | connect() | admin | Initial role during first provisioning |
| ip_allowlist | connect()/tokens | ["*"] | Source IP/CIDR enforcement |
| ttl | issue_token | None | Token expiry in seconds |
| single_use | generate_link | True | Link burn-after-read mode |
| lock_timeout | store | 10s | Write lock acquisition timeout |
| shard_size | storage | 10000 | Records per shard |
| cache_ttl | shard cache | 30s | Decrypted shard cache lifetime |

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
