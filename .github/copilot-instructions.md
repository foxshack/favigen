# GitHub Copilot Instructions

## Project Overview

**favigen** is a Python CLI tool (`favigen`) that converts images (JPEG, PNG, WEBP, SVG) into
`.ico` favicons or a full app-icon bundle (`.tar.gz`). SVG inputs are rasterised via
`svglib`/`reportlab` before processing; all other formats are handled by Pillow.

## Tech Stack

- **Python ≥ 3.10**
- **Pillow** — image loading, resizing, and `.ico` generation
- **click** — CLI framework
- **svglib + reportlab** — SVG rasterisation
- **Ruff** — linting and formatting (target: `py310`)
- **pre-commit** — enforces Ruff checks on every commit
- **setuptools + build** — packaging; distributed on PyPI as `favicon-generator`

## Project Structure

```
favicon_generator/
    __init__.py     # package version
    cli.py          # click CLI entry point  →  `favigen` command
    converter.py    # core image processing (rasterise, crop, convert, bundle)
Makefile            # all developer workflows — prefer make commands
pyproject.toml      # project metadata, dependencies, Ruff config
```

## Key Make Commands

| Command | Purpose |
|---|---|
| `make install-dev` | Create venv and install package in editable mode |
| `make pre-commit-all` | Run Ruff lint + format checks across all files |
| `make pre-commit` | Run pre-commit on staged files only |
| `make build` | Build sdist and wheel into `dist/` |
| `make check` | Build then validate distributions with `twine check` |
| `make clean` | Remove venv, `dist/`, `build/`, `__pycache__` |

Always prefer `make` commands over running tools directly (e.g. use `make pre-commit-all`
instead of `ruff check .`).

## Coding Conventions

- **Type annotations**: use `X | Y` union syntax (PEP 604) — no `Union` from `typing`
- **Formatting**: double quotes, 4-space indent, `ruff format` style (Black-compatible)
- **Imports**: isort-ordered; stdlib → third-party → first-party (`favicon_generator`)
- **Docstrings**: Google style with `Args:`, `Returns:`, `Raises:` sections
- **No `from __future__ import annotations`** — the project targets Python 3.10+ natively

## Core Module: `converter.py`

- `rasterize_svg(svg_path, target_size)` — SVG → RGBA PIL Image
- `_load_image(input_path)` — unified loader; dispatches SVG to `rasterize_svg`
- `crop_to_square(image)` — centre-crop to square
- `convert_to_ico(input_path, output_path, crop_square)` — single `.ico` output
- `generate_app_icons_bundle(input_path, output_path, crop_square)` — full `.tar.gz` bundle
  containing `favicon.ico`, PNG icons at standard sizes, `site.webmanifest`, `README.md`

## CLI (`cli.py`)

Entry point: `favigen <INPUT_FILE> [OPTIONS]`

| Flag | Purpose |
|---|---|
| `-o / --output` | Custom output path |
| `-c / --crop` | Centre-crop to square before processing |
| `-a / --app-icons` | Generate full app-icon bundle (`.tar.gz`) instead of `.ico` |

## Adding New Features

1. Image processing logic belongs in `converter.py`.
2. New CLI options are wired up in `cli.py` using `@click.option`.
3. After changes, run `make pre-commit-all` to verify lint/format compliance.
4. Update docstrings and `README.md` if public behaviour changes.
