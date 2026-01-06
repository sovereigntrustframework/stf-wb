# Plugin System Guide

STF-WB provides a plugin system for customizing step implementations (S0-S5). This allows you to extend the default behavior without modifying the core codebase.

## Overview

By default, STF-WB uses simple placeholder implementations for steps S0-S5. The plugin system lets you:

- Replace default step implementations with custom logic
- Add tool integrations (TLA+, model checkers, parsers, etc.)
- Implement organization-specific verification workflows
- Create reusable step libraries

## Quick Start

### 1. Create a Plugin

```python
# my_plugin.py
from stfwb.steps.plugin import register_step_implementation

@register_step_implementation("S0")
def custom_s0_implementation(iteration):
    """Custom S0 implementation: Clone repository and compute hash."""
    import subprocess
    import hashlib
    from datetime import datetime, timezone
    
    # Clone the repository
    target_uri = iteration.metadata.get("target_uri", "")
    result = subprocess.run(
        ["git", "clone", "--depth=1", target_uri, "/tmp/repo"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Failed to clone: {result.stderr}")
    
    # Compute hash of cloned content
    result = subprocess.run(
        ["git", "-C", "/tmp/repo", "rev-parse", "HEAD"],
        capture_output=True,
        text=True
    )
    
    source_hash = result.stdout.strip()
    
    # Return artifact
    return {
        "source_hash": source_hash,
        "source_uri": target_uri,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
```

### 2. Register and Use

```python
# main.py
from pathlib import Path
from stfwb.core.iteration import Iteration
from stfwb.steps.runner import run_step
from stfwb.utils.storage import save_iteration

# Import your plugin to register it
import my_plugin

# Create an iteration
iteration = Iteration(
    project_id="abc-123",
    metadata={"target_uri": "https://github.com/owner/repo"}
)

# Run step - uses your plugin implementation
run_step("S0", iteration)

# Save results
save_iteration(iteration, Path(".stfwb"))

print(f"S0 artifact: {iteration.steps[0].artifacts}")
```

### 3. Run from CLI

The plugin system automatically uses registered implementations:

```bash
# Your plugin is imported when the CLI runs
# (Add import in stfwb_cli/main.py or use entry points)
stfwb iteration run --iteration-id <id>
```

## Plugin API

### Registration Decorator

```python
from stfwb.steps.plugin import register_step_implementation

@register_step_implementation(step_name: str)
def implementation_function(iteration: Iteration) -> dict:
    """
    Args:
        step_name: Step identifier ("S0", "S1", "S2", "S3", "S4", "S5")
        iteration: Current iteration object (read/write)
    
    Returns:
        dict: Artifact data to be stored in the step
    
    Raises:
        Any exception will mark the step as failed
    """
    pass
```

### Implementation Requirements

1. **Function signature**: `(iteration: Iteration) -> dict`
2. **Return value**: Dictionary with artifact data
3. **Side effects**: Can modify `iteration.metadata` or other fields
4. **Exceptions**: Any uncaught exception marks step as failed

### Accessing Registry

```python
from stfwb.steps.plugin import get_step_implementation, list_registered_steps

# Get implementation for a step (returns None if not registered)
impl = get_step_implementation("S0")

# List all registered steps
steps = list_registered_steps()
print(f"Registered: {steps}")  # ["S0", "S1", ...]
```

## Example Plugins

### Example 1: S0 - Git Repository Snapshot

```python
from stfwb.steps.plugin import register_step_implementation
import subprocess
from datetime import datetime, timezone

@register_step_implementation("S0")
def git_snapshot(iteration):
    """Clone repo and capture commit hash."""
    target_uri = iteration.metadata.get("target_uri", "")
    
    # Clone repo
    subprocess.run(
        ["git", "clone", "--depth=1", target_uri, "/tmp/stf-repo"],
        check=True,
        capture_output=True
    )
    
    # Get commit hash
    result = subprocess.run(
        ["git", "-C", "/tmp/stf-repo", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True
    )
    
    return {
        "source_hash": result.stdout.strip(),
        "source_uri": target_uri,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
```

### Example 2: S1 - Markdown Requirements Parser

```python
from stfwb.steps.plugin import register_step_implementation
import re

@register_step_implementation("S1")
def parse_markdown_requirements(iteration):
    """Extract requirements from markdown specification."""
    
    # Get S0 artifact (source location)
    s0_artifact = iteration.steps[0].artifacts if iteration.steps else {}
    source_path = s0_artifact.get("source_path", "/tmp/stf-repo/spec.md")
    
    # Read markdown file
    with open(source_path) as f:
        content = f.read()
    
    # Extract requirements (lines starting with "REQ:")
    requirements = []
    for line in content.split("\n"):
        if match := re.match(r"^REQ:\s*(.+)", line):
            requirements.append({
                "id": len(requirements) + 1,
                "text": match.group(1).strip()
            })
    
    return {
        "requirements": requirements,
        "count": len(requirements),
        "source": source_path
    }
```

### Example 3: S2 - TLA+ Specification Generator

```python
from stfwb.steps.plugin import register_step_implementation

@register_step_implementation("S2")
def generate_tla_spec(iteration):
    """Generate TLA+ specification from requirements."""
    
    # Get S1 artifact (requirements)
    s1_artifact = iteration.steps[1].artifacts if len(iteration.steps) > 1 else {}
    requirements = s1_artifact.get("requirements", [])
    
    # Generate TLA+ module
    tla_spec = "---- MODULE Protocol ----\n"
    tla_spec += "EXTENDS Naturals, Sequences\n\n"
    
    for req in requirements:
        tla_spec += f"\\* Requirement {req['id']}: {req['text']}\n"
    
    tla_spec += "\n====\n"
    
    # Write to file
    output_path = "/tmp/Protocol.tla"
    with open(output_path, "w") as f:
        f.write(tla_spec)
    
    return {
        "specification": tla_spec,
        "output_path": output_path,
        "requirement_count": len(requirements)
    }
```

### Example 4: S3 - TLC Model Checker

```python
from stfwb.steps.plugin import register_step_implementation
import subprocess

@register_step_implementation("S3")
def run_tlc_model_checker(iteration):
    """Run TLC model checker on specification."""
    
    # Get S2 artifact (specification path)
    s2_artifact = iteration.steps[2].artifacts if len(iteration.steps) > 2 else {}
    spec_path = s2_artifact.get("output_path", "/tmp/Protocol.tla")
    
    # Run TLC
    result = subprocess.run(
        ["tlc", spec_path, "-deadlock"],
        capture_output=True,
        text=True,
        timeout=300  # 5 minute timeout
    )
    
    is_valid = result.returncode == 0
    
    return {
        "is_valid": is_valid,
        "checker": "TLC",
        "output": result.stdout,
        "errors": result.stderr if not is_valid else None
    }
```

### Example 5: S4 - Coverage Computation

```python
from stfwb.steps.plugin import register_step_implementation

@register_step_implementation("S4")
def compute_coverage(iteration):
    """Compute requirement coverage from verification results."""
    
    # Get requirements (S1) and verification results (S3)
    s1_artifact = iteration.steps[1].artifacts if len(iteration.steps) > 1 else {}
    s3_artifact = iteration.steps[3].artifacts if len(iteration.steps) > 3 else {}
    
    requirements = s1_artifact.get("requirements", [])
    is_valid = s3_artifact.get("is_valid", False)
    
    # Simple coverage: if valid, all requirements covered
    covered = len(requirements) if is_valid else 0
    total = len(requirements)
    
    coverage_pct = (covered / total * 100) if total > 0 else 0
    
    return {
        "unit": "requirements",
        "covered": covered,
        "total": total,
        "percentage": coverage_pct,
        "gaps": [] if is_valid else [r["id"] for r in requirements]
    }
```

### Example 6: S5 - Gate Derivation

```python
from stfwb.steps.plugin import register_step_implementation

@register_step_implementation("S5")
def derive_gate_decision(iteration):
    """Derive approve/reject decision based on coverage."""
    
    # Get coverage artifact (S4)
    s4_artifact = iteration.steps[4].artifacts if len(iteration.steps) > 4 else {}
    
    coverage_pct = s4_artifact.get("percentage", 0)
    threshold = 90.0  # 90% coverage required
    
    decision = "approve" if coverage_pct >= threshold else "reject"
    
    return {
        "decision": decision,
        "coverage": coverage_pct,
        "threshold": threshold,
        "rationale": f"Coverage {coverage_pct:.1f}% {'meets' if decision == 'approve' else 'below'} threshold {threshold}%"
    }
```

## Plugin Packaging

### Create a Distributable Plugin

```
my_stfwb_plugin/
├── setup.py
├── README.md
└── stfwb_plugins/
    ├── __init__.py
    └── git_steps.py
```

**setup.py:**
```python
from setuptools import setup, find_packages

setup(
    name="stfwb-git-plugin",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "stfwb>=0.1.0",
    ],
    entry_points={
        "stfwb.plugins": [
            "git_steps = stfwb_plugins.git_steps",
        ]
    }
)
```

**stfwb_plugins/git_steps.py:**
```python
from stfwb.steps.plugin import register_step_implementation

@register_step_implementation("S0")
def git_snapshot(iteration):
    # Implementation here
    pass
```

**Install and use:**
```bash
pip install stfwb-git-plugin

# Plugin automatically registers when imported
stfwb iteration run --iteration-id <id>
```

## Testing Plugins

```python
# test_my_plugin.py
import pytest
from stfwb.core.iteration import Iteration
from stfwb.steps.plugin import get_step_implementation
import my_plugin

def test_custom_s0():
    """Test custom S0 implementation."""
    
    # Create test iteration
    iteration = Iteration(
        project_id="test-project",
        metadata={"target_uri": "https://github.com/octocat/Hello-World"}
    )
    
    # Get registered implementation
    impl = get_step_implementation("S0")
    assert impl is not None, "S0 implementation not registered"
    
    # Run implementation
    artifact = impl(iteration)
    
    # Verify artifact structure
    assert "source_hash" in artifact
    assert "source_uri" in artifact
    assert "timestamp" in artifact
    assert artifact["source_uri"] == "https://github.com/octocat/Hello-World"
```

Run tests:
```bash
pytest test_my_plugin.py
```

## Plugin Best Practices

### 1. Error Handling

```python
@register_step_implementation("S0")
def safe_implementation(iteration):
    try:
        result = risky_operation()
        return {"success": True, "data": result}
    except Exception as e:
        # Log error for debugging
        import logging
        logging.error(f"S0 failed: {e}")
        
        # Re-raise to mark step as failed
        raise
```

### 2. Logging

```python
from stfwb.utils.logger import get_logger

@register_step_implementation("S1")
def logged_implementation(iteration):
    log = get_logger("my_plugin.S1")
    
    log.info("Starting S1 implementation")
    log.debug(f"Iteration ID: {iteration.id}")
    
    # Do work...
    
    log.info("S1 completed successfully")
    return artifact
```

### 3. Configuration

```python
from stfwb.utils.config import load_config

@register_step_implementation("S2")
def configurable_implementation(iteration):
    config = load_config()
    
    # Get plugin-specific settings
    timeout = config.get("plugins", {}).get("s2_timeout", 300)
    
    # Use configuration
    result = run_with_timeout(timeout)
    return artifact
```

### 4. Idempotency

Ensure steps can be rerun safely:

```python
@register_step_implementation("S0")
def idempotent_implementation(iteration):
    output_dir = f"/tmp/stf-{iteration.id}"
    
    # Clean up previous run
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    # Fresh start
    os.makedirs(output_dir)
    
    # Do work...
    return artifact
```

### 5. Resource Cleanup

```python
@register_step_implementation("S3")
def cleanup_implementation(iteration):
    temp_file = None
    try:
        temp_file = "/tmp/model.tla"
        # Do work with temp file
        return artifact
    finally:
        # Always cleanup
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
```

## Advanced Topics

### Chaining Steps

Access previous step artifacts:

```python
@register_step_implementation("S4")
def chained_implementation(iteration):
    # Get S0-S3 artifacts
    s0 = iteration.steps[0].artifacts if iteration.steps else {}
    s1 = iteration.steps[1].artifacts if len(iteration.steps) > 1 else {}
    # ... use artifacts ...
```

### Conditional Logic

```python
@register_step_implementation("S2")
def conditional_implementation(iteration):
    s1 = iteration.steps[1].artifacts if len(iteration.steps) > 1 else {}
    
    req_count = s1.get("count", 0)
    
    if req_count == 0:
        # No requirements, skip formal spec
        return {"status": "skipped", "reason": "No requirements"}
    
    # Generate spec for requirements
    return generate_spec(s1["requirements"])
```

### External Tool Integration

```python
@register_step_implementation("S3")
def external_tool_integration(iteration):
    import subprocess
    import shutil
    
    # Check if tool is available
    if not shutil.which("tlc"):
        raise RuntimeError("TLC not found in PATH. Install from: https://...")
    
    # Run external tool
    result = subprocess.run(
        ["tlc", "spec.tla"],
        capture_output=True,
        text=True,
        timeout=600
    )
    
    return {
        "tool": "TLC",
        "version": get_tlc_version(),
        "exit_code": result.returncode,
        "output": result.stdout
    }
```

## Troubleshooting

### Plugin Not Registered

**Problem:** Implementation not found when running step.

**Solution:**
1. Ensure plugin file is imported before use
2. Check decorator syntax: `@register_step_implementation("S0")`
3. Verify step name is correct (case-sensitive)

```python
from stfwb.steps.plugin import list_registered_steps
print(list_registered_steps())  # Should include your step
```

### Multiple Registrations

**Problem:** Multiple plugins register same step.

**Behavior:** Last registration wins (overwrites previous).

**Solution:**
- Use unique step names if creating custom steps
- Document plugin conflicts
- Use configuration to choose which plugin to load

### Import Errors

**Problem:** Plugin can't be imported in CLI.

**Solution:**
```python
# In stfwb_cli/main.py, add:
try:
    import my_plugin  # Register plugin implementations
except ImportError:
    pass  # Plugin not installed
```

## See Also

- [CLI Reference](cli-reference.md) - Command documentation
- [Architecture](architecture.md) - Internal design
- [GitHub Integration](github-integration.md) - Publishing results
- [STF-Workbench Spec](https://github.com/sovereigntrustframework/stf-workbench) - Step definitions
