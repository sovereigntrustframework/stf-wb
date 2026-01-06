# STF-WB CLI Reference

Complete command-line interface reference for STF-Workbench v0.2.0.

## Global Options

```bash
stfwb --version        # Show version
stfwb --help           # Show help message
```

## Project Commands

### project create

Create a new project.

```bash
stfwb project create --name NAME --target-uri URI [--store-dir DIR]
```

**Options:**
- `--name` (required): Project name
- `--target-uri` (required): Target specification URI
- `--store-dir`: Local storage directory (default: `.stfwb`)

**Example:**
```bash
stfwb project create \
  --name "MyProject" \
  --target-uri "https://github.com/owner/repo"
```

### project list

List all projects in the store.

```bash
stfwb project list [--store-dir DIR] [--json]
```

**Options:**
- `--store-dir`: Local storage directory (default: `.stfwb`)
- `--json`: Output as JSON array

**Examples:**
```bash
# Human-readable output
stfwb project list

# JSON output
stfwb project list --json

# Custom store
stfwb project list --store-dir ./my-data
```

### project show

Show details for a specific project.

```bash
stfwb project show --id PROJECT_ID [--store-dir DIR] [--json]
```

**Options:**
- `--id` (required): Project ID
- `--store-dir`: Local storage directory (default: `.stfwb`)
- `--json`: Output as JSON object

**Examples:**
```bash
# Human-readable output
stfwb project show --id abc-123-uuid

# JSON output
stfwb project show --id abc-123-uuid --json
```

**Exit Codes:**
- `0`: Success
- `1`: Project not found

### project update

Update a project's properties.

```bash
stfwb project update --id PROJECT_ID [--name NAME] [--target-uri URI] [--store-dir DIR]
```

**Options:**
- `--id` (required): Project ID
- `--name`: New project name
- `--target-uri`: New target URI
- `--store-dir`: Local storage directory (default: `.stfwb`)

**Examples:**
```bash
# Update name
stfwb project update --id abc-123 --name "New Name"

# Update target URI
stfwb project update --id abc-123 --target-uri "https://new.example.org"

# Update both
stfwb project update --id abc-123 --name "New Name" --target-uri "https://new.example.org"
```

**Exit Codes:**
- `0`: Success
- `1`: Project not found

### project delete

Delete a project.

```bash
stfwb project delete --id PROJECT_ID [--yes] [--store-dir DIR]
```

**Options:**
- `--id` (required): Project ID
- `--yes`, `-y`: Skip confirmation prompt
- `--store-dir`: Local storage directory (default: `.stfwb`)

**Examples:**
```bash
# With confirmation
stfwb project delete --id abc-123

# Skip confirmation
stfwb project delete --id abc-123 --yes
```

**Exit Codes:**
- `0`: Success or aborted
- `1`: Project not found

### project export

Export a project to a JSON file.

```bash
stfwb project export --id PROJECT_ID --output FILE [--store-dir DIR]
```

**Options:**
- `--id` (required): Project ID
- `--output` (required): Output file path
- `--store-dir`: Local storage directory (default: `.stfwb`)

**Example:**
```bash
stfwb project export --id abc-123 --output project-backup.json
```

**Exit Codes:**
- `0`: Success
- `1`: Project not found

### project import

Import a project from a JSON file.

```bash
stfwb project import --input FILE [--store-dir DIR]
```

**Options:**
- `--input` (required): Input file path
- `--store-dir`: Local storage directory (default: `.stfwb`)

**Example:**
```bash
stfwb project import --input project-backup.json
```

**Exit Codes:**
- `0`: Success
- `1`: Invalid JSON or file not found

## Iteration Commands

### iteration create

Create a new iteration for a project.

```bash
stfwb iteration create --project-id PROJECT_ID [--store-dir DIR]
```

**Options:**
- `--project-id` (required): Parent project ID
- `--store-dir`: Local storage directory (default: `.stfwb`)

**Example:**
```bash
stfwb iteration create --project-id abc-123-uuid
```

### iteration list

List all iterations in the store.

```bash
stfwb iteration list [--store-dir DIR] [--json]
```

**Options:**
- `--store-dir`: Local storage directory (default: `.stfwb`)
- `--json`: Output as JSON array

**Examples:**
```bash
# Human-readable output
stfwb iteration list

# JSON output
stfwb iteration list --json

# Filter with jq
stfwb iteration list --json | jq '.[] | select(.state == "in_progress")'
```

### iteration show

Show details for a specific iteration.

```bash
stfwb iteration show --id ITERATION_ID [--store-dir DIR] [--json]
```

**Options:**
- `--id` (required): Iteration ID
- `--store-dir`: Local storage directory (default: `.stfwb`)
- `--json`: Output as JSON object

**Examples:**
```bash
# Human-readable output
stfwb iteration show --id xyz-456-uuid

# JSON output
stfwb iteration show --id xyz-456-uuid --json
```

**Exit Codes:**
- `0`: Success
- `1`: Iteration not found

### iteration run

Execute iteration state transition.

```bash
stfwb iteration run --iteration-id ITERATION_ID [--store-dir DIR] [--skip] [--redo]
```

**Options:**
- `--iteration-id` (required): Iteration ID
- `--store-dir`: Local storage directory (default: `.stfwb`)
- `--skip`: Skip this iteration without advancing state
- `--redo`: Redo work without advancing state

**Behavior:**
Each invocation advances the iteration through one state transition:
1. `created` → `in_progress`
2. `in_progress` → `frozen`
3. `frozen` → `archived`
4. `archived`: No change (already final state)

With `--skip` or `--redo`: State is not advanced. Useful for:
- **--skip**: Temporarily bypass an iteration in a workflow
- **--redo**: Retry work in current state (e.g., after fixing issues)

**Examples:**
```bash
# First run: created → in_progress
stfwb iteration run --iteration-id xyz-456

# Second run: in_progress → frozen
stfwb iteration run --iteration-id xyz-456

# Third run: frozen → archived
stfwb iteration run --iteration-id xyz-456

# Skip without advancing state
stfwb iteration run --iteration-id xyz-456 --skip

# Redo work in current state
stfwb iteration run --iteration-id xyz-456 --redo
```

**Exit Codes:**
- `0`: Success
- `1`: Iteration not found or both --skip and --redo specified

### iteration update

Update iteration properties (advanced).

```bash
stfwb iteration update --id ITERATION_ID --state STATE [--store-dir DIR]
```

**Options:**
- `--id` (required): Iteration ID
- `--state`: New state value (created, in_progress, frozen, archived)
- `--store-dir`: Local storage directory (default: `.stfwb`)

**Example:**
```bash
stfwb iteration update --id xyz-456 --state frozen
```

**Exit Codes:**
- `0`: Success
- `1`: Iteration not found or invalid state

### iteration delete

Delete an iteration.

```bash
stfwb iteration delete --id ITERATION_ID [--yes] [--store-dir DIR]
```

**Options:**
- `--id` (required): Iteration ID
- `--yes`, `-y`: Skip confirmation prompt
- `--store-dir`: Local storage directory (default: `.stfwb`)

**Examples:**
```bash
# With confirmation
stfwb iteration delete --id xyz-456

# Skip confirmation
stfwb iteration delete --id xyz-456 --yes
```

**Exit Codes:**
- `0`: Success or aborted
- `1`: Iteration not found

### iteration export

Export an iteration to a JSON file.

```bash
stfwb iteration export --id ITERATION_ID --output FILE [--store-dir DIR]
```

**Options:**
- `--id` (required): Iteration ID
- `--output` (required): Output file path
- `--store-dir`: Local storage directory (default: `.stfwb`)

**Example:**
```bash
stfwb iteration export --id xyz-456 --output iteration-backup.json
```

**Exit Codes:**
- `0`: Success
- `1`: Iteration not found

### iteration import

Import an iteration from a JSON file.

```bash
stfwb iteration import --input FILE [--store-dir DIR]
```

**Options:**
- `--input` (required): Input file path
- `--store-dir`: Local storage directory (default: `.stfwb`)

**Example:**
```bash
stfwb iteration import --input iteration-backup.json
```

**Exit Codes:**
- `0`: Success
- `1`: Invalid JSON or file not found

## Cleanup Commands

Maintenance commands for managing iterations and storage.

### cleanup archived-iterations

List all archived iterations.

```bash
stfwb cleanup archived-iterations [--store-dir DIR]
```

**Options:**
- `--store-dir`: Local storage directory (default: `.stfwb`)

**Example:**
```bash
stfwb cleanup archived-iterations
```

### cleanup bulk-delete-iterations

Delete multiple iterations matching filter criteria.

```bash
stfwb cleanup bulk-delete-iterations [--project-id ID] [--state STATE] [--yes] [--store-dir DIR]
```

**Options:**
- `--project-id`: Filter by project ID
- `--state`: Filter by state (created, in_progress, frozen, archived)
- `--yes`, `-y`: Skip confirmation prompt
- `--store-dir`: Local storage directory (default: `.stfwb`)

**Examples:**
```bash
# Delete all archived iterations for a project
stfwb cleanup bulk-delete-iterations \
  --project-id abc-123 \
  --state archived \
  --yes

# Delete all frozen iterations (with confirmation)
stfwb cleanup bulk-delete-iterations --state frozen

# Delete all iterations for a project
stfwb cleanup bulk-delete-iterations --project-id abc-123 --yes
```

**Exit Codes:**
- `0`: Success or aborted
- `1`: No iterations matched filter

### cleanup archive-to-file

Export iterations to a file and optionally delete them.

```bash
stfwb cleanup archive-to-file --output FILE [--project-id ID] [--state STATE] [--delete-after] [--store-dir DIR]
```

**Options:**
- `--output` (required): Output file path
- `--project-id`: Filter by project ID
- `--state`: Filter by state (created, in_progress, frozen, archived)
- `--delete-after`: Delete iterations after exporting
- `--store-dir`: Local storage directory (default: `.stfwb`)

**Examples:**
```bash
# Archive frozen iterations to file
stfwb cleanup archive-to-file \
  --output frozen-backup.json \
  --state frozen

# Archive and delete archived iterations
stfwb cleanup archive-to-file \
  --output archived-cleanup.json \
  --state archived \
  --delete-after

# Archive all iterations for a project
stfwb cleanup archive-to-file \
  --output project-abc-archive.json \
  --project-id abc-123
```

**Exit Codes:**
- `0`: Success
- `1`: No iterations matched filter

## Publish Command

Publish iteration results to GitHub as issues.

```bash
stfwb publish --iteration-id ID --repo OWNER/REPO --token TOKEN [--dry-run] [--store-dir DIR]
```

**Options:**
- `--iteration-id` (required): Iteration ID
- `--repo` (required): GitHub repository in format `owner/repo`
- `--token` (required): GitHub personal access token with `repo` scope
- `--dry-run`: Test without creating GitHub issue
- `--store-dir`: Local storage directory (default: `.stfwb`)

**Examples:**
```bash
# Test publishing (dry-run)
stfwb publish \
  --iteration-id xyz-456 \
  --repo owner/repo \
  --token ghp_xxx \
  --dry-run

# Actually publish to GitHub
stfwb publish \
  --iteration-id xyz-456 \
  --repo owner/repo \
  --token ghp_xxx
```

**Created Issue Format:**
- **Title**: `Iteration {short-id} - Project {project-id}`
- **Body**: Markdown with iteration metadata, state, and completed steps with artifacts formatted as JSON code blocks

**Exit Codes:**
- `0`: Success
- `1`: Iteration not found or GitHub API error

See [github-integration.md](github-integration.md) for detailed setup guide.

## Exit Codes

- `0`: Success
- `1`: Error (resource not found, invalid input, etc.)

## JSON Schema

### Project Object

```json
{
  "kind": "project",
  "version": "0.2.0",
  "id": "uuid-string",
  "name": "Project Name",
  "target_uri": "https://example.org",
  "metadata": {},
  "created_at": "2026-01-06T12:00:00Z"
}
```

### Iteration Object

```json
{
  "kind": "iteration",
  "version": "0.2.0",
  "id": "uuid-string",
  "project_id": "project-uuid",
  "state": "created",
  "steps": [],
  "metadata": {},
  "created_at": "2026-01-06T12:00:00Z",
  "updated_at": null
}
```

## Environment Variables

Currently, STF-WB does not use environment variables. All configuration is via command-line options.

## Shell Completion

To enable shell completion (bash/zsh):

```bash
# Generate completion script
_STFWB_COMPLETE=bash_source stfwb > ~/.stfwb-complete.bash

# Add to .bashrc or .zshrc
source ~/.stfwb-complete.bash
```

## Tips and Tricks

### Store Project/Iteration IDs in Variables

```bash
# Store ID when creating
PROJECT_ID=$(stfwb project create --name "Test" --target-uri "https://example.org" --json | jq -r '.id')

# Reuse in commands
stfwb iteration create --project-id $PROJECT_ID
```

### Batch Operations with jq

```bash
# Delete all archived iterations
stfwb iteration list --json | \
  jq -r '.[] | select(.state == "archived") | .id' | \
  while read id; do
    stfwb iteration delete --id $id --yes
  done
```

### Human-Friendly Timestamps

```bash
# Convert ISO timestamps to local time
stfwb project show --id abc-123 --json | \
  jq -r '.created_at' | \
  xargs -I {} date -d {} "+%Y-%m-%d %H:%M:%S %Z"
```

### Check Iteration Progress

```bash
# Count iterations by state
stfwb iteration list --json | jq 'group_by(.state) | map({state: .[0].state, count: length})'
```

## See Also

- [quickstart.md](quickstart.md) - Getting started guide
- [architecture.md](architecture.md) - Design and implementation details
- [README.md](../README.md) - Project overview
