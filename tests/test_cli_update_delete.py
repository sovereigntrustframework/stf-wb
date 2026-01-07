"""Tests for project and iteration update/delete commands."""

from pathlib import Path

from click.testing import CliRunner

from stfwb.core.iteration import Iteration
from stfwb.core.project import Project
from stfwb.core.types import IterationState
from stfwb.utils.storage import (
    load_iteration,
    load_project,
    save_iteration,
    save_project,
)
from stfwb_cli.main import cli


def test_project_update_name(tmp_path: Path) -> None:
    """Test updating project name."""
    proj = Project(
        name="old_name", target_uri="https://example.org"
    )  # pyright: ignore[reportCallIssue]
    save_project(proj, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "project",
            "update",
            "--id",
            proj.id,
            "--name",
            "new_name",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert f"Updated project {proj.id}" in result.output

    reloaded = load_project(proj.id, tmp_path)
    assert reloaded.name == "new_name"
    assert reloaded.target_uri == "https://example.org"


def test_project_update_target_uri(tmp_path: Path) -> None:
    """Test updating project target URI."""
    proj = Project(name="demo", target_uri="https://old.org")  # pyright: ignore[reportCallIssue]
    save_project(proj, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "project",
            "update",
            "--id",
            proj.id,
            "--target-uri",
            "https://new.org",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert f"Updated project {proj.id}" in result.output

    reloaded = load_project(proj.id, tmp_path)
    assert reloaded.name == "demo"
    assert reloaded.target_uri == "https://new.org"


def test_project_update_both(tmp_path: Path) -> None:
    """Test updating both name and target URI."""
    proj = Project(name="old", target_uri="https://old.org")  # pyright: ignore[reportCallIssue]
    save_project(proj, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "project",
            "update",
            "--id",
            proj.id,
            "--name",
            "new",
            "--target-uri",
            "https://new.org",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0

    reloaded = load_project(proj.id, tmp_path)
    assert reloaded.name == "new"
    assert reloaded.target_uri == "https://new.org"


def test_project_update_no_changes(tmp_path: Path) -> None:
    """Test project update with no changes specified."""
    proj = Project(
        name="demo", target_uri="https://example.org"
    )  # pyright: ignore[reportCallIssue]
    save_project(proj, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "project",
            "update",
            "--id",
            proj.id,
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert "No changes specified" in result.output


def test_project_update_not_found(tmp_path: Path) -> None:
    """Test project update with non-existent ID."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "project",
            "update",
            "--id",
            "nonexistent",
            "--name",
            "new",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 1
    assert "Error: Project nonexistent not found" in result.output


def test_project_delete_with_yes(tmp_path: Path) -> None:
    """Test deleting project with --yes flag."""
    proj = Project(
        name="demo", target_uri="https://example.org"
    )  # pyright: ignore[reportCallIssue]
    save_project(proj, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "project",
            "delete",
            "--id",
            proj.id,
            "--yes",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert f"Deleted project {proj.id}" in result.output

    # Verify it's gone
    try:
        load_project(proj.id, tmp_path)
        assert False, "Expected project to be deleted"
    except FileNotFoundError:
        pass


def test_project_delete_with_confirmation(tmp_path: Path) -> None:
    """Test deleting project with confirmation prompt."""
    proj = Project(
        name="demo", target_uri="https://example.org"
    )  # pyright: ignore[reportCallIssue]
    save_project(proj, tmp_path)

    runner = CliRunner()
    # Confirm deletion
    result = runner.invoke(
        cli,
        [
            "project",
            "delete",
            "--id",
            proj.id,
            "--store-dir",
            str(tmp_path),
        ],
        input="y\n",
    )
    assert result.exit_code == 0
    assert f"Deleted project {proj.id}" in result.output


def test_project_delete_abort(tmp_path: Path) -> None:
    """Test aborting project deletion."""
    proj = Project(
        name="demo", target_uri="https://example.org"
    )  # pyright: ignore[reportCallIssue]
    save_project(proj, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "project",
            "delete",
            "--id",
            proj.id,
            "--store-dir",
            str(tmp_path),
        ],
        input="n\n",
    )
    assert result.exit_code == 0
    assert "Aborted" in result.output

    # Verify it still exists
    reloaded = load_project(proj.id, tmp_path)
    assert reloaded.id == proj.id


def test_project_delete_not_found(tmp_path: Path) -> None:
    """Test deleting non-existent project."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "project",
            "delete",
            "--id",
            "nonexistent",
            "--yes",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 1
    assert "Error: Project nonexistent not found" in result.output


def test_iteration_update_state(tmp_path: Path) -> None:
    """Test updating iteration state."""
    it = Iteration(project_id="p1")  # pyright: ignore[reportCallIssue]
    save_iteration(it, tmp_path)
    assert it.state == IterationState.CREATED

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "iteration",
            "update",
            "--id",
            it.id,
            "--state",
            "in_progress",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert f"Updated iteration {it.id} state to in_progress" in result.output

    reloaded = load_iteration(it.id, tmp_path)
    assert reloaded.state == IterationState.IN_PROGRESS


def test_iteration_update_invalid_state(tmp_path: Path) -> None:
    """Test updating iteration with invalid state."""
    it = Iteration(project_id="p1")  # pyright: ignore[reportCallIssue]
    save_iteration(it, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "iteration",
            "update",
            "--id",
            it.id,
            "--state",
            "invalid_state",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 1
    assert "Error: Invalid state 'invalid_state'" in result.output


def test_iteration_update_no_changes(tmp_path: Path) -> None:
    """Test iteration update with no changes specified."""
    it = Iteration(project_id="p1")  # pyright: ignore[reportCallIssue]
    save_iteration(it, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "iteration",
            "update",
            "--id",
            it.id,
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert "No changes specified" in result.output


def test_iteration_update_not_found(tmp_path: Path) -> None:
    """Test iteration update with non-existent ID."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "iteration",
            "update",
            "--id",
            "nonexistent",
            "--state",
            "frozen",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 1
    assert "Error: Iteration nonexistent not found" in result.output


def test_iteration_delete_with_yes(tmp_path: Path) -> None:
    """Test deleting iteration with --yes flag."""
    it = Iteration(project_id="p1")  # pyright: ignore[reportCallIssue]
    save_iteration(it, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "iteration",
            "delete",
            "--id",
            it.id,
            "--yes",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert f"Deleted iteration {it.id}" in result.output

    # Verify it's gone
    try:
        load_iteration(it.id, tmp_path)
        assert False, "Expected iteration to be deleted"
    except FileNotFoundError:
        pass


def test_iteration_delete_with_confirmation(tmp_path: Path) -> None:
    """Test deleting iteration with confirmation prompt."""
    it = Iteration(project_id="p1")  # pyright: ignore[reportCallIssue]
    save_iteration(it, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "iteration",
            "delete",
            "--id",
            it.id,
            "--store-dir",
            str(tmp_path),
        ],
        input="y\n",
    )
    assert result.exit_code == 0
    assert f"Deleted iteration {it.id}" in result.output


def test_iteration_delete_abort(tmp_path: Path) -> None:
    """Test aborting iteration deletion."""
    it = Iteration(project_id="p1")  # pyright: ignore[reportCallIssue]
    save_iteration(it, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "iteration",
            "delete",
            "--id",
            it.id,
            "--store-dir",
            str(tmp_path),
        ],
        input="n\n",
    )
    assert result.exit_code == 0
    assert "Aborted" in result.output

    # Verify it still exists
    reloaded = load_iteration(it.id, tmp_path)
    assert reloaded.id == it.id


def test_iteration_delete_not_found(tmp_path: Path) -> None:
    """Test deleting non-existent iteration."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "iteration",
            "delete",
            "--id",
            "nonexistent",
            "--yes",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 1
    assert "Error: Iteration nonexistent not found" in result.output
