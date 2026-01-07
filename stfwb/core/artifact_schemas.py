"""Pydantic content schemas for S0–S5 artifacts.

These models define the structure of each artifact's `content` field
while remaining JSON-serializable via `model_dump(mode="json")`.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class S0Content(BaseModel):
    summary: str = Field(default="source snapshot")
    source_uri: str | None = None
    snapshot_time: str | None = None
    commit: str | None = None
    tree_hash: str | None = None
    files: list[str] | None = None


class Requirement(BaseModel):
    id: int
    text: str


class S1Content(BaseModel):
    summary: str = Field(default="requirements normalized")
    requirements: list[Requirement] | None = None
    count: int = 0
    source: str | None = None


class S2Content(BaseModel):
    summary: str = Field(default="protocol spec")
    modules: list[str] | None = None


class S3Check(BaseModel):
    name: str
    passed: bool


class S3Content(BaseModel):
    summary: str = Field(default="model checking results")
    passed: bool = False
    checks: list[S3Check] | None = None


class S4Content(BaseModel):
    summary: str = Field(default="evidence coverage")
    coverage: float = 0.0
    metrics: dict[str, float] | None = None


class S5Content(BaseModel):
    summary: str = Field(default="gate decision")
    decision: str = Field(default="undecided")
    reason: str | None = None
