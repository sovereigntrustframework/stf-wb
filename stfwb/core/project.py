"""Project model from STF-Workbench v0.2.0 Section 6.1."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid

class Project(BaseModel):
    """Project model (Section 6.1).
    
    Represents a verification project targeting a specific specification.
    """
    kind: str = Field(default="project", description="Resource kind")
    version: str = Field(default="0.2.0", description="Schema version")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Project ID")
    name: str = Field(..., description="Project name")
    target_uri: str = Field(..., description="Target specification URI")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Last update time")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize project to dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """Deserialize project from dictionary."""
        return cls(**data)

    def validate(self) -> bool:
        """Validate project state."""
        return bool(self.id and self.name and self.target_uri)