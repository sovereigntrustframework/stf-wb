"""Unit tests for local storage helpers."""

from pathlib import Path

from stfwb.core.iteration import Iteration
from stfwb.core.project import Project
from stfwb.utils.storage import (
    delete_iteration,
    delete_project,
    iteration_path,
    load_iteration,
    load_project,
    project_path,
    save_iteration,
    save_project,
)


def test_save_and_load_project(tmp_path: Path) -> None:
    p = Project(name="p1", target_uri="u1")  # pyright: ignore[reportCallIssue]
    out = save_project(p, tmp_path)
    assert out == project_path(tmp_path, p.id)
    assert out.exists()

    p2 = load_project(p.id, tmp_path)
    assert p2.name == "p1"
    assert p2.target_uri == "u1"
    assert p2.id == p.id


def test_save_and_load_iteration(tmp_path: Path) -> None:
    it = Iteration(project_id="p1")  # pyright: ignore[reportCallIssue]
    out = save_iteration(it, tmp_path)
    assert out == iteration_path(tmp_path, it.id)
    assert out.exists()

    it2 = load_iteration(it.id, tmp_path)
    assert it2.project_id == "p1"
    assert it2.id == it.id


def test_load_project_invalid_json_root_raises(tmp_path: Path) -> None:
    # Write a non-dict JSON root to simulate corruption
    bad_path = project_path(tmp_path, "bad")
    bad_path.parent.mkdir(parents=True, exist_ok=True)
    bad_path.write_text("[]", encoding="utf-8")

    try:
        _ = load_project("bad", tmp_path)
        assert False, "Expected ValueError for non-dict JSON root"
    except ValueError as e:  # pragma: no cover - exception path validated
        assert "Expected JSON object at root" in str(e)


def test_delete_project(tmp_path: Path) -> None:
    p = Project(name="p1", target_uri="u1")  # pyright: ignore[reportCallIssue]
    save_project(p, tmp_path)
    assert project_path(tmp_path, p.id).exists()

    delete_project(p.id, tmp_path)
    assert not project_path(tmp_path, p.id).exists()


def test_delete_project_not_found(tmp_path: Path) -> None:
    try:
        delete_project("nonexistent", tmp_path)
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError as e:
        assert "Project nonexistent not found" in str(e)


def test_delete_iteration(tmp_path: Path) -> None:
    it = Iteration(project_id="p1")  # pyright: ignore[reportCallIssue]
    save_iteration(it, tmp_path)
    assert iteration_path(tmp_path, it.id).exists()

    delete_iteration(it.id, tmp_path)
    assert not iteration_path(tmp_path, it.id).exists()


def test_delete_iteration_not_found(tmp_path: Path) -> None:
    try:
        delete_iteration("nonexistent", tmp_path)
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError as e:
        assert "Iteration nonexistent not found" in str(e)
