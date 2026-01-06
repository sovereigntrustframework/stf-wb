# GitHub Integration Guide

This guide explains how to publish STF-WB iteration results to GitHub issues.

## Prerequisites

- A GitHub account
- A GitHub repository where you want to publish results
- A GitHub Personal Access Token with `repo` scope

## Creating a GitHub Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "STF-WB Publisher")
4. Select the `repo` scope (full control of private repositories)
5. Click "Generate token"
6. **Save the token securely** - you won't be able to see it again

Token format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## Configuration and Environment Variables

You can provide GitHub credentials via config file or environment variables.

**Config file (`~/.stfwb/stfwb.yaml` or `./stfwb.yaml`):**

```yaml
github_token: ghp_xxx
github_repo: owner/repo
```

**Environment variables:**

```bash
export STFWB_GITHUB_TOKEN=ghp_xxx
export STFWB_GITHUB_REPO=owner/repo
```

**Precedence:** CLI flags > environment variables > config file.

## Publishing an Iteration

### Dry-Run Mode (Recommended First)

Test the publishing process without creating an actual GitHub issue:

```bash
stfwb publish \
  --iteration-id <iteration-id> \
  --repo owner/repo \
  --token ghp_xxx \
  --dry-run
```

Output:
```
[DRY RUN] Would publish iteration <iteration-id> to owner/repo
✓ Successfully published iteration (dry-run)
  Mock issue URL: https://github.com/owner/repo/issues/1
```

### Actual Publishing

Once you've verified the dry-run works:

```bash
stfwb publish \
  --iteration-id <iteration-id> \
  --repo owner/repo \
  --token ghp_xxx
```

Output:
```
✓ Successfully published iteration
  Issue URL: https://github.com/owner/repo/issues/42
```

## Issue Format

The created GitHub issue includes:

### Title
```
Iteration {short-id} - Project {project-id}
```

Example: `Iteration abc12345 - Project xyz-789...`

### Body

The issue body contains:

1. **Iteration Metadata**
   - Full iteration ID
   - Project ID
   - Current state (created, in_progress, frozen, archived)
   - Created timestamp
   - Updated timestamp (if any)

2. **Completed Steps**
   Each completed step is shown with:
   - Step name
   - Status
   - Artifacts (formatted as JSON code blocks)

**Example Issue Body:**

```markdown
## Iteration: abc12345-6789-...

**Project ID:** xyz-789...  
**State:** frozen  
**Created:** 2026-01-06T10:00:00Z  
**Updated:** 2026-01-06T11:30:00Z

## Steps

### Step: S0
**Status:** completed

**Artifacts:**
\`\`\`json
{
  "source_hash": "abc123...",
  "source_uri": "https://github.com/owner/repo",
  "timestamp": "2026-01-06T10:15:00Z"
}
\`\`\`

### Step: S1
**Status:** completed

**Artifacts:**
\`\`\`json
{
  "requirements": [...],
  "metadata": {...}
}
\`\`\`
```

## Error Handling

### Iteration Not Found
```bash
$ stfwb publish --iteration-id invalid-id --repo owner/repo --token ghp_xxx
Error: Iteration 'invalid-id' not found
```

**Fix:** Verify the iteration ID with `stfwb iteration list`

### Invalid Repository Format
```bash
$ stfwb publish --iteration-id abc-123 --repo invalid --token ghp_xxx
# GitHub API will return 404
```

**Fix:** Use format `owner/repo` (e.g., `microsoft/vscode`)

### Authentication Failed
```
✗ Failed to publish iteration
  Error: 401 Unauthorized
```

**Fixes:**
- Verify token is correct and not expired
- Ensure token has `repo` scope
- Check token hasn't been revoked

### Permission Denied
```
✗ Failed to publish iteration
  Error: 403 Forbidden
```

**Fixes:**
- Verify you have write access to the repository
- For organization repos, ensure your token has appropriate organization permissions
- Check repository isn't archived or read-only

### Rate Limiting
```
✗ Failed to publish iteration
  Error: 403 API rate limit exceeded
```

**Fix:** Wait an hour or authenticate with a different token. GitHub allows:
- 60 requests/hour (unauthenticated)
- 5,000 requests/hour (authenticated)

## Best Practices

### 1. Use Dry-Run First

Always test with `--dry-run` before actual publishing:

```bash
# Test first
stfwb publish --iteration-id abc-123 --repo owner/repo --token $TOKEN --dry-run

# If successful, publish for real
stfwb publish --iteration-id abc-123 --repo owner/repo --token $TOKEN
```

### 2. Store Token Securely

**Never commit tokens to version control.** Use environment variables:

```bash
# In ~/.bashrc or ~/.zshrc
export STFWB_GITHUB_TOKEN="ghp_xxx"

# In your scripts
stfwb publish \
  --iteration-id abc-123 \
  --repo owner/repo \
  --token $STFWB_GITHUB_TOKEN
```

Or use a secrets manager (1Password, AWS Secrets Manager, etc.)

### 3. Publish Only Final States

Consider publishing only `frozen` or `archived` iterations:

```bash
# Check state first
STATE=$(stfwb iteration show --id abc-123 --json | jq -r '.state')

if [ "$STATE" = "frozen" ] || [ "$STATE" = "archived" ]; then
  stfwb publish --iteration-id abc-123 --repo owner/repo --token $TOKEN
else
  echo "Iteration not ready for publishing (state: $STATE)"
fi
```

### 4. Automate Publishing

Create a script for batch publishing:

```bash
#!/bin/bash
# publish-frozen.sh - Publish all frozen iterations

REPO="owner/repo"
TOKEN="$STFWB_GITHUB_TOKEN"

stfwb iteration list --json | \
  jq -r '.[] | select(.state == "frozen") | .id' | \
  while read id; do
    echo "Publishing $id..."
    stfwb publish --iteration-id $id --repo $REPO --token $TOKEN
    if [ $? -eq 0 ]; then
      echo "✓ Published $id"
    else
      echo "✗ Failed to publish $id"
    fi
  done
```

### 5. Use Dedicated Repository

Consider creating a dedicated repository for published results:

```bash
# Instead of polluting your main repo
stfwb publish --iteration-id abc-123 --repo owner/stf-wb-results --token $TOKEN
```

Benefits:
- Keeps main repo clean
- Easier to manage/search results
- Can have different access controls

## Integration Examples

### With CI/CD

**GitHub Actions Example:**

```yaml
name: STF-WB Workflow

on:
  push:
    branches: [main]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install STF-WB
        run: pip install -e .
      
      - name: Create Project
        run: |
          PROJECT_ID=$(stfwb project create \
            --name "$GITHUB_REPOSITORY" \
            --target-uri "$GITHUB_SERVER_URL/$GITHUB_REPOSITORY" \
            --json | jq -r '.id')
          echo "PROJECT_ID=$PROJECT_ID" >> $GITHUB_ENV
      
      - name: Create Iteration
        run: |
          ITERATION_ID=$(stfwb iteration create \
            --project-id $PROJECT_ID \
            --json | jq -r '.id')
          echo "ITERATION_ID=$ITERATION_ID" >> $GITHUB_ENV
      
      - name: Run Iteration
        run: stfwb iteration run --iteration-id $ITERATION_ID
      
      - name: Publish Results
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          stfwb publish \
            --iteration-id $ITERATION_ID \
            --repo $GITHUB_REPOSITORY \
            --token $GITHUB_TOKEN
```

### With Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run verification on staged changes
PROJECT_ID="your-project-id"
ITERATION_ID=$(stfwb iteration create --project-id $PROJECT_ID --json | jq -r '.id')

stfwb iteration run --iteration-id $ITERATION_ID

# Check if iteration passed (implementation-specific)
STATE=$(stfwb iteration show --id $ITERATION_ID --json | jq -r '.state')

if [ "$STATE" != "frozen" ]; then
  echo "Verification failed. Commit aborted."
  exit 1
fi

# Optionally publish
stfwb publish \
  --iteration-id $ITERATION_ID \
  --repo owner/repo \
  --token $STFWB_GITHUB_TOKEN \
  --dry-run
```

## Troubleshooting

### Issue Creation Timeout

If GitHub is slow to respond:

```bash
# The default timeout is 30 seconds
# If you see timeout errors, GitHub may be experiencing issues
# Check https://www.githubstatus.com/
```

### Multiple Issues for Same Iteration

The tool doesn't track which iterations have been published. To avoid duplicates:

1. Check issues manually before publishing
2. Use issue labels or project boards to track published iterations
3. Delete the iteration after successful publishing: `stfwb iteration delete --id abc-123 --yes`

### Large Artifacts

GitHub has limits on issue body size:
- Maximum: ~65,536 characters

If artifacts are very large, consider:
1. Summarizing artifacts instead of including full content
2. Uploading artifacts to GitHub Releases or other storage
3. Implementing a custom publisher (see [plugins.md](plugins.md))

## API Reference

See [cli-reference.md](cli-reference.md#publish-command) for complete `publish` command documentation.

## Future Enhancements

Planned features for GitHub integration:

- [ ] Configuration file for storing tokens/repos
- [ ] Environment variable support (`STFWB_GITHUB_TOKEN`, `STFWB_GITHUB_REPO`)
- [ ] Issue labels and milestones
- [ ] Pull request creation instead of issues
- [ ] Comments on existing issues for updated iterations
- [ ] Link iterations to GitHub Projects
- [ ] Artifact upload to GitHub Releases

## See Also

- [CLI Reference](cli-reference.md) - Complete command documentation
- [Plugins Guide](plugins.md) - Custom publishers and step implementations
- [Architecture](architecture.md) - Internal design details
