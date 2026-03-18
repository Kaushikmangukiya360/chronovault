# Contributing

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

## Development Setup

```bash
git clone https://github.com/kaushikmangukiya/chronovault
cd chronovault
python -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"
pip install pytest pytest-cov black ruff mypy
```

## Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=chronovault --cov-report=html
```

## Code Style

```bash
black chronovault/
ruff chronovault/
mypy chronovault/
```

## Pull Request Rules

- All tests must pass.
- New features must include tests.
- Security-related changes should be pre-discussed by email.
- Never store keys or plaintext secrets in repository assets.

## Contact

Built by Kaushik Mangukiya  
kaushikmangukiya360@gmail.com

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
