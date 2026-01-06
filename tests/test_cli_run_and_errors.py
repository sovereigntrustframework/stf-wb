"""Tests for iteration run command with state transitions and persistence."""

from pathlib import Path

from click.testing import CliRunner

from stfwb.core.types import IterationState
from stfwb.utils.storage import load_iteration, save_iteration
from stfwb_cli.main import cli


def test_iteration_run_full_cycle(tmp_path: Path) -> None:
    """Test iteration run through all state transitions."""
    from stfwb.core.iteration import Iteration

    # Create a new iteration in CREATED state
    it = Iteration(project_id="p1")  # pyright: ignore[reportCallIssue]
    save_iteration(it, tmp_path)
    assert it.state == IterationState.CREATED

    runner = CliRunner()

    # First run: CREATED -> IN_PROGRESS
    result = runner.invoke(
        cli,
        ["iteration", "run", "--iteration-id", it.id, "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "Starting iteration..." in result.output
    assert "State: in_progress" in result.output

    # Verify state was persisted
    reloaded = load_iteration(it.id, tmp_path)
    assert reloaded.state == IterationState.IN_PROGRESS

    # Second run: IN_PROGRESS -> FROZEN
    result = runner.invoke(
        cli,
        ["iteration", "run", "--iteration-id", it.id, "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "Freezing iteration..." in result.output
    assert "State: frozen" in result.output

    reloaded = load_iteration(it.id, tmp_path)
    assert reloaded.state == IterationState.FROZEN

    # Third run: FROZEN -> ARCHIVED
    result = runner.invoke(
        cli,
        ["iteration", "run", "--iteration-id", it.id, "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "Archiving iteration..." in result.output
    assert "State: archived" in result.output

    reloaded = load_iteration(it.id, tmp_path)
    assert reloaded.state == IterationState.ARCHIVED


def test_iteration_run_not_found(tmp_path: Path) -> None:
    """Test iteration run with non-existent iteration ID."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["iteration", "run", "--iteration-id", "nonexistent", "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 1
    assert "Error: Iteration nonexistent not found" in result.output


def test_project_show_not_found(tmp_path: Path) -> None:
    """Test project show with non-existent project ID."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["project", "show", "--id", "nonexistent", "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 1
    assert "Error: Project nonexistent not found" in result.output


def test_iteration_show_not_found(tmp_path: Path) -> None:
    """Test iteration show with non-existent iteration ID."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["iteration", "show", "--id", "nonexistent", "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 1
    assert "Error: Iteration nonexistent not found" in result.output


def test_iteration_run_already_archived(tmp_path: Path) -> None:
    """Test iteration run with an already archived iteration."""
    from stfwb.core.iteration import Iteration

    # Create an archived iteration
    it = Iteration(project_id="p1")  # pyright: ignore[reportCallIssue]
    it.start()
    it.freeze()
    it.archive()
    save_iteration(it, tmp_path)
    assert it.state == IterationState.ARCHIVED

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["iteration", "run", "--iteration-id", it.id, "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "already in final state: archived" in result.output
