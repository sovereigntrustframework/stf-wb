"""Unit tests for core models."""

import pytest
from stfwb.core.project import Project
from stfwb.core.iteration import Iteration
from stfwb.core.types import IterationState

class TestProject:
    """Tests for Project model."""

    def test_create_project(self):
        """Test creating a project."""
        project = Project(
            name="hello-world",
            target_uri="https://example.org/hello-world-v1.0.md"
        )
        assert project.name == "hello-world"
        assert project.target_uri == "https://example.org/hello-world-v1.0.md"
        assert project.id is not None
        assert project.validate()

    def test_project_serialization(self):
        """Test serializing project to dict."""
        project = Project(
            name="test",
            target_uri="https://example.org/test.md"
        )
        data = project.to_dict()
        assert data["name"] == "test"
        assert data["kind"] == "project"

class TestIteration:
    """Tests for Iteration model."""

    def test_create_iteration(self):
        """Test creating an iteration."""
        iteration = Iteration(project_id="proj-123")
        assert iteration.project_id == "proj-123"
        assert iteration.state == IterationState.CREATED
        assert len(iteration.steps) == 0

    def test_iteration_state_transitions(self):
        """Test iteration state machine."""
        iteration = Iteration(project_id="proj-123")
        assert iteration.state == IterationState.CREATED

        iteration.start()
        assert iteration.state == IterationState.IN_PROGRESS

        iteration.freeze()
        assert iteration.state == IterationState.FROZEN

    def test_add_step(self):
        """Test adding workflow steps."""
        iteration = Iteration(project_id="proj-123")
        step = iteration.add_step("s0")
        assert len(iteration.steps) == 1
        assert step.step_id == "s0"
        assert iteration.get_step("s0") == step
