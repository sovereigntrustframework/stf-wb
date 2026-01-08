"""Pydantic models for API requests and responses."""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class RunStatus(str, Enum):
    """Status of a workbench run."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class StepName(str, Enum):
    """STF workbench step names."""

    S0 = "S0"
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    S4 = "S4"
    S5 = "S5"


class ProjectInfo(BaseModel):
    """Project information."""

    id: str
    repo_owner: str
    repo_name: str
    branch: str
    spec_path: str


class RunInfo(BaseModel):
    """Run information."""

    id: str
    project_id: str
    status: RunStatus
    current_step: StepName | None
    created_at: datetime
    updated_at: datetime
    error: str | None = None


class StepResult(BaseModel):
    """Step execution result."""

    step: StepName
    status: str
    artifact_path: str | None = None
    error: str | None = None
