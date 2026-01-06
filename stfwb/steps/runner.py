"""Step runner for S0→S5 workflow.

Provides helpers to execute iteration steps sequentially and attach
results to `Iteration.steps` with timestamps and statuses.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Final, List, Literal

from stfwb.core.artifact import (
    ArtifactMetadata,
    S0Artifact,
    S1Artifact,
    S2Artifact,
    S3Artifact,
    S4Artifact,
    S5Artifact,
)
from stfwb.core.artifact_schemas import (
    S0Content,
    S1Content,
    S2Content,
    S3Content,
    S4Content,
    S5Content,
)
from stfwb.core.iteration import Iteration, IterationStep
from stfwb.utils.logging import get_logger

_STEP_IDS: Final[List[str]] = ["s0", "s1", "s2", "s3", "s4", "s5"]
_log = get_logger("stfwb.runner")


def _achieved_count(iteration: Iteration) -> int:
    """Return how many sequential steps (s0..sN) have been achieved.

    A step is considered achieved if any entry exists for that `step_id`,
    regardless of status (completed/skipped). Redo does not advance the
    achieved count; it creates an additional entry for the last achieved step.
    """
    count = 0
    for step_id in _STEP_IDS:
        if any(s.step_id == step_id for s in iteration.steps):
            count += 1
        else:
            break
    return count


def _make_artifact(step_id: str) -> S0Artifact | S1Artifact | S2Artifact | S3Artifact | S4Artifact | S5Artifact:
    """Create an artifact for a step, using plugin if registered, else default."""
    from stfwb.steps.plugin import get_plugin

    # Check if a plugin is registered for this step
    plugin = get_plugin(step_id)
    if plugin is not None:
        return plugin(step_id)

    # Default artifact generation
    now = datetime.now(UTC)
    if step_id == "s0":
        meta = ArtifactMetadata(kind="s0.a", version="0.2.0", id=f"{step_id}-{int(now.timestamp())}")
        return S0Artifact(metadata=meta, content=S0Content().model_dump(mode="json"))
    if step_id == "s1":
        meta = ArtifactMetadata(kind="s1.a", version="0.2.0", id=f"{step_id}-{int(now.timestamp())}")
        return S1Artifact(metadata=meta, content=S1Content().model_dump(mode="json"))
    if step_id == "s2":
        meta = ArtifactMetadata(kind="s2.a", version="0.2.0", id=f"{step_id}-{int(now.timestamp())}")
        return S2Artifact(metadata=meta, content=S2Content().model_dump(mode="json"))
    if step_id == "s3":
        meta = ArtifactMetadata(kind="s3.a", version="0.2.0", id=f"{step_id}-{int(now.timestamp())}")
        return S3Artifact(metadata=meta, content=S3Content().model_dump(mode="json"))
    if step_id == "s4":
        meta = ArtifactMetadata(kind="s4.a", version="0.2.0", id=f"{step_id}-{int(now.timestamp())}")
        return S4Artifact(metadata=meta, content=S4Content().model_dump(mode="json"))
    # s5
    meta = ArtifactMetadata(kind="s5.a", version="0.2.0", id=f"{step_id}-{int(now.timestamp())}")
    return S5Artifact(metadata=meta, content=S5Content().model_dump(mode="json"))



def run_next_step(iteration: Iteration, action: Literal["normal", "skip", "redo"] = "normal") -> IterationStep | None:
    """Run the next step in S0→S5 sequence.

    Adds a new `IterationStep` with status 'completed', timestamps,
    and attaches artifact JSON into `result`.
    Returns the created step, or None if all steps are already completed.
    """
    completed = _achieved_count(iteration)
    if action not in ("normal", "skip", "redo"):
        raise ValueError(f"Unknown action '{action}'")

    # All steps completed
    if completed >= len(_STEP_IDS):
        return None

    now = datetime.now(UTC)

    if action == "skip":
        step_id = _STEP_IDS[completed]
        _log.info(f"Skipping step {step_id}")
        step = IterationStep(
            step_id=step_id,
            status="skipped",
            started_at=now,
            completed_at=now,
            result=None,
        )
        iteration.steps.append(step)
        iteration.updated_at = now
        return step

    if action == "redo":
        if completed == 0:
            raise ValueError("Cannot redo: no previous step exists")
        # Re-run the previous achieved step id
        prev_step_id = _STEP_IDS[completed - 1]
        _log.info(f"Redoing step {prev_step_id}")
        art = _make_artifact(prev_step_id)
        step = IterationStep(
            step_id=prev_step_id,
            status="completed",
            started_at=now,
            completed_at=now,
            result=art.to_dict(),
        )
        iteration.steps.append(step)
        iteration.updated_at = now
        return step

    # Normal run of next step
    step_id = _STEP_IDS[completed]
    _log.info(f"Running step {step_id}")
    art = _make_artifact(step_id)
    step = IterationStep(
        step_id=step_id,
        status="completed",
        started_at=now,
        completed_at=now,
        result=art.to_dict(),
    )
    iteration.steps.append(step)
    iteration.updated_at = now
    return step


def run_steps(iteration: Iteration, count: int, action: Literal["normal", "skip", "redo"] = "normal") -> list[IterationStep]:
    """Run up to `count` next steps, stopping when S5 is completed.

    Action applies to each execution: "normal" (default), "skip", or "redo".
    """
    out: list[IterationStep] = []
    for _ in range(count):
        step = run_next_step(iteration, action=action)
        if step is None:
            break
        out.append(step)
    return out
