# File Format Reference

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

## Standard Envelope

```json
{
  "v": 1,
  "org_id": "acme-corp",
  "purpose": "data",
  "ts": 1710000000,
  "nonce": "12-byte nonce hex",
  "tag": "16-byte tag hex",
  "ct": "ciphertext hex"
}
```

## Purpose Values

- `config`
- `tokens`
- `audit`
- `meta`
- `index`
- `data`
- `keys_meta`
- `wal`
- `migrations`
- `fts`

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
