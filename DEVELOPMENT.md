# Development Guide

## Setup

```bash
git clone https://github.com/sovereigntrustframework/stf-wb.git
cd stf-wb
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
pytest --cov=stfwb --cov=stfwb_cli
```

## Code Style

```bash
black stfwb stfwb_cli tests
ruff check stfwb stfwb_cli tests
mypy stfwb stfwb_cli
```

## Type Checking (Pyright/Pylance)

- Pylance runs in strict mode for this workspace. See `.vscode/settings.json` and `pyrightconfig.json`.
- Treat Pylance errors as build blockers; fix or explicitly type-narrow rather than suppress.
- Preferred patterns:
	- Explicit parameter and return types; avoid implicit `Any`.
	- Use `TypedDict`, `Protocol`, and generics where appropriate.
	- Handle `Optional[T]` with guards; avoid unchecked `None` access.
	- Prefer `datetime.now(datetime.UTC)` over `utcnow()` for timezone-aware values.
	- Use `assert isinstance(...)` or `if` guards for type narrowing.
- Optional CLI (if you want a terminal check):

```bash
npm install --save-dev pyright
npx pyright --level error
```

### Pre-commit hooks

Install and enable hooks so type/style checks run before every commit:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Running CLI

```bash
python -m stfwb_cli.main --help
```

## Key Design Principles

1. **Spec-First** - Models follow v0.2.0 specification exactly
2. **Pydantic Validation** - All models use Pydantic for validation
3. **Type Safety** - Full type hints, check with mypy
4. **Test Coverage** - Aim for >90% coverage
5. **Modular** - Core library separable from UIs
