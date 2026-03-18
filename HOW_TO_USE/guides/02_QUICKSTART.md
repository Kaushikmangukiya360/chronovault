# 02 Quickstart

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

## From Zero to Encrypted Database in 5 Minutes

## Step 1: Install

```bash
pip install chronovault
```

## Step 2: Generate a Token

```python
import secrets

token = secrets.token_hex(32)
print(token)
```

> **Warning:** Losing your token makes data permanently unrecoverable. There is no reset mechanism.

## Step 3: Connect

```python
import chronovault as cv

db = cv.connect(
    token="your-token-here",
    org_id="my-org",
    path="~/.chronovault",
)
```

## Step 4: Insert

```python
user_id = db.users.insert(
    {
        "name": "Alice",
        "email": "alice@example.com",
        "age": 30,
        "role": "admin",
        "country": "India",
    }
)
print(user_id)
```

## Step 5: Verify Encrypted Disk Output

```python
import json
import os

path = os.path.expanduser("~/.chronovault/tenants/my-org/collections/users/data_000.json")
with open(path, "r", encoding="utf-8") as f:
    raw = json.load(f)
print(json.dumps(raw, indent=2))
```

Expected structure:

```json
{
  "v": 1,
  "org_id": "my-org",
  "purpose": "data",
  "ts": 1742290321,
  "nonce": "...",
  "tag": "...",
  "ct": "..."
}
```

## Step 6: Query

```python
print(db.users.find({}).sort("name", 1).limit(10).execute())
print(db.users.find_one({"email": "alice@example.com"}))
```

## Step 7: Update and Delete

```python
db.users.update({"name": "Alice"}, {"age": 31})
db.users.delete({"name": "Alice"})
```

## Step 8: Read Audit

```python
entries = db.audit_log.tail(n=10)
for e in entries:
    print(e["timestamp"], e["event"], e["result"])
```

## What Happens During Insert

1. Token and role validation.
2. IP scope check.
3. Optional schema validation.
4. HKDF key derivation for current second.
5. AES-256-GCM encryption.
6. Atomic write with lock.
7. Index and metadata update.
8. Audit append with chain hash.

> **Security:** The derived key is never stored anywhere. It is created, used, and discarded within a single function call.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
