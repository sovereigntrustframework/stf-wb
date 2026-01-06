# STF-WB Quickstart Guide

This guide covers installation, basic usage, and common workflows for STF-Workbench v0.2.0 reference implementation.

## Installation

### From Source

```bash
git clone https://github.com/sovereigntrustframework/stf-wb.git
cd stf-wb
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Verify Installation

```bash
stfwb --version
# Output: stfwb, version 0.1.0-beta

stfwb --help
# Shows available commands
```

## Basic Concepts

- **Project**: Represents a verification target (e.g., a GitHub repository or specification document)
- **Iteration**: A workflow run through stages S0→S1→S2→S3→S4→S5
- **Store**: Local directory (`.stfwb/` by default) where projects and iterations are persisted as JSON

## Quick Start: Your First Workflow

### 1. Create a Project

```bash
stfwb project create \
  --name "My First Project" \
  --target-uri "https://github.com/owner/repo"
```

Output:
```
Creating project 'My First Project' targeting https://github.com/owner/repo
Created project 'My First Project' (id=abc-123...) at .stfwb/projects/abc-123....json
```

Save the project ID for later use.

### 2. List Projects

```bash
# Human-readable format
stfwb project list

# JSON format for scripting
stfwb project list --json
```

### 3. View Project Details

```bash
stfwb project show --id <project-id>

# JSON output
stfwb project show --id <project-id> --json
```

### 4. Create an Iteration

```bash
stfwb iteration create --project-id <project-id>
```

Output:
```
Creating iteration for project <project-id>
Created iteration xyz-456... for project <project-id> at .stfwb/iterations/xyz-456....json
```

### 5. Run the Iteration

The iteration progresses through states: `created` → `in_progress` → `frozen` → `archived`

```bash
# First run: created → in_progress
stfwb iteration run --iteration-id <iteration-id>

# Second run: in_progress → frozen
stfwb iteration run --iteration-id <iteration-id>

# Third run: frozen → archived
stfwb iteration run --iteration-id <iteration-id>
```

Each run advances the iteration to the next state and persists changes.

**Advanced Options:**

```bash
# Skip running this iteration (doesn't advance state)
stfwb iteration run --iteration-id <iteration-id> --skip

# Redo work without advancing state (useful for fixing issues)
stfwb iteration run --iteration-id <iteration-id> --redo
```

### 6. Check Iteration Status

```bash
stfwb iteration show --id <iteration-id>

# JSON format
stfwb iteration list --json | jq '.[] | select(.state == "frozen")'
```

## Common Workflows

### Update a Project

```bash
# Update name
stfwb project update --id <project-id> --name "New Name"

# Update target URI
stfwb project update --id <project-id> --target-uri "https://new.example.org"

# Update both
stfwb project update --id <project-id> --name "New Name" --target-uri "https://new.example.org"
```

### Update Iteration State (Advanced)

```bash
# Manually set state (bypasses workflow logic)
stfwb iteration update --id <iteration-id> --state frozen
```

### Delete Resources

```bash
# Delete project (with confirmation)
stfwb project delete --id <project-id>

# Delete without confirmation
stfwb project delete --id <project-id> --yes

# Delete iteration
stfwb iteration delete --id <iteration-id> --yes
```

### Working with Custom Store Directory

By default, all data is saved to `.stfwb/`. You can use a custom directory:

```bash
# Create with custom store
stfwb project create \
  --name "Test" \
  --target-uri "https://example.org" \
  --store-dir ./my-data

# List from custom store
stfwb project list --store-dir ./my-data

# All commands support --store-dir
```

### JSON Output for Scripting

All list/show commands support `--json` for machine-readable output:

```bash
# Get all projects as JSON array
stfwb project list --json

# Get single project details
stfwb project show --id <id> --json

# Pipe to jq for filtering
stfwb iteration list --json | jq '.[] | select(.state == "in_progress")'

# Count archived iterations
stfwb iteration list --json | jq '[.[] | select(.state == "archived")] | length'
```

### Exporting and Importing Resources

Export projects and iterations to JSON files for backup, sharing, or migration:

```bash
# Export a project
stfwb project export --id <project-id> --output project.json

# Export an iteration
stfwb iteration export --id <iteration-id> --output iteration.json

# Import a project
stfwb project import --input project.json

# Import an iteration
stfwb iteration import --input iteration.json
```

### Cleanup and Maintenance

Manage archived iterations and storage:

```bash
# List all archived iterations
stfwb cleanup archived-iterations

# Delete multiple archived iterations
stfwb cleanup bulk-delete-iterations \
  --project-id <project-id> \
  --state archived \
  --yes

# Archive iterations to file and optionally delete them
stfwb cleanup archive-to-file \
  --output backup.json \
  --project-id <project-id> \
  --state frozen \
  --delete-after
```

### Publishing to GitHub

Publish iteration results to GitHub issues:

```bash
# Test publishing without creating an issue (dry-run)
stfwb publish \
  --iteration-id <iteration-id> \
  --repo owner/repo \
  --token ghp_xxx \
  --dry-run

# Actually publish to GitHub
stfwb publish \
  --iteration-id <iteration-id> \
  --repo owner/repo \
  --token ghp_xxx
```

The command creates a GitHub issue with:
- Title: "Iteration {short-id} - Project {project-id}"
- Body: Iteration metadata, state, and all completed steps with artifacts

## File Structure

```
.stfwb/
├── projects/
│   ├── abc-123-uuid.json
│   └── def-456-uuid.json
└── iterations/
    ├── xyz-789-uuid.json
    └── uvw-012-uuid.json
```

Each file contains the full JSON representation of the resource, including:
- Metadata (kind, version, id, timestamps)
- Resource-specific fields (name, target_uri, state, steps, etc.)

## Examples

### Example 1: Create and Run Multiple Iterations

```bash
# Create project
PROJECT_ID=$(stfwb project create \
  --name "Multi-Iteration Test" \
  --target-uri "https://example.org" \
  --json | jq -r '.id')

# Create 3 iterations
for i in {1..3}; do
  stfwb iteration create --project-id $PROJECT_ID
done

# List iterations for this project
stfwb iteration list --json | jq ".[] | select(.project_id == \"$PROJECT_ID\")"
```

### Example 2: Automated Workflow Script

```bash
#!/bin/bash
set -e

# Create project
echo "Creating project..."
PROJECT_JSON=$(stfwb project create \
  --name "Automated Test" \
  --target-uri "https://github.com/owner/repo" \
  --json)
PROJECT_ID=$(echo $PROJECT_JSON | jq -r '.id')
echo "Project ID: $PROJECT_ID"

# Create iteration
echo "Creating iteration..."
ITERATION_JSON=$(stfwb iteration create --project-id $PROJECT_ID --json)
ITERATION_ID=$(echo $ITERATION_JSON | jq -r '.id')
echo "Iteration ID: $ITERATION_ID"

# Run through all states
for state in "created" "in_progress" "frozen"; do
  echo "Running iteration (current state: $state)..."
  stfwb iteration run --iteration-id $ITERATION_ID
done

# Verify final state
FINAL_STATE=$(stfwb iteration show --id $ITERATION_ID --json | jq -r '.state')
echo "Final state: $FINAL_STATE"

if [ "$FINAL_STATE" = "archived" ]; then
  echo "✓ Workflow completed successfully"
else
  echo "✗ Unexpected final state: $FINAL_STATE"
  exit 1
fi
```

### Example 3: Backup and Restore

```bash
# Backup: Copy entire store
cp -r .stfwb .stfwb.backup

# Or export as single JSON file
stfwb project list --json > projects-backup.json
stfwb iteration list --json > iterations-backup.json

# Restore: Copy back
cp -r .stfwb.backup .stfwb
```

## Python API Usage

While the CLI is the primary interface, you can also use the Python API directly:

```python
from pathlib import Path
from stfwb.core.project import Project
from stfwb.core.iteration import Iteration
from stfwb.utils.storage import save_project, save_iteration, load_project

# Create project
project = Project(name="Test", target_uri="https://example.org")
save_project(project, Path(".stfwb"))

# Create iteration
iteration = Iteration(project_id=project.id)
save_iteration(iteration, Path(".stfwb"))

# Load and modify
loaded = load_project(project.id, Path(".stfwb"))
loaded.name = "Updated Name"
save_project(loaded, Path(".stfwb"))
```

## Troubleshooting

### Command not found: stfwb

Ensure the package is installed and virtual environment is activated:

```bash
source .venv/bin/activate
pip install -e .
```

### FileNotFoundError when showing/deleting

The resource ID doesn't exist in the store. List resources to see available IDs:

```bash
stfwb project list
stfwb iteration list
```

### JSON Parsing Errors

Ensure you're using `--json` flag with the command, not trying to parse human-readable output:

```bash
# ✓ Correct
stfwb project list --json | jq '.'

# ✗ Wrong - human-readable output is not valid JSON
stfwb project list | jq '.'
```

## Next Steps

- Read [cli-reference.md](cli-reference.md) for complete command documentation
- See [github-integration.md](github-integration.md) for GitHub publishing guide
- See [plugins.md](plugins.md) for customizing step implementations
- Read [architecture.md](architecture.md) for detailed design information
- Explore the [STF-Workbench v0.2.0 specification](../README.md)
- Run tests: `pytest`
- Check code quality: `ruff check . && pyright`

## Support

For issues, questions, or contributions, visit the GitHub repository:
https://github.com/sovereigntrustframework/stf-wb
