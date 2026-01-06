"""CLI tests for list/show commands with isolated store dirs."""

import re
from pathlib import Path

from click.testing import CliRunner

from stfwb_cli.main import cli


def _extract_id_from_output(text: str) -> str:
    m = re.search(r"id=([0-9a-f\-]{10,})", text)
    assert m, f"Could not find id in output: {text}"
    return m.group(1)


def test_project_list_empty(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["project", "list", "--store-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert f"No projects found in {tmp_path}" in result.output


def test_project_list_and_show(tmp_path: Path) -> None:
    runner = CliRunner()
    # Create a project
    created = runner.invoke(
        cli,
        [
            "project",
            "create",
            "--name",
            "demo",
            "--target-uri",
            "https://example.org/x",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert created.exit_code == 0
    pid = _extract_id_from_output(created.output)

    # List projects
    listed = runner.invoke(cli, ["project", "list", "--store-dir", str(tmp_path)])
    assert listed.exit_code == 0
    assert pid in listed.output
    assert "demo" in listed.output

    # Show project details
    shown = runner.invoke(
        cli,
        [
            "project",
            "show",
            "--id",
            pid,
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert shown.exit_code == 0
    assert f"Project demo (id={pid})" in shown.output
    assert "Target: https://example.org/x" in shown.output


def test_iteration_list_empty(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["iteration", "list", "--store-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert f"No iterations found in {tmp_path}" in result.output


def test_iteration_list_and_show(tmp_path: Path) -> None:
    runner = CliRunner()
    # Create an iteration
    created = runner.invoke(
        cli,
        [
            "iteration",
            "create",
            "--project-id",
            "p1",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert created.exit_code == 0
    mid = re.search(r"Created iteration ([0-9a-f\-]{10,})", created.output)
    assert mid is not None
    iid = mid.group(1)

    # List iterations
    listed = runner.invoke(cli, ["iteration", "list", "--store-dir", str(tmp_path)])
    assert listed.exit_code == 0
    assert iid in listed.output
    assert "p1" in listed.output

    # Show iteration details
    shown = runner.invoke(
        cli,
        [
            "iteration",
            "show",
            "--id",
            iid,
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert shown.exit_code == 0
    assert f"Iteration {iid}" in shown.output
    assert "Project: p1" in shown.output
