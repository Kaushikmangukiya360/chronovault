# TEMP_INSTALL

This document explains how to install `chronovault` locally from the GitHub repository **without publishing to PyPI** and how to minimize additional package installations.

## 1) Clone the repository (or download as ZIP)

### Option A — Clone via git (recommended)
```bash
git clone https://github.com/kaushikmangukiya360/chronovault.git
cd chronovault/chron/chronovault
```

### Option B — Download ZIP and unpack
1. Visit the repo page: https://github.com/kaushikmangukiya360/chronovault
2. Click **Code → Download ZIP**
3. Unzip, then `cd` into the directory containing `pyproject.toml`.

---

## 2) Create a virtual environment (recommended)

Using venv keeps dependencies isolated and lets you uninstall cleanly.

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 3) Install the package locally (without publishing)

### A) Editable install (recommended for development)
This installs the package in-place so edits are reflected immediately.

```bash
python -m pip install -e .
```

### B) Install directly from GitHub (no local clone required)
This installs from the GitHub repo directly. It still installs dependencies by default.

```bash
python -m pip install git+https://github.com/kaushikmangukiya360/chronovault.git
```

### C) Install without pulling dependencies
If you want to avoid installing third‑party dependencies (e.g., for minimal testing), use `--no-deps`.

```bash
python -m pip install -e . --no-deps
```

> ⚠️ Note: Without dependencies, some features may not work (FastAPI server, etc.).

---

## 4) Run a quick smoke test

```bash
python -c "import chronovault; print(chronovault.__version__)"
```

Or run the included example script:

```bash
python example.py
```

---

## 5) Uninstall (cleanup)

```bash
python -m pip uninstall chronovault
```
