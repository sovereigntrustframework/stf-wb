"""CLI filter tests for project and iteration list commands."""

import json
import re
from pathlib import Path

from click.testing import CliRunner

from stfwb.core.types import IterationState
from stfwb_cli.main import cli


def _create_project(runner: CliRunner, tmp_path: Path, name: str) -> str:
    res = runner.invoke(
        cli,
        [
            "project",
            "create",
            "--name",
            name,
            "--target-uri",
            "https://example.org/t",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert res.exit_code == 0
    mid = re.search(r"\(id=([0-9a-f\-]{10,})\)", res.output)
    assert mid is not None
    return mid.group(1)


def test_project_list_name_contains_filter(tmp_path: Path) -> None:
    runner = CliRunner()
    _create_project(runner, tmp_path, "alpha")
    _create_project(runner, tmp_path, "beta")

    listed = runner.invoke(
        cli,
        ["project", "list", "--name-contains", "alp", "--store-dir", str(tmp_path)],
    )
    assert listed.exit_code == 0
    # Only alpha should be present
    assert "alpha" in listed.output
    assert "beta" not in listed.output

    # JSON output with same filter
    listed_json = runner.invoke(
        cli,
        ["project", "list", "--json", "--name-contains", "ta", "--store-dir", str(tmp_path)],
    )
    assert listed_json.exit_code == 0
    data = json.loads(listed_json.output)
    assert all(d["name"] == "beta" for d in data)


def test_iteration_list_state_and_project_filters(tmp_path: Path) -> None:
    runner = CliRunner()
    # Create iterations in different states
    res1 = runner.invoke(
        cli,
        ["iteration", "create", "--project-id", "p1", "--store-dir", str(tmp_path)],
    )
    res2 = runner.invoke(
        cli,
        ["iteration", "create", "--project-id", "p2", "--store-dir", str(tmp_path)],
    )
    assert res1.exit_code == 0 and res2.exit_code == 0

    # Extract iteration IDs
    i1 = re.search(r"Created iteration ([0-9a-f\-]{10,})", res1.output).group(1)
    i2 = re.search(r"Created iteration ([0-9a-f\-]{10,})", res2.output).group(1)

    # Run i1 once to move to in_progress and create s0-s2
    run1 = runner.invoke(
        cli,
        ["iteration", "run", "--iteration-id", i1, "--store-dir", str(tmp_path)],
    )
    assert run1.exit_code == 0

    # Filter by state: created should only include i2
    listed_created = runner.invoke(
        cli,
        ["iteration", "list", "--state", "created", "--store-dir", str(tmp_path)],
    )
    assert listed_created.exit_code == 0
    assert i2 in listed_created.output
    assert i1 not in listed_created.output

    # Filter by project id: p1 should include i1
    listed_p1 = runner.invoke(
        cli,
        ["iteration", "list", "--project-id", "p1", "--store-dir", str(tmp_path)],
    )
    assert listed_p1.exit_code == 0
    assert i1 in listed_p1.output
    assert i2 not in listed_p1.output

    # JSON output with combined filters (should match empty or single as appropriate)
    listed_json = runner.invoke(
        cli,
        [
            "iteration",
            "list",
            "--json",
            "--state",
            "in_progress",
            "--project-id",
            "p1",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert listed_json.exit_code == 0
    data = json.loads(listed_json.output)
    assert len(data) == 1
    assert data[0]["project_id"] == "p1"
    assert data[0]["state"] == IterationState.IN_PROGRESS.value

    # Invalid state should error via click.Choice
    bad = runner.invoke(
        cli,
        ["iteration", "list", "--state", "invalid", "--store-dir", str(tmp_path)],
    )
    assert bad.exit_code == 2
    assert "Invalid value for '--state'" in bad.output
