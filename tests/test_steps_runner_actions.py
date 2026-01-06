"""Tests for runner actions: skip and redo behaviors."""

from stfwb.core.iteration import Iteration
from stfwb.steps.runner import run_next_step, run_steps


def test_skip_single_step() -> None:
    it = Iteration(project_id="p1")  # pyright: ignore[reportCallIssue]
    s0 = run_next_step(it, action="skip")
    assert s0 is not None
    assert s0.step_id == "s0"
    assert s0.status == "skipped"
    # Next normal run should be s1
    s1 = run_next_step(it)
    assert s1 is not None
    assert s1.step_id == "s1"
    assert s1.status == "completed"


def test_redo_previous_step() -> None:
    it = Iteration(project_id="p2")  # pyright: ignore[reportCallIssue]
    # Run first two normally
    out = run_steps(it, 2)
    assert [s.step_id for s in out] == ["s0", "s1"]
    # Redo last (s1) again
    redo = run_next_step(it, action="redo")
    assert redo is not None
    assert redo.step_id == "s1"
    assert redo.status == "completed"
    # Continue normal should proceed with s2
    s2 = run_next_step(it)
    assert s2 is not None
    assert s2.step_id == "s2"


def test_redo_without_previous_errors() -> None:
    it = Iteration(project_id="p3")  # pyright: ignore[reportCallIssue]
    try:
        run_next_step(it, action="redo")
        assert False, "Expected ValueError when redoing without previous step"
    except ValueError as e:
        assert "Cannot redo" in str(e)


def test_unknown_action_errors() -> None:
    it = Iteration(project_id="p4")  # pyright: ignore[reportCallIssue]
    try:
        run_next_step(it, action="oops")  # type: ignore[arg-type]
        assert False, "Expected ValueError for unknown action"
    except ValueError as e:
        assert "Unknown action" in str(e)
