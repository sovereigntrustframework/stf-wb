"""Tests for S0 default implementation (source snapshot)."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from stfwb.core.iteration import Iteration
from stfwb.steps.runner import run_next_step


def test_s0_local_snapshot(tmp_path: Path) -> None:
    """S0 should hash local paths and list files."""
    file_path = tmp_path / "file.txt"
    file_path.write_text("hello")

    it = Iteration(project_id="p1", metadata={"target_uri": str(tmp_path)})
    step = run_next_step(it)

    assert step is not None
    assert step.step_id == "s0"
    assert step.result is not None

    content = step.result["content"]
    assert content["source_uri"] == str(tmp_path)
    assert content["tree_hash"]
    assert "file.txt" in content["files"]
    assert content["snapshot_time"]


def test_s0_git_snapshot(tmp_path: Path) -> None:
    """S0 should call git clone and capture HEAD commit for git targets."""
    it = Iteration(project_id="p1", metadata={"target_uri": "https://example.com/repo.git"})

    clone_result = SimpleNamespace(stdout="", returncode=0)
    head_result = SimpleNamespace(stdout="abc123\n", returncode=0)

    with patch("stfwb.steps.runner.subprocess.run") as mock_run:
        mock_run.side_effect = [clone_result, head_result]
        step = run_next_step(it)

    assert step is not None
    assert step.step_id == "s0"
    assert step.result is not None
    content = step.result["content"]
    assert content["commit"] == "abc123"
    assert content["source_uri"] == "https://example.com/repo.git"

    # Ensure git clone and rev-parse were invoked
    assert mock_run.call_count == 2
    clone_call = mock_run.call_args_list[0]
    head_call = mock_run.call_args_list[1]
    assert "clone" in clone_call.args[0]
    assert "rev-parse" in head_call.args[0]


def test_s0_no_target_defaults() -> None:
    """If no target is provided, S0 returns a minimal artifact."""
    it = Iteration(project_id="p1")
    step = run_next_step(it)

    assert step is not None
    content = step.result["content"]
    assert content["summary"].startswith("source snapshot")
    # No target means no commit or files
    assert content.get("source_uri") is None
    assert content.get("files") is None


def test_s0_missing_local_path_errors() -> None:
    """Missing local path should raise FileNotFoundError."""
    it = Iteration(project_id="p1", metadata={"target_uri": "/nonexistent/path"})
    try:
        run_next_step(it)
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_list_files_limit(tmp_path: Path) -> None:
    """_list_files should short-circuit when limit reached."""
    from stfwb.steps.runner import _list_files

    for i in range(3):
        (tmp_path / f"f{i}.txt").write_text("x")

    files = _list_files(tmp_path, limit=1)
    assert len(files) == 1
