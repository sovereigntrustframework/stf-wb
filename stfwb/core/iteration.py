"""Iteration model from STF-Workbench v0.2.0 Section 6.2."""

import uuid
from datetime import UTC, datetime
from typing import Optional

from pydantic import BaseModel, Field

from stfwb.core.types import IterationState
from stfwb.core.schemas import JsonObject


class IterationStep(BaseModel):
    """Single step in iteration workflow."""

    step_id: str = Field(..., description="Step identifier (s0-s5)")
    status: str = Field(default="pending", description="Step status")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[JsonObject] = None


def _new_steps() -> list["IterationStep"]:
    return []


def _new_meta() -> JsonObject:
    return {}


class Iteration(BaseModel):
    """Iteration model (Section 6.2).

    Represents a single verification iteration through S0→S5 workflow.
    """

    kind: str = Field(default="iteration", description="Resource kind")
    version: str = Field(default="0.2.0", description="Schema version")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Iteration ID")
    project_id: str = Field(..., description="Parent project ID")
    state: IterationState = Field(default=IterationState.CREATED, description="Iteration state")
    steps: list[IterationStep] = Field(default_factory=_new_steps, description="Workflow steps")
    metadata: JsonObject = Field(default_factory=_new_meta, description="Custom metadata")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Creation time",
    )
    updated_at: Optional[datetime] = Field(None, description="Last update time")

    def to_dict(self) -> JsonObject:
        """Serialize iteration to dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Iteration":
        """Deserialize iteration from dictionary."""
        return cls(**data)  # pyright: ignore[reportArgumentType]

    def start(self) -> None:
        """Transition from created → in_progress."""
        if self.state == IterationState.CREATED:
            self.state = IterationState.IN_PROGRESS
            self.updated_at = datetime.now(UTC)

    def freeze(self) -> None:
        """Transition from in_progress → frozen."""
        if self.state == IterationState.IN_PROGRESS:
            self.state = IterationState.FROZEN
            self.updated_at = datetime.now(UTC)

    def archive(self) -> None:
        """Transition to archived state."""
        self.state = IterationState.ARCHIVED
        self.updated_at = datetime.now(UTC)

    def get_step(self, step_id: str) -> Optional[IterationStep]:
        """Get step by ID."""
        return next((s for s in self.steps if s.step_id == step_id), None)

    def add_step(self, step_id: str) -> IterationStep:
        """Add workflow step."""
        step = IterationStep(step_id=step_id)
        self.steps.append(step)
        return step
