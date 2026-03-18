# 24 Publishing

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

## pyproject.toml Template

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "chronovault"
version = "1.0.0"
description = "Enterprise time-keyed encrypted JSON database"
readme = "README.md"
license = {text = "MIT"}
authors = [
  {name = "Kaushik Mangukiya", email = "kaushikmangukiya360@gmail.com"}
]
keywords = ["database", "encryption", "security", "json", "aes", "enterprise", "saas"]
classifiers = [
  "Development Status :: 5 - Production/Stable",
  "Intended Audience :: Developers",
  "License :: OSI Approved :: MIT License",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Topic :: Database",
  "Topic :: Security :: Cryptography",
]
requires-python = ">=3.10"
dependencies = [
  "cryptography>=42.0.0",
  "filelock>=3.13.0",
  "click>=8.1.0",
  "rich>=13.0.0",
]

[project.optional-dependencies]
server = ["fastapi>=0.110.0", "uvicorn>=0.29.0"]
django = ["django>=4.2"]
grpc = ["grpcio>=1.62.0", "grpcio-tools>=1.62.0"]
all = ["chronovault[server,django,grpc]"]

[project.scripts]
chronovault = "chronovault.cli:main"

[project.urls]
Homepage = "https://github.com/kaushikmangukiya360/chronovault"
Repository = "https://github.com/kaushikmangukiya360/chronovault"
"Bug Tracker" = "https://github.com/kaushikmangukiya360/chronovault/issues"
Documentation = "https://github.com/kaushikmangukiya360/chronovault/HOW_TO_USE"
```

## Release Workflow

```bash
pip install build twine
python -m build
twine check dist/*
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ chronovault
twine upload dist/*
```

## Versioning Strategy

- 1.0.0: Query engine baseline
- 1.1.0: Indexes, joins, aggregation
- 1.2.0: Transactions, FTS, migrations
- 2.0.0: Server mode, ORM, integrations

## Repository Setup

- Name: `chronovault`
- License: MIT
- Topics: python, database, encryption, security, json, aes-256, enterprise, saas

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
