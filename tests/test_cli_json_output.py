"""Tests for JSON output in list/show commands."""

import json
from pathlib import Path

from click.testing import CliRunner

from stfwb.core.iteration import Iteration
from stfwb.core.project import Project
from stfwb.utils.storage import save_iteration, save_project
from stfwb_cli.main import cli


def test_project_list_json_empty(tmp_path: Path) -> None:
    """Test project list --json with no projects."""
    runner = CliRunner()
    result = runner.invoke(cli, ["project", "list", "--json", "--store-dir", str(tmp_path)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == []


def test_project_list_json_with_data(tmp_path: Path) -> None:
    """Test project list --json with projects."""
    p1 = Project(name="proj1", target_uri="https://a.com")  # pyright: ignore[reportCallIssue]
    p2 = Project(name="proj2", target_uri="https://b.com")  # pyright: ignore[reportCallIssue]
    save_project(p1, tmp_path)
    save_project(p2, tmp_path)

    runner = CliRunner()
    result = runner.invoke(cli, ["project", "list", "--json", "--store-dir", str(tmp_path)])
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["kind"] == "project"
    assert data[0]["name"] in ["proj1", "proj2"]
    assert "id" in data[0]
    assert "created_at" in data[0]


def test_project_show_json(tmp_path: Path) -> None:
    """Test project show --json."""
    proj = Project(name="demo", target_uri="https://example.org")  # pyright: ignore[reportCallIssue]
    save_project(proj, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["project", "show", "--id", proj.id, "--json", "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert data["id"] == proj.id
    assert data["name"] == "demo"
    assert data["target_uri"] == "https://example.org"
    assert data["kind"] == "project"
    assert "created_at" in data


def test_iteration_list_json_empty(tmp_path: Path) -> None:
    """Test iteration list --json with no iterations."""
    runner = CliRunner()
    result = runner.invoke(cli, ["iteration", "list", "--json", "--store-dir", str(tmp_path)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == []


def test_iteration_list_json_with_data(tmp_path: Path) -> None:
    """Test iteration list --json with iterations."""
    it1 = Iteration(project_id="p1")  # pyright: ignore[reportCallIssue]
    it2 = Iteration(project_id="p2")  # pyright: ignore[reportCallIssue]
    save_iteration(it1, tmp_path)
    save_iteration(it2, tmp_path)

    runner = CliRunner()
    result = runner.invoke(cli, ["iteration", "list", "--json", "--store-dir", str(tmp_path)])
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["kind"] == "iteration"
    assert data[0]["project_id"] in ["p1", "p2"]
    assert "id" in data[0]
    assert "state" in data[0]
    assert "created_at" in data[0]


def test_iteration_show_json(tmp_path: Path) -> None:
    """Test iteration show --json."""
    it = Iteration(project_id="p1")  # pyright: ignore[reportCallIssue]
    save_iteration(it, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["iteration", "show", "--id", it.id, "--json", "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert data["id"] == it.id
    assert data["project_id"] == "p1"
    assert data["state"] == "created"
    assert data["kind"] == "iteration"
    assert "created_at" in data
    assert "steps" in data


def test_project_show_json_not_found(tmp_path: Path) -> None:
    """Test project show --json with non-existent ID still returns error text."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["project", "show", "--id", "nonexistent", "--json", "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 1
    assert "Error: Project nonexistent not found" in result.output
    # Should not be valid JSON on error
    try:
        json.loads(result.output)
        assert False, "Error output should not be JSON"
    except json.JSONDecodeError:
        pass


def test_iteration_show_json_not_found(tmp_path: Path) -> None:
    """Test iteration show --json with non-existent ID still returns error text."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["iteration", "show", "--id", "nonexistent", "--json", "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 1
    assert "Error: Iteration nonexistent not found" in result.output
    # Should not be valid JSON on error
    try:
        json.loads(result.output)
        assert False, "Error output should not be JSON"
    except json.JSONDecodeError:
        pass
