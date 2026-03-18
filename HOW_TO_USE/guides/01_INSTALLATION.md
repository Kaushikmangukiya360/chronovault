# 01 Installation

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

## Table of Contents

- [System Requirements](#system-requirements)
- [Install Commands](#install-commands)
- [Dependency Breakdown](#dependency-breakdown)
- [Virtual Environment](#virtual-environment)
- [Upgrade and Validation](#upgrade-and-validation)

## System Requirements

- Python 3.10+
- Linux, macOS, or Windows
- Local filesystem write permissions
- No network needed for core mode

## Install Commands

```bash
pip install chronovault
```

Optional extras:

```bash
pip install chronovault[server]
pip install chronovault[django]
pip install chronovault[grpc]
pip install chronovault[all]
```

## Dependency Breakdown

- `cryptography>=42.0.0`: AES-256-GCM and HKDF primitives.
- `filelock>=3.13.0`: multi-process write safety.
- `click>=8.1.0`: CLI command surface.
- `rich>=13.0.0`: readable terminal UX.
- `fastapi>=0.110.0` and `uvicorn>=0.29.0`: server mode.
- `python-multipart>=0.0.9`: request parsing support for HTTP endpoints.

## Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install chronovault
```

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install chronovault
```

## Upgrade and Validation

```bash
pip install --upgrade chronovault
python -c "import chronovault; print('chronovault import OK')"
chronovault --help
```

> **Tip:** Use `secrets.token_hex(32)` to generate a cryptographically secure token.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
