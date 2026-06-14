# Variables
VENV_NAME ?= venv
PYTHON_ENV_PATH := $(or $(VIRTUAL_ENV), $(VENV_NAME))
PIP = $(PYTHON_ENV_PATH)/bin/pip
RUFF = $(PYTHON_ENV_PATH)/bin/ruff
PRECOMMIT = $(PYTHON_ENV_PATH)/bin/pre-commit
PYTEST = $(PYTHON_ENV_PATH)/bin/pytest

.PHONY: all build sdist wheel install install-dev check clean deps test

venv:
	@python3 -m venv $(VENV_NAME) && $(VENV_NAME)/bin/pip install --upgrade pip;
	@echo "Virtual environment created.";

all: build

# Install build and check dependencies
deps: venv
	$(PIP) install --upgrade build twine

# Build both sdist and wheel
build: deps
	python -m build

# Build source distribution only
sdist: deps
	python -m build --sdist

# Build wheel only
wheel: deps
	python -m build --wheel

# Check the built distributions for common packaging issues
check: build
	twine check dist/*

# Install the package in editable/development mode
install-dev: venv
	$(PIP) install -e .

# Install the built wheel
install: wheel
	$(PIP) install dist/*.whl

# Perform code quality checks using ruff and pre-commit
pre-commit: pre-commit-install
	$(PRECOMMIT) run

# Run test suite
test: install-dev
	$(PIP) install -e .[dev]
	$(PYTEST)

# Pre-commit targets
pre-commit-all: pre-commit-install
	$(PRECOMMIT) run --all-files

pre-commit-install:
	$(PIP) install pre-commit
	$(PRECOMMIT) install

pre-commit-update:
	$(PRECOMMIT) autoupdate

# Remove build artifacts
clean:
	rm -rf $(VENV_NAME) dist/ build/ *.egg-info/ favicon_generator/*.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
