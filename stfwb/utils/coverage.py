"""Coverage computation algorithm from STF-Workbench v0.2.0 Section 6.4.1."""

from typing import Any

from pydantic import BaseModel, Field

from stfwb.core.types import CoverageUnit


class Coverage(BaseModel):
    """Coverage metrics (Section 6.4.1)."""

    unit: CoverageUnit = Field(..., description="Coverage unit")
    covered: int = Field(..., description="Number of covered items")
    total: int = Field(..., description="Total number of items")
    gaps: list[str] = Field(default_factory=list, description="Uncovered items")

    @property
    def percentage(self) -> float:
        """Compute coverage percentage."""
        if self.total == 0:
            return 0.0
        return (self.covered / self.total) * 100.0

    @property
    def is_complete(self) -> bool:
        """Check if coverage is 100%."""
        return self.covered == self.total

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "unit": self.unit.value,
            "covered": self.covered,
            "total": self.total,
            "percentage": self.percentage,
            "gaps": self.gaps,
        }
