"""Type definitions and constants from STF-Workbench v0.2.0 spec."""

from enum import Enum

class IterationState(str, Enum):
    """Iteration state machine (Section 6.2)."""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    FROZEN = "frozen"
    ARCHIVED = "archived"

class GateDecision(str, Enum):
    """Gate decision outcomes (Section 6.3)."""
    APPROVE = "approve"
    REJECT = "reject"
    CONDITIONAL = "conditional"

class ArtifactKind(str, Enum):
    """Artifact kinds (Section 6.5)."""
    SOURCE = "s0.a"
    REQUIREMENTS = "s1.a"
    PROTOCOL = "s2.a"
    MODEL_CHECK = "s3.a"
    EVIDENCE = "s4.a"
    GATE = "s5.a"

class CoverageUnit(str, Enum):
    """Coverage computation units (Section 6.4.1)."""
    FRAGMENTS = "fragments"
    SECTIONS = "sections"