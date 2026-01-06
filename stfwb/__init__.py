"""STF-WB: Reference implementation of STF-Workbench v0.2.0 specification."""

__version__ = "0.1.0-alpha"
__author__ = "Sovereign Trust Framework"
__license__ = "MIT"

from stfwb.core.artifact import Artifact
from stfwb.core.iteration import Iteration
from stfwb.core.project import Project

__all__ = [
    "Project",
    "Iteration",
    "Artifact",
]
