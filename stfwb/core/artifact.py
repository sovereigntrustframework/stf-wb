"""Artifact models (S0.A through S5.A) from STF-Workbench v0.2.0 Section 6.5."""

from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field

class ArtifactMetadata(BaseModel):
    """Common artifact metadata (Section 6.1)."""
    kind: str = Field(..., description="Artifact kind")
    version: str = Field(..., description="Artifact version")
    id: str = Field(..., description="Unique artifact ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")

class Artifact(BaseModel):
    """Base artifact class for S0.A through S5.A."""
    metadata: ArtifactMetadata
    content: Dict[str, Any] = Field(default_factory=dict, description="Artifact content")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize artifact to dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Artifact":
        """Deserialize artifact from dictionary."""
        return cls(**data)

class S0Artifact(Artifact):
    """Source snapshot artifact (S0.A - Section 6.5.1)."""
    content: Dict[str, Any] = Field(default_factory=dict, description="Source snapshot")

class S1Artifact(Artifact):
    """Normalized requirements artifact (S1.A - Section 6.5.2)."""
    content: Dict[str, Any] = Field(default_factory=dict, description="Structured requirements")

class S2Artifact(Artifact):
    """Protocol specification artifact (S2.A - Section 6.5.3)."""
    content: Dict[str, Any] = Field(default_factory=dict, description="TLA+ module")

class S3Artifact(Artifact):
    """Model checking results artifact (S3.A - Section 6.5.4)."""
    content: Dict[str, Any] = Field(default_factory=dict, description="TLC results")

class S4Artifact(Artifact):
    """Evidence collection artifact (S4.A - Section 6.5.5)."""
    content: Dict[str, Any] = Field(default_factory=dict, description="Coverage metrics")

class S5Artifact(Artifact):
    """Gate derivation artifact (S5.A - Section 6.5.6)."""
    content: Dict[str, Any] = Field(default_factory=dict, description="Gate decision")