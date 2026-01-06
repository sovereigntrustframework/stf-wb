"""Additional iteration tests to cover archive and lookup miss paths."""

from stfwb.core.iteration import Iteration
from stfwb.core.types import IterationState


def test_iteration_archive_and_get_step_miss():
    it = Iteration(project_id="p1")  # pyright: ignore[reportCallIssue]
    assert it.get_step("nope") is None

    it.start()
    assert it.state == IterationState.IN_PROGRESS
    it.freeze()
    assert it.state == IterationState.FROZEN
    it.archive()
    assert it.state == IterationState.ARCHIVED

    d = it.to_dict()
    assert d["kind"] == "iteration"


def test_iteration_from_dict_roundtrip():
    it = Iteration(project_id="p2")  # pyright: ignore[reportCallIssue]
    d = it.to_dict()
    it2 = Iteration.from_dict(d)
    assert it2.project_id == "p2"
    assert it2.state == it.state
