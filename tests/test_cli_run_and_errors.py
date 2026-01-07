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


def test_iteration_run_skip(tmp_path: Path) -> None:
    """Test iteration run with --skip flag on CREATED iteration."""
    from stfwb.core.iteration import Iteration

    # Create a new iteration (in CREATED state, not started)
    it = Iteration(project_id="p1")  # pyright: ignore[reportCallIssue]
    save_iteration(it, tmp_path)
    assert it.state == IterationState.CREATED

    runner = CliRunner()

    # Run with --skip to skip the next 3 steps (s0, s1, s2)
    result = runner.invoke(
        cli,
        ["iteration", "run", "--iteration-id", it.id, "--store-dir", str(tmp_path), "--skip"],
    )
    assert result.exit_code == 0
    assert "Iteration run complete." in result.output

    # Verify iteration was persisted with 3 skipped steps and transitioned to IN_PROGRESS
    reloaded = load_iteration(it.id, tmp_path)
    assert len(reloaded.steps) == 3
    assert all(s.status == "skipped" for s in reloaded.steps)
    assert [s.step_id for s in reloaded.steps] == ["s0", "s1", "s2"]
    assert reloaded.state == IterationState.IN_PROGRESS


def test_iteration_run_redo(tmp_path: Path) -> None:
    """Test iteration run with --redo flag on FROZEN iteration."""
    from stfwb.core.iteration import Iteration

    # Create iteration, start it, run to IN_PROGRESS, then to FROZEN
    it = Iteration(project_id="p1")  # pyright: ignore[reportCallIssue]
    save_iteration(it, tmp_path)

    runner = CliRunner()

    # First run: CREATED -> IN_PROGRESS (s0, s1, s2)
    result = runner.invoke(
        cli,
        ["iteration", "run", "--iteration-id", it.id, "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "Starting iteration..." in result.output

    reloaded = load_iteration(it.id, tmp_path)
    assert len(reloaded.steps) == 3
    assert [s.step_id for s in reloaded.steps] == ["s0", "s1", "s2"]
    assert reloaded.state == IterationState.IN_PROGRESS

    # Second run: IN_PROGRESS -> FROZEN (s3, s4)
    result = runner.invoke(
        cli,
        ["iteration", "run", "--iteration-id", it.id, "--store-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "Freezing iteration..." in result.output

    reloaded = load_iteration(it.id, tmp_path)
    assert len(reloaded.steps) == 5
    assert [s.step_id for s in reloaded.steps] == ["s0", "s1", "s2", "s3", "s4"]
    assert reloaded.state == IterationState.FROZEN

    # Third run with --redo: FROZEN stays frozen, redo s4 twice
    result = runner.invoke(
        cli,
        ["iteration", "run", "--iteration-id", it.id, "--store-dir", str(tmp_path), "--redo"],
    )
    assert result.exit_code == 0

    # Verify 1 additional s4 entry was added (redo of last achieved step, once)
    reloaded = load_iteration(it.id, tmp_path)
    s4_steps = [s for s in reloaded.steps if s.step_id == "s4"]
    assert len(s4_steps) == 2  # 1 original + 1 redo
    assert all(s.status == "completed" for s in s4_steps)
    # State should still be FROZEN after redo
    assert reloaded.state == IterationState.FROZEN


def test_iteration_run_skip_and_redo_error(tmp_path: Path) -> None:
    """Test iteration run with both --skip and --redo raises error."""
    from stfwb.core.iteration import Iteration

    it = Iteration(project_id="p1")  # pyright: ignore[reportCallIssue]
    it.start()
    save_iteration(it, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "iteration",
            "run",
            "--iteration-id",
            it.id,
            "--store-dir",
            str(tmp_path),
            "--skip",
            "--redo",
        ],
    )
    assert result.exit_code == 1
    assert "Cannot use both --skip and --redo" in result.output
