# STF-WB: Reference Implementation

Reference implementation of [STF-Workbench v0.2.0](https://github.com/sovereigntrustframework/stf-workbench/tree/main/versions/v0.2.0) specification in Python.

**Status:** Early Alpha (v0.1.0-alpha)

## Overview

STF-WB is the reference implementation of the Sovereign Trust Framework Workbench specification. It demonstrates how to:

- Model projects and iterations as specified in STF-Workbench v0.2.0
- Implement the S0→S5 verification workflow
- Publish evidence artifacts to GitHub
- Compute coverage and derive gate results
- Execute deterministic validation

## Quick Start

```bash
# Install from source
git clone https://github.com/sovereigntrustframework/stf-wb.git
cd stf-wb
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Create a project
stfwb project create --name "hello-world" --target-uri "https://example.org/spec.md"

# Create an iteration
stfwb iteration create --project-id <project-id>

# Run iteration through states (created → in_progress → frozen → archived)
stfwb iteration run --iteration-id <iteration-id>

# List and view resources
stfwb project list
stfwb iteration show --id <iteration-id> --json
```

See [docs/quickstart.md](docs/quickstart.md) for detailed examples and workflows.

## Documentation

- **[Quickstart Guide](docs/quickstart.md)** - Installation, basic usage, and examples
- **[CLI Reference](docs/cli-reference.md)** - Complete command-line documentation
- **[Architecture](docs/architecture.md)** - Design and implementation details

## Architecture

```
stfwb/
├── core/              # Spec implementation (Project, Iteration, Artifact models)
├── steps/             # S0-S5 workflow steps
├── publishers/        # Evidence publishers (GitHub, etc.)
└── utils/             # Validation, coverage, schemas

stfwb_cli/            # Command-line UI
stfwb_web/            # Web UI (future)
```

## Development

### Setup

```bash
git clone https://github.com/sovereigntrustframework/stf-wb.git
cd stf-wb
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
pytest --cov
```

### Run CLI

```bash
python -m stfwb_cli project create --name test
```

## Specification Reference

- **Specification:** [STF-Workbench v0.2.0](https://github.com/sovereigntrustframework/stf-workbench/tree/main/versions/v0.2.0)
- **Methodology:** [STF-M v0.1.3](https://github.com/sovereigntrustframework/stf-methodology)
- **Standards:** [STF-Spec v0.1.3](https://github.com/sovereigntrustframework/stf-spec)

## Key Concepts

### Artifacts (S0-S5)

| Artifact | Purpose |
|----------|---------|
| **S0.A** | Source snapshot (hash, URI, timestamp) |
| **S1.A** | Normalized requirements (structured JSON) |
| **S2.A** | Protocol specification (TLA+ module) |
| **S3.A** | Model checking results (TLC output) |
| **S4.A** | Evidence collection report (coverage) |
| **S5.A** | Gate derivation result (approve/reject) |

### Coverage Computation (Section 6.4.1)

```
coverage = {
  "unit": "fragments",  # or "sections"
  "covered": N,         # verified items
  "total": T,           # total items
  "gaps": [...]         # unverified items
}
```

### Gate Derivation (Section 6.3)

```
decision = all(S3.is_valid) AND coverage >= threshold
```

## Implementation Status

- ✅ Project and Iteration models
- ✅ Artifact schemas (S0.A-S5.A)
- ✅ Core validation framework
- 🟡 S0-S5 step implementations (WIP)
- 🟡 CLI commands (WIP)
- ⏳ GitHub publisher
- ⏳ Web UI

## Hello World Protocol

The [Hello World Protocol](https://github.com/sovereigntrustframework/stf-workbench/blob/main/versions/v0.1.0/stf-workbench-v0.2.0-sip.md#5-hello-world-protocol-example) is the reference scenario demonstrating end-to-end workflow. See [docs/hello_world.md](docs/hello_world.md) for walkthrough.

## Contributing

See [DEVELOPMENT.md](docs/development.md) for contribution guidelines.

## License

MIT License. See [LICENSE](LICENSE) for details.

## See Also

- [Architecture Guide](docs/architecture.md)
- [CLI Reference](docs/cli.md)
- [Artifact Schemas](docs/artifacts.md)
