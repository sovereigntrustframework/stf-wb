"""Iteration model from STF-Workbench v0.2.0 Section 6.2."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from stfwb.core.types import IterationState
import uuid

class IterationStep(BaseModel):
    """Single step in iteration workflow."""
    step_id: str = Field(..., description="Step identifier (s0-s5)")
    status: str = Field(default="pending", description="Step status")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None

class Iteration(BaseModel):
    """Iteration model (Section 6.2).
    
    Represents a single verification iteration through S0→S5 workflow.
    """
    kind: str = Field(default="iteration", description="Resource kind")
    version: str = Field(default="0.2.0", description="Schema version")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Iteration ID")
    project_id: str = Field(..., description="Parent project ID")
    state: IterationState = Field(default=IterationState.CREATED, description="Iteration state")
    steps: List[IterationStep] = Field(default_factory=list, description="Workflow steps")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Last update time")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize iteration to dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Iteration":
        """Deserialize iteration from dictionary."""
        return cls(**data)

    def start(self) -> None:
        """Transition from created → in_progress."""
        if self.state == IterationState.CREATED:
            self.state = IterationState.IN_PROGRESS
            self.updated_at = datetime.utcnow()

    def freeze(self) -> None:
        """Transition from in_progress → frozen."""
        if self.state == IterationState.IN_PROGRESS:
            self.state = IterationState.FROZEN
            self.updated_at = datetime.utcnow()

    def archive(self) -> None:
        """Transition to archived state."""
        self.state = IterationState.ARCHIVED
        self.updated_at = datetime.utcnow()

    def get_step(self, step_id: str) -> Optional[IterationStep]:
        """Get step by ID."""
        return next((s for s in self.steps if s.step_id == step_id), None)

    def add_step(self, step_id: str) -> IterationStep:
        """Add workflow step."""
        step = IterationStep(step_id=step_id)
        self.steps.append(step)
        return step