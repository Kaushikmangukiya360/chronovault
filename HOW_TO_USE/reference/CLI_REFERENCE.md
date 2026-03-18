# CLI Reference

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

## Core

```bash
chronovault init --org ORG --token TOKEN --path PATH
chronovault status --org ORG --token TOKEN --path PATH
chronovault serve --org ORG --token TOKEN --host 0.0.0.0 --port 8471
```

## Collections

```bash
chronovault collections list --org ORG --token TOKEN --path PATH
chronovault collections drop --org ORG --token TOKEN --name COL
chronovault collections rename --org ORG --token TOKEN --from A --to B
```

## Audit

```bash
chronovault audit tail --org ORG --token TOKEN --n 50
chronovault audit verify --org ORG --token TOKEN
chronovault audit export --org ORG --token TOKEN --output audit.json
```

## Tokens

```bash
chronovault token issue --org ORG --token TOKEN --name NAME --role viewer
chronovault token revoke --org ORG --token TOKEN --name NAME
chronovault token list --org ORG --token TOKEN
```

## Rotation and Reporting

```bash
chronovault rotate --org ORG --token TOKEN --collection users
chronovault rotate-all --org ORG --token TOKEN
chronovault export-report --org ORG --token TOKEN --output report.json
```

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
