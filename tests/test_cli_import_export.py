"""Tests for project and iteration import/export commands."""

import json
from pathlib import Path

from click.testing import CliRunner

from stfwb.core.iteration import Iteration
from stfwb.core.project import Project
from stfwb.utils.storage import load_iteration, load_project
from stfwb_cli.main import cli


def test_project_export(tmp_path: Path) -> None:
    """Test exporting a project to JSON."""
    from stfwb.utils.storage import save_project

    # Create and save a project
    proj = Project(name="Test Project", target_uri="http://example.com/spec")
    save_project(proj, tmp_path)

    # Export to file
    export_file = tmp_path / "project_export.json"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["project", "export", "--id", proj.id, "--output", str(export_file), "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert f"Exported project {proj.id}" in result.output

    # Verify file contents
    assert export_file.exists()
    data = json.loads(export_file.read_text())
    assert data["id"] == proj.id
    assert data["name"] == "Test Project"
    assert data["target_uri"] == "http://example.com/spec"


def test_project_import(tmp_path: Path) -> None:
    """Test importing a project from JSON."""
    # Create a project JSON file
    proj_data = {
        "kind": "project",
        "version": "0.2.0",
        "id": "imported-project-123",
        "name": "Imported Project",
        "target_uri": "http://example.com/imported",
        "metadata": {},
        "created_at": "2026-01-06T00:00:00Z",
    }
    import_file = tmp_path / "project_import.json"
    import_file.write_text(json.dumps(proj_data))

    # Import the project
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["project", "import", "--file", str(import_file), "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "Imported project imported-project-123" in result.output

    # Verify it was saved to storage
    loaded = load_project("imported-project-123", tmp_path)
    assert loaded.name == "Imported Project"
    assert loaded.target_uri == "http://example.com/imported"


def test_iteration_export(tmp_path: Path) -> None:
    """Test exporting an iteration to JSON."""
    from stfwb.utils.storage import save_iteration

    # Create and save an iteration
    it = Iteration(project_id="p1")
    save_iteration(it, tmp_path)

    # Export to file
    export_file = tmp_path / "iteration_export.json"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["iteration", "export", "--id", it.id, "--output", str(export_file), "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert f"Exported iteration {it.id}" in result.output

    # Verify file contents
    assert export_file.exists()
    data = json.loads(export_file.read_text())
    assert data["id"] == it.id
    assert data["project_id"] == "p1"
    assert data["state"] == "created"


def test_iteration_import(tmp_path: Path) -> None:
    """Test importing an iteration from JSON."""
    # Create an iteration JSON file
    it_data = {
        "kind": "iteration",
        "version": "0.2.0",
        "id": "imported-iteration-456",
        "project_id": "p1",
        "state": "in_progress",
        "steps": [],
        "metadata": {},
        "created_at": "2026-01-06T00:00:00Z",
        "updated_at": None,
    }
    import_file = tmp_path / "iteration_import.json"
    import_file.write_text(json.dumps(it_data))

    # Import the iteration
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["iteration", "import", "--file", str(import_file), "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "Imported iteration imported-iteration-456" in result.output

    # Verify it was saved to storage
    loaded = load_iteration("imported-iteration-456", tmp_path)
    assert loaded.project_id == "p1"
    assert loaded.state.value == "in_progress"


def test_project_export_not_found(tmp_path: Path) -> None:
    """Test exporting a non-existent project."""
    export_file = tmp_path / "export.json"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["project", "export", "--id", "nonexistent", "--output", str(export_file), "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 1
    assert "not found" in result.output


def test_iteration_export_not_found(tmp_path: Path) -> None:
    """Test exporting a non-existent iteration."""
    export_file = tmp_path / "export.json"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["iteration", "export", "--id", "nonexistent", "--output", str(export_file), "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 1
    assert "not found" in result.output


def test_project_import_nonexistent_file(tmp_path: Path) -> None:
    """Test importing from a non-existent file."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["project", "import", "--file", str(tmp_path / "nonexistent.json"), "--store-dir", str(tmp_path)],
    )
    assert result.exit_code != 0


def test_iteration_import_nonexistent_file(tmp_path: Path) -> None:
    """Test importing from a non-existent file."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["iteration", "import", "--file", str(tmp_path / "nonexistent.json"), "--store-dir", str(tmp_path)],
    )
    assert result.exit_code != 0
