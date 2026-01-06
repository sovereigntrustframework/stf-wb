"""Test console script entry point (stfwb command)."""

import subprocess
from pathlib import Path


def test_console_script_version() -> None:
    """Test that stfwb console script works and returns version."""
    result = subprocess.run(
        [".venv/bin/stfwb", "--version"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    assert result.returncode == 0
    assert "0.1.0-beta" in result.stdout


def test_console_script_help() -> None:
    """Test that stfwb console script shows help."""
    result = subprocess.run(
        [".venv/bin/stfwb", "--help"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    assert result.returncode == 0
    assert "STF-WB" in result.stdout
    assert "project" in result.stdout
    assert "iteration" in result.stdout


def test_console_script_project_list(tmp_path: Path) -> None:
    """Test project list via console script."""
    result = subprocess.run(
        [".venv/bin/stfwb", "project", "list", "--store-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    assert result.returncode == 0
    assert f"No projects found in {tmp_path}" in result.stdout
