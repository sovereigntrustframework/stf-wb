"""Tests for the step plugin system."""

from stfwb.core.artifact import S0Artifact, S3Artifact
from stfwb.core.artifact_schemas import S0Content, S3Content
from stfwb.core.iteration import Iteration
from stfwb.steps.plugin import (
    clear_plugins,
    get_all_plugins,
    get_plugin,
    has_plugin,
    register_plugin,
    unregister_plugin,
)
from stfwb.steps.runner import run_next_step, run_steps


def test_plugin_registration() -> None:
    """Test registering and unregistering plugins."""
    clear_plugins()

    def custom_s0(step_id: str) -> S0Artifact:
        """Custom S0 plugin."""
        from stfwb.core.artifact import ArtifactMetadata

        meta = ArtifactMetadata(kind="s0.custom", version="0.2.0", id=f"{step_id}-custom")
        content = {"custom": True}
        return S0Artifact(metadata=meta, content=content)

    # Register plugin
    assert not has_plugin("s0")
    register_plugin("s0", custom_s0)
    assert has_plugin("s0")

    # Get plugin
    plugin = get_plugin("s0")
    assert plugin is custom_s0

    # Unregister plugin
    unregister_plugin("s0")
    assert not has_plugin("s0")
    assert get_plugin("s0") is None


def test_plugin_invalid_step_id() -> None:
    """Test that invalid step IDs are rejected."""
    clear_plugins()

    def dummy_plugin(step_id: str) -> S0Artifact:
        from stfwb.core.artifact import S0Artifact, ArtifactMetadata

        meta = ArtifactMetadata(kind="s0.a", version="0.2.0", id="dummy")
        return S0Artifact(metadata=meta, content={})

    try:
        register_plugin("invalid", dummy_plugin)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid step_id" in str(e)


def test_runner_uses_plugin() -> None:
    """Test that the runner uses registered plugins."""
    clear_plugins()

    def custom_s0(step_id: str) -> S0Artifact:
        """Custom S0 plugin."""
        from stfwb.core.artifact import ArtifactMetadata

        meta = ArtifactMetadata(kind="s0.custom", version="0.2.0", id=f"{step_id}-custom")
        content = {"files": "custom", "summary": "custom s0"}
        return S0Artifact(metadata=meta, content=content)

    register_plugin("s0", custom_s0)

    it = Iteration(project_id="p1")
    step = run_next_step(it)
    assert step is not None
    assert step.step_id == "s0"
    assert step.result is not None
    # Check that custom plugin was used
    assert step.result["content"]["files"] == "custom"
    assert step.result["metadata"]["kind"] == "s0.custom"

    clear_plugins()


def test_runner_uses_default_without_plugin() -> None:
    """Test that the runner uses default implementation when no plugin."""
    clear_plugins()

    it = Iteration(project_id="p1")
    step = run_next_step(it)
    assert step is not None
    assert step.step_id == "s0"
    assert step.result is not None
    # Check that default implementation was used
    assert step.result["metadata"]["kind"] == "s0.a"


def test_mixed_plugins_and_defaults() -> None:
    """Test using plugins for some steps and defaults for others."""
    clear_plugins()

    def custom_s3(step_id: str) -> S3Artifact:
        """Custom S3 plugin."""
        from stfwb.core.artifact import ArtifactMetadata

        meta = ArtifactMetadata(kind="s3.custom", version="0.2.0", id=f"{step_id}-custom")
        content = {"checks": [{"name": "custom_check", "passed": True}]}
        return S3Artifact(metadata=meta, content=content)

    register_plugin("s3", custom_s3)

    it = Iteration(project_id="p1")
    # Run through first 3 steps (should use default for s0, s1, s2)
    steps = run_steps(it, 3)
    assert steps[0].result["metadata"]["kind"] == "s0.a"
    assert steps[1].result["metadata"]["kind"] == "s1.a"
    assert steps[2].result["metadata"]["kind"] == "s2.a"

    # Run s3 (should use custom plugin)
    steps = run_steps(it, 1)
    assert steps[0].result["metadata"]["kind"] == "s3.custom"
    assert steps[0].result["content"]["checks"][0]["name"] == "custom_check"

    # Run s4 and s5 (should use defaults)
    steps = run_steps(it, 2)
    assert steps[0].result["metadata"]["kind"] == "s4.a"
    assert steps[1].result["metadata"]["kind"] == "s5.a"

    clear_plugins()


def test_get_all_plugins() -> None:
    """Test getting all registered plugins."""
    clear_plugins()

    def plugin_s0(step_id: str) -> S0Artifact:
        from stfwb.core.artifact import ArtifactMetadata

        meta = ArtifactMetadata(kind="s0.a", version="0.2.0", id="p0")
        return S0Artifact(metadata=meta, content={})

    def plugin_s3(step_id: str) -> S3Artifact:
        from stfwb.core.artifact import ArtifactMetadata

        meta = ArtifactMetadata(kind="s3.a", version="0.2.0", id="p3")
        return S3Artifact(metadata=meta, content={})

    register_plugin("s0", plugin_s0)
    register_plugin("s3", plugin_s3)

    all_plugins = get_all_plugins()
    assert len(all_plugins) == 2
    assert "s0" in all_plugins
    assert "s3" in all_plugins

    clear_plugins()
    assert len(get_all_plugins()) == 0


def test_clear_plugins() -> None:
    """Test clearing all plugins."""
    clear_plugins()

    def dummy_plugin(step_id: str) -> S0Artifact:
        from stfwb.core.artifact import ArtifactMetadata

        meta = ArtifactMetadata(kind="s0.a", version="0.2.0", id="d")
        return S0Artifact(metadata=meta, content={})

    register_plugin("s0", dummy_plugin)
    register_plugin("s1", dummy_plugin)

    assert len(get_all_plugins()) == 2
    clear_plugins()
    assert len(get_all_plugins()) == 0
    assert not has_plugin("s0")
    assert not has_plugin("s1")
