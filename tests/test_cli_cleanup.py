"""Tests for cleanup commands."""

import json
from pathlib import Path

from click.testing import CliRunner

from stfwb.core.iteration import Iteration
from stfwb.core.types import IterationState
from stfwb.utils.storage import load_all_iterations, save_iteration
from stfwb_cli.main import cli


def test_cleanup_archived_iterations_list(tmp_path: Path) -> None:
    """Test listing archived iterations."""
    # Create some iterations in different states
    it1 = Iteration(project_id="p1")
    it1.start()
    it1.freeze()
    it1.archive()
    save_iteration(it1, tmp_path)

    it2 = Iteration(project_id="p1")
    save_iteration(it2, tmp_path)

    it3 = Iteration(project_id="p2")
    it3.start()
    it3.freeze()
    it3.archive()
    save_iteration(it3, tmp_path)

    runner = CliRunner()
    result = runner.invoke(cli, ["cleanup", "archived-iterations", "--store-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert it1.id in result.output
    assert it3.id in result.output
    assert it2.id not in result.output


def test_cleanup_archived_iterations_json(tmp_path: Path) -> None:
    """Test listing archived iterations as JSON."""
    it = Iteration(project_id="p1")
    it.start()
    it.freeze()
    it.archive()
    save_iteration(it, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli, ["cleanup", "archived-iterations", "--store-dir", str(tmp_path), "--json"]
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["id"] == it.id


def test_cleanup_archived_iterations_empty(tmp_path: Path) -> None:
    """Test listing archived iterations when none exist."""
    runner = CliRunner()
    result = runner.invoke(cli, ["cleanup", "archived-iterations", "--store-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No archived iterations found" in result.output


def test_cleanup_bulk_delete_iterations_by_state(tmp_path: Path) -> None:
    """Test bulk deleting iterations by state."""
    # Create iterations in different states
    it1 = Iteration(project_id="p1")
    save_iteration(it1, tmp_path)

    it2 = Iteration(project_id="p1")
    it2.start()
    save_iteration(it2, tmp_path)

    it3 = Iteration(project_id="p1")
    it3.start()
    it3.freeze()
    save_iteration(it3, tmp_path)

    runner = CliRunner()
    # Delete all CREATED iterations
    result = runner.invoke(
        cli,
        [
            "cleanup",
            "bulk-delete-iterations",
            "--state",
            "created",
            "--yes",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert "Deleted 1 iteration(s)" in result.output

    # Verify it was deleted
    remaining = load_all_iterations(tmp_path)
    assert len(remaining) == 2
    assert all(it.id != it1.id for it in remaining)


def test_cleanup_bulk_delete_iterations_by_project(tmp_path: Path) -> None:
    """Test bulk deleting iterations by project ID."""
    it1 = Iteration(project_id="p1")
    save_iteration(it1, tmp_path)

    it2 = Iteration(project_id="p1")
    save_iteration(it2, tmp_path)

    it3 = Iteration(project_id="p2")
    save_iteration(it3, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "cleanup",
            "bulk-delete-iterations",
            "--project-id",
            "p1",
            "--yes",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert "Deleted 2 iteration(s)" in result.output

    # Verify only p2 iteration remains
    remaining = load_all_iterations(tmp_path)
    assert len(remaining) == 1
    assert remaining[0].id == it3.id


def test_cleanup_bulk_delete_iterations_confirmation(tmp_path: Path) -> None:
    """Test bulk delete with confirmation prompt."""
    it = Iteration(project_id="p1")
    save_iteration(it, tmp_path)

    runner = CliRunner()
    # Abort the deletion
    result = runner.invoke(
        cli,
        [
            "cleanup",
            "bulk-delete-iterations",
            "--state",
            "created",
            "--store-dir",
            str(tmp_path),
        ],
        input="n\n",
    )
    assert result.exit_code == 0
    assert "Aborted." in result.output

    # Verify iteration still exists
    remaining = load_all_iterations(tmp_path)
    assert len(remaining) == 1


def test_cleanup_bulk_delete_iterations_no_matches(tmp_path: Path) -> None:
    """Test bulk delete with no matching iterations."""
    it = Iteration(project_id="p1")
    save_iteration(it, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "cleanup",
            "bulk-delete-iterations",
            "--state",
            "archived",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert "No iterations match the criteria" in result.output


def test_cleanup_archive_to_file(tmp_path: Path) -> None:
    """Test exporting archived iterations to file."""
    # Create archived iterations
    it1 = Iteration(project_id="p1")
    it1.start()
    it1.freeze()
    it1.archive()
    save_iteration(it1, tmp_path)

    it2 = Iteration(project_id="p2")
    it2.start()
    it2.freeze()
    it2.archive()
    save_iteration(it2, tmp_path)

    # Also create a non-archived one
    it3 = Iteration(project_id="p1")
    save_iteration(it3, tmp_path)

    archive_file = tmp_path / "archived.json"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["cleanup", "archive-to-file", "--output", str(archive_file), "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "Exported 2 archived iteration(s)" in result.output

    # Verify file contains only archived iterations
    assert archive_file.exists()
    data = json.loads(archive_file.read_text())
    assert len(data) == 2
    assert all(it["state"] == "archived" for it in data)


def test_cleanup_archive_to_file_with_delete(tmp_path: Path) -> None:
    """Test exporting and deleting archived iterations."""
    it1 = Iteration(project_id="p1")
    it1.start()
    it1.freeze()
    it1.archive()
    save_iteration(it1, tmp_path)

    it2 = Iteration(project_id="p2")
    it2.start()
    it2.freeze()
    it2.archive()
    save_iteration(it2, tmp_path)

    archive_file = tmp_path / "archived.json"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "cleanup",
            "archive-to-file",
            "--output",
            str(archive_file),
            "--delete-after",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert "Exported 2 archived iteration(s)" in result.output
    assert "Deleted 2 archived iteration(s)" in result.output

    # Verify iterations were deleted
    remaining = load_all_iterations(tmp_path)
    assert len(remaining) == 0


def test_cleanup_archive_to_file_empty(tmp_path: Path) -> None:
    """Test exporting when no archived iterations exist."""
    archive_file = tmp_path / "archived.json"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["cleanup", "archive-to-file", "--output", str(archive_file), "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "No archived iterations to export" in result.output
