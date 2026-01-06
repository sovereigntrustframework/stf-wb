"""Tests for step runner executing S0→S5 with artifacts and timestamps."""

from datetime import datetime

from stfwb.core.iteration import Iteration
from stfwb.steps.runner import run_next_step, run_steps


def test_run_next_step_sequence() -> None:
    it = Iteration(project_id="p1")  # pyright: ignore[reportCallIssue]
    # No steps yet
    assert len(it.steps) == 0

    # Run all steps sequentially
    ids = []
    for _ in range(6):
        step = run_next_step(it)
        assert step is not None
        ids.append(step.step_id)
        assert step.status == "completed"
        assert step.started_at is not None
        assert step.completed_at is not None
        assert step.result is not None
        assert isinstance(step.started_at, datetime)
    # No more steps
    assert run_next_step(it) is None

    assert ids == ["s0", "s1", "s2", "s3", "s4", "s5"]


def test_run_steps_batch() -> None:
    it = Iteration(project_id="p2")  # pyright: ignore[reportCallIssue]
    out = run_steps(it, 3)
    assert len(out) == 3
    assert [s.step_id for s in out] == ["s0", "s1", "s2"]

    out2 = run_steps(it, 10)  # should stop at s5
    assert len(out2) == 3
    assert [s.step_id for s in out2] == ["s3", "s4", "s5"]
