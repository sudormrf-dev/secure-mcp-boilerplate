# Contributing to secure-mcp-boilerplate

Thank you for your interest in contributing!

## Getting started

1. Fork the repository and clone your fork.
2. Create a virtual environment and install dev dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```
3. Create a feature branch: `git checkout -b feat/your-feature`

## Code style

- All code is formatted and linted with **ruff** (`ruff check src/ tests/`).
- Type annotations are required for all public functions; checked with **mypy**.
- Line length is 120 characters (configured in pyproject.toml).

## Running tests

```bash
pytest tests/ -v
```

All tests must pass before opening a pull request.

## Pull request checklist

- [ ] Tests added/updated for new behaviour
- [ ] `ruff check` passes with no errors
- [ ] `mypy src/ --ignore-missing-imports` passes
- [ ] PR description explains the motivation and approach

## Reporting bugs

Open a GitHub Issue with a minimal reproducible example and the output of
`python --version` and `pip show mcp`.
