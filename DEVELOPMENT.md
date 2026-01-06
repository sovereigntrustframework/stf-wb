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
