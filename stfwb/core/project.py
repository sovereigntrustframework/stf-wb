"""Project model from STF-Workbench v0.2.0 Section 6.1."""

import uuid
from datetime import UTC, datetime
from typing import Optional

from pydantic import BaseModel, Field
from stfwb.core.schemas import JsonObject


class Project(BaseModel):
    """Project model (Section 6.1).

    Represents a verification project targeting a specific specification.
    """

    kind: str = Field(default="project", description="Resource kind")
    version: str = Field(default="0.2.0", description="Schema version")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Project ID")
    name: str = Field(..., description="Project name")
    target_uri: str = Field(..., description="Target specification URI")
    metadata: JsonObject = Field(default_factory=dict, description="Custom metadata")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Creation time",
    )
    updated_at: Optional[datetime] = Field(None, description="Last update time")

    def to_dict(self) -> JsonObject:
        """Serialize project to dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Project":
        """Deserialize project from dictionary."""
        return cls(**data)  # pyright: ignore[reportArgumentType]

    def is_valid(self) -> bool:
        """Validate project state."""
        return bool(self.id and self.name and self.target_uri)
