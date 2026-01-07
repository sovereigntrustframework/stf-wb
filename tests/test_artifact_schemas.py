"""Tests for artifact content schemas."""

from stfwb.core.artifact_schemas import (
    S0Content,
    S3Check,
    S3Content,
    S4Content,
    S5Content,
)


def test_s0_content_defaults() -> None:
    c = S0Content()
    d = c.model_dump(mode="json")
    assert d["summary"] == "source snapshot"
    assert "files" in d


def test_s3_content_checks() -> None:
    c = S3Content(passed=True, checks=[S3Check(name="invariant1", passed=True)])
    d = c.model_dump(mode="json")
    assert d["passed"] is True
    assert d["checks"][0]["name"] == "invariant1"


def test_s4_content_metrics() -> None:
    c = S4Content(coverage=0.85, metrics={"lines": 0.9, "branches": 0.8})
    d = c.model_dump(mode="json")
    assert d["coverage"] == 0.85
    assert d["metrics"]["lines"] == 0.9


def test_s5_content_decision() -> None:
    c = S5Content(decision="pass", reason="all checks passed")
    d = c.model_dump(mode="json")
    assert d["decision"] == "pass"
    assert d["reason"] == "all checks passed"
