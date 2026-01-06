"""Pydantic content schemas for S0–S5 artifacts.

These models define the structure of each artifact's `content` field
while remaining JSON-serializable via `model_dump(mode="json")`.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class S0Content(BaseModel):
    summary: str = Field(default="source snapshot")
    files: Optional[List[str]] = None


class S1Content(BaseModel):
    summary: str = Field(default="requirements normalized")
    requirements: Optional[List[str]] = None


class S2Content(BaseModel):
    summary: str = Field(default="protocol spec")
    modules: Optional[List[str]] = None


class S3Check(BaseModel):
    name: str
    passed: bool


class S3Content(BaseModel):
    summary: str = Field(default="model checking results")
    passed: bool = False
    checks: Optional[List[S3Check]] = None


class S4Content(BaseModel):
    summary: str = Field(default="evidence coverage")
    coverage: float = 0.0
    metrics: Optional[Dict[str, float]] = None


class S5Content(BaseModel):
    summary: str = Field(default="gate decision")
    decision: str = Field(default="undecided")
    reason: Optional[str] = None
