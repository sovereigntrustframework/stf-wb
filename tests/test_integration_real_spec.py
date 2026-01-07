"""Integration test using the real STF-Workbench specification."""

from pathlib import Path

from stfwb.core.iteration import Iteration
from stfwb.steps.runner import run_next_step


def test_s1_extracts_rfc2119_requirements_from_real_spec() -> None:
    """Verify S1 can parse RFC 2119 requirements from the actual workbench spec."""
    spec_dir = Path(__file__).parent.parent / "docs" / "specs"

    if not spec_dir.exists():
        # Skip if spec directory not present in test environment
        return

    it = Iteration(project_id="stf-wb-self-verification", metadata={"target_uri": str(spec_dir)})

    # Run S0 to snapshot the spec
    s0 = run_next_step(it)
    assert s0 is not None
    assert s0.step_id == "s0"
    assert s0.result is not None
    s0_content = s0.result["content"]
    assert "stf-workbench-v0.2.0.md" in str(s0_content.get("files", []))

    # Run S1 to extract requirements
    s1 = run_next_step(it)
    assert s1 is not None
    assert s1.step_id == "s1"
    assert s1.result is not None

    s1_content = s1.result["content"]
    assert s1_content["count"] > 0, "Should extract RFC 2119 requirements from spec"
    assert s1_content["source"] == str(spec_dir)

    # Verify some expected requirement patterns
    reqs = s1_content["requirements"]
    assert any("MUST" in req["text"] for req in reqs), "Should find MUST requirements"

    # Check for known requirements from the spec
    req_texts = [req["text"] for req in reqs]
    assert any(
        "profile:core" in text and "MUST" in text for text in req_texts
    ), "Should extract core profile requirement"


def test_s0_s1_workflow_with_real_spec() -> None:
    """End-to-end test: S0 snapshot + S1 normalization on real spec."""
    spec_dir = Path(__file__).parent.parent / "docs" / "specs"

    if not spec_dir.exists():
        return

    it = Iteration(project_id="stf-wb-verification", metadata={"target_uri": str(spec_dir)})

    # S0: Source snapshot
    s0 = run_next_step(it)
    assert s0 is not None
    assert s0.result["content"]["source_uri"] == str(spec_dir)

    # S1: Requirements normalization
    s1 = run_next_step(it)
    assert s1 is not None
    reqs = s1.result["content"]["requirements"]

    # Verify RFC 2119 keywords are captured
    keywords_found = set()
    for req in reqs:
        text = req["text"]
        if " MUST " in text:
            keywords_found.add("MUST")
        if " SHALL " in text:
            keywords_found.add("SHALL")
        if " SHOULD " in text:
            keywords_found.add("SHOULD")
        if " MAY " in text:
            keywords_found.add("MAY")

    assert len(keywords_found) > 0, "Should find at least one RFC 2119 keyword"
    assert "MUST" in keywords_found, "Spec contains many MUST requirements"
