PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest

.PHONY: venv install test test-q preflight run-example clean

venv:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip

install: venv
	$(PIP) install -e .[dev]

test: install
	$(PYTEST)

test-q: install
	$(PYTEST) -q

preflight: install
	$(VENV)/bin/python -c "import chronovault as cv; print(cv.ChronoVault.preflight_check())"

run-example: install
	$(VENV)/bin/python example.py

clean:
	rm -rf $(VENV) .pytest_cache
