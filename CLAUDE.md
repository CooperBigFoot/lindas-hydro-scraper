# Python Package Management with uv

Use uv exclusively for Python package management in this project.

## Package Management Commands

All Python dependencies **must be installed, synchronized, and locked** using uv. Never use pip, pip-tools, poetry, or conda directly for dependency management.

### Core Commands

- **Install dependencies**: `uv add <package>`
- **Remove dependencies**: `uv remove <package>`
- **Sync dependencies**: `uv sync`
- **Install development dependencies**: `uv add --dev <package>`

## Running Python Code

Execute Python code through uv to ensure proper dependency resolution:

- **Run Python scripts**: `uv run <script-name>.py`
- **Run Python tools**: `uv run pytest`, `uv run ruff`, `uv run mypy`
- **Launch Python REPL**: `uv run python`
- **Run with specific Python version**: `uv run --python 3.11 <script.py>`

## Managing Scripts with PEP 723 Inline Metadata

For standalone scripts with embedded dependencies:

- **Run script with inline metadata**: `uv run script.py`
- **Add dependencies to script**: `uv add <package> --script script.py`
- **Remove dependencies from script**: `uv remove <package> --script script.py`

### PEP 723 Script Format

```python
# /// script
# dependencies = [
#     "requests",
#     "pandas>=2.0",
# ]
# ///

import requests
import pandas as pd
```

## Project Structure

- **pyproject.toml**: Project metadata and dependencies
- **uv.lock**: Lockfile (commit to version control)
- **.python-version**: Python version specification (optional)

# Type Checking with ty

Use ty for fast Python type checking in this project.

## Running Type Checks

- **Check entire project**: `uv run ty check`
- **Check specific file**: `uv run ty check src/lindas_hydro_scraper/main.py`
- **Check directory**: `uv run ty check src/`

## Notes

- ty is extremely fast (written in Rust)
- Automatically detects virtual environment
- Run from project root for best results
- If encountering many errors from venv, ensure `.venv` is in `.gitignore`

# Coding Standards

Python coding best practices are defined in `.github/copilot-instructions.md`.
