# Changelog

## 0.1.0-beta - 2026-01-06

### Added
- GitHub publisher with CLI `publish` command and `--dry-run` support
- Plugin system for custom S0–S5 step implementations
- Import/export commands for projects and iterations
- Cleanup command group: archived-iterations, bulk-delete-iterations, archive-to-file
- Skip/redo flags for iteration runs
- Configuration system with YAML + env vars for store/log and GitHub defaults
- Comprehensive docs: quickstart, CLI reference, GitHub integration guide, plugin guide
- Test suite expanded to 139 tests with 100% coverage

### Changed
- Version bumped to 0.1.0-beta; status to Beta
- CLI respects config/env defaults for publish (repo/token)
- Updated README and docs to reflect new features

### Notes
- Default store dir remains `.stfwb/`; override via config/env/CLI
- Recommended to run `pytest -q --tb=short` before releases
