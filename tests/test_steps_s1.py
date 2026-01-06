"""Tests for S1 default implementation (requirements normalization)."""

from pathlib import Path
from stfwb.core.iteration import Iteration
from stfwb.steps.runner import run_steps, run_next_step


def test_s1_local_requirements(tmp_path: Path) -> None:
    """S1 should parse REQ: lines from local markdown files."""
    md = tmp_path / "spec.md"
    md.write_text(
        """
Introduction

REQ: The system shall greet users.
REQ: The system shall log events.
        """.strip()
    )
    # Non-markdown file should be ignored
    (tmp_path / "notes.txt").write_text("REQ: Not parsed from non-md file")

    it = Iteration(project_id="p1", metadata={"target_uri": str(tmp_path)})
    # Run S0 then S1
    run_next_step(it)
    s1 = run_next_step(it)

    assert s1 is not None
    assert s1.step_id == "s1"
    assert s1.result is not None
    content = s1.result["content"]
    assert content["count"] == 2
    assert content["requirements"][0]["text"].startswith("The system shall greet")
    assert content["source"] == str(tmp_path)


def test_s1_remote_is_empty() -> None:
    """Remote URIs yield empty normalized requirements."""
    it = Iteration(project_id="p1", metadata={"target_uri": "https://example.com/repo.git"})
    # Mark S0 achieved to avoid real git operations
    it.add_step("s0")
    s1 = run_next_step(it)

    assert s1 is not None
    content = s1.result["content"]
    assert content["count"] == 0
    assert content["requirements"] == []
    assert content["source"] == "https://example.com/repo.git"


def test_s1_missing_local_path_errors() -> None:
    it = Iteration(project_id="p1", metadata={"target_uri": "/no/such/path"})
    # S0 will error too, but we jump directly to S1 branch via two runs
    try:
        # Run S0 (expected FileNotFoundError)
        run_next_step(it)
        assert False, "Expected S0 FileNotFoundError"
    except FileNotFoundError:
        pass
    # After failure, trying S1 separately should also raise if path missing
    try:
        # Manually invoke S1 by marking s0 achieved then calling next
        it.add_step("s0")
        run_next_step(it)
        assert False, "Expected S1 FileNotFoundError"
    except FileNotFoundError:
        pass


def test_s1_skips_unreadable_file(tmp_path: Path, monkeypatch) -> None:
    """Unreadable markdown files should be skipped without failing the step."""
    good = tmp_path / "good.md"
    bad = tmp_path / "bad.md"
    good.write_text("REQ: A valid requirement.")
    bad.write_text("REQ: This file will appear unreadable.")

    original_read = Path.read_text

    def fake_read(self, *args, **kwargs):  # type: ignore[override]
        if self.name == "bad.md":
            raise IOError("simulated unreadable file")
        return original_read(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fake_read)

    it = Iteration(project_id="p1", metadata={"target_uri": str(tmp_path)})
    # Run S0 then S1
    run_next_step(it)
    s1 = run_next_step(it)

    assert s1 is not None
    content = s1.result["content"]
    assert content["count"] == 1
    assert content["requirements"][0]["text"] == "A valid requirement."
