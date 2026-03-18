# 03 Configuration

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

## connect() Options

```python
import chronovault as cv

db = cv.connect(
    token="secure-token",
    org_id="acme-corp",
    path="~/.chronovault",
    role="admin",
    ip_allowlist=["*"],
)
```

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| token | str | Yes | - | Master tenant secret used for key derivation and auth |
| org_id | str | Yes | - | Tenant namespace and cryptographic context |
| path | str | Yes | - | Base data directory |
| role | str | No | admin | Bootstrap role for first tenant init |
| ip_allowlist | list[str] | No | ["*"] | Allowed source IPs/CIDRs |
| tls | bool | No | False | Metadata flag for gateway-managed TLS deployments |

Environment-driven pattern:

```python
import os
import chronovault as cv

db = cv.connect(
    token=os.environ["CV_TOKEN"],
    org_id=os.environ.get("CV_ORG", "acme"),
    path=os.environ.get("CV_PATH", "~/.chronovault"),
)
```

> **Note:** `org_id` is baked into the encryption key. Never change it after first use.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
