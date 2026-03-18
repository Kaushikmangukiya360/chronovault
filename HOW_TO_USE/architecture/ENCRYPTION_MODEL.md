# Encryption Model

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

chronovault uses authenticated encryption (AES-256-GCM) for every persisted JSON file. Ciphertext is stored as hex in an envelope, and decryption fails if tag validation fails.

## Algorithm Choice

AES-256-GCM was selected because it combines confidentiality and integrity in one primitive. Alternatives like CBC or CTR need separate MAC handling and are easier to misuse.

## Universal Encryption Coverage

| File | Encrypted | Algorithm | Key Source |
|---|---|---|---|
| data_*.json | YES | AES-256-GCM | HKDF(token, org_id, ts) |
| index.json | YES | AES-256-GCM | HKDF(token, org_id, ts) |
| meta.json | YES | AES-256-GCM | HKDF(token, org_id, ts) |
| audit.json | YES | AES-256-GCM | HKDF(token, org_id, ts) |
| tokens.json | YES | AES-256-GCM | HKDF(token, org_id, ts) |
| config.json | YES | AES-256-GCM | HKDF(token, org_id, ts) |
| wal.json | YES | AES-256-GCM | HKDF(token, org_id, ts) |
| fts.json | YES | AES-256-GCM | HKDF(token, org_id, ts) |
| migrations.json | YES | AES-256-GCM | HKDF(token, org_id, ts) |
| keys_meta.json | YES | AES-256-GCM | HKDF(token, org_id, ts) |

## Envelope Format

```json
{
  "v": 1,
  "org_id": "acme-corp",
  "purpose": "data",
  "ts": 1710000000,
  "nonce": "hex-12-bytes",
  "tag": "hex-16-bytes",
  "ct": "hex-ciphertext"
}
```

## Key Lifecycle

1. Derive key from token + org + second.
2. Encrypt or decrypt payload.
3. Return result.
4. Key leaves scope.

> **Security:** The derived key is never stored anywhere. It is created, used, and discarded within a single function call.

## Hash-Based Index and FTS Strategy

Indexes and full-text tokens are keyed by SHA-256 digests rather than plaintext values, then the full index file is encrypted as well.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
