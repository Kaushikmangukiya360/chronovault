# 18 Server Mode

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

Run chronovault as a daemon for HTTP-accessible operations.

```bash
chronovault serve --org acme --token <token> --host 0.0.0.0 --port 8471
```

Typical endpoint family in server builds:

- `POST /v1/connect`
- `POST /v1/{col}/insert`
- `POST /v1/{col}/find`
- `PUT /v1/{col}/update`
- `DELETE /v1/{col}/delete`
- `GET /v1/audit/tail`

Always pass `Authorization: Bearer <token>` and enforce trusted ingress.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
