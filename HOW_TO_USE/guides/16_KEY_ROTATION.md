# 16 Key Rotation

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

Rotate encrypted payloads to a fresh key epoch.

```python
db.users.rotate_key()
db.rotate_all_keys()
```

Rotation re-encrypts persisted payloads using the current second key derivation context and appends key metadata history.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
