"""Tests for Artifact models: metadata, to_dict/from_dict roundtrip."""

from datetime import UTC, datetime

from stfwb.core.artifact import ArtifactMetadata, S0Artifact


def test_artifact_roundtrip():
    meta = ArtifactMetadata(
        kind="s0.a",
        version="0.2.0",
        id="a-1",
        created_at=datetime.now(UTC),
    )
    a = S0Artifact(metadata=meta, content={"files": ["a", "b"]})

    d = a.to_dict()
    assert d["metadata"]["kind"] == "s0.a"
    assert d["content"]["files"] == ["a", "b"]

    # from_dict uses pydantic validation and returns the same shape
    b = S0Artifact.from_dict(d)
    assert b.metadata.kind == "s0.a"
    assert b.content == {"files": ["a", "b"]}
