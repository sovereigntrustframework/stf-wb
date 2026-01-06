"""Plugin system for custom step implementations.

This module provides a framework for extending the step runner with custom
step implementations. Plugins can generate custom artifacts for any step.
"""

from __future__ import annotations

from typing import Any, Callable, Protocol

from stfwb.core.artifact import S0Artifact, S1Artifact, S2Artifact, S3Artifact, S4Artifact, S5Artifact


class StepPlugin(Protocol):
    """Protocol for step plugins.
    
    A plugin is a callable that takes a step ID and returns an artifact.
    """

    def __call__(self, step_id: str) -> S0Artifact | S1Artifact | S2Artifact | S3Artifact | S4Artifact | S5Artifact:
        """Generate an artifact for the given step."""
        ...


_plugins: dict[str, StepPlugin] = {}


def register_plugin(step_id: str, plugin: StepPlugin) -> None:
    """Register a custom step plugin.
    
    Args:
        step_id: Step identifier (s0-s5)
        plugin: Callable that generates an artifact for the step
    """
    if step_id not in ("s0", "s1", "s2", "s3", "s4", "s5"):
        raise ValueError(f"Invalid step_id: {step_id}")
    _plugins[step_id] = plugin


def unregister_plugin(step_id: str) -> None:
    """Unregister a custom step plugin.
    
    Args:
        step_id: Step identifier (s0-s5)
    """
    _plugins.pop(step_id, None)


def get_plugin(step_id: str) -> StepPlugin | None:
    """Get a registered plugin for a step.
    
    Args:
        step_id: Step identifier (s0-s5)
        
    Returns:
        The plugin if registered, None otherwise
    """
    return _plugins.get(step_id)


def has_plugin(step_id: str) -> bool:
    """Check if a plugin is registered for a step.
    
    Args:
        step_id: Step identifier (s0-s5)
        
    Returns:
        True if a plugin is registered, False otherwise
    """
    return step_id in _plugins


def clear_plugins() -> None:
    """Clear all registered plugins."""
    _plugins.clear()


def get_all_plugins() -> dict[str, StepPlugin]:
    """Get all registered plugins."""
    return dict(_plugins)
