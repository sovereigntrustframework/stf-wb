"""Step runner for S0→S5 workflow.

Provides helpers to execute iteration steps sequentially and attach
results to `Iteration.steps` with timestamps and statuses.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Final, Literal

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
    Requirement,
    S0Content,
    S1Content,
    S2Content,
    S3Content,
    S4Content,
    S5Content,
)
from stfwb.core.iteration import Iteration, IterationStep
from stfwb.utils.logging import get_logger

_STEP_IDS: Final[list[str]] = ["s0", "s1", "s2", "s3", "s4", "s5"]
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


def _list_files(base: Path, limit: int = 200) -> list[str]:
    """Return up to `limit` relative file paths under base."""
    paths: list[str] = []
    for root, _dirs, files in os.walk(base):  # type: ignore[name-defined]
        for name in files:
            rel = Path(root, name).relative_to(base)
            paths.append(str(rel))
            if len(paths) >= limit:
                return paths
    return paths


def _hash_tree(base: Path) -> str:
    """Compute a deterministic hash of file contents under base."""
    sha = hashlib.sha256()
    for root, _dirs, files in os.walk(base):  # type: ignore[name-defined]
        for name in sorted(files):
            full = Path(root, name)
            sha.update(str(full.relative_to(base)).encode("utf-8"))
            with full.open("rb") as f:
                while chunk := f.read(8192):
                    sha.update(chunk)
    return sha.hexdigest()


def _default_s0_artifact(iteration: Iteration) -> S0Artifact:
    """Generate a default S0 artifact by snapshotting the target source."""
    target_uri = iteration.metadata.get("target_uri") if iteration.metadata else None
    now = datetime.now(UTC)
    meta = ArtifactMetadata(kind="s0.a", version="0.2.0", id=f"s0-{int(now.timestamp())}")

    if not target_uri:
        content = S0Content(summary="source snapshot (no target)")
        return S0Artifact(metadata=meta, content=content.model_dump(mode="json"))

    snapshot_time = now.isoformat()

    def _content_from_local(path: Path) -> S0Content:
        if not path.exists():
            raise FileNotFoundError(f"Target path does not exist: {path}")
        tree_hash = _hash_tree(path)
        files = _list_files(path)
        return S0Content(
            summary="source snapshot (local)",
            source_uri=str(path),
            snapshot_time=snapshot_time,
            commit=None,
            tree_hash=tree_hash,
            files=files,
        )

    def _content_from_git(uri: str) -> S0Content:
        tmpdir = Path(tempfile.mkdtemp(prefix="stfwb-s0-"))
        try:
            subprocess.run(
                ["git", "clone", "--depth=1", uri, str(tmpdir)],
                check=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
            head = subprocess.run(
                ["git", "-C", str(tmpdir), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
                timeout=15,
            )
            commit = head.stdout.strip()
            files = _list_files(tmpdir)
            return S0Content(
                summary="source snapshot (git)",
                source_uri=uri,
                snapshot_time=snapshot_time,
                commit=commit,
                tree_hash=None,
                files=files,
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    if str(target_uri).startswith(("http://", "https://", "git@", "ssh://")):
        content = _content_from_git(str(target_uri))
    else:
        content = _content_from_local(Path(str(target_uri)))

    return S0Artifact(metadata=meta, content=content.model_dump(mode="json"))


def _default_s1_artifact(iteration: Iteration) -> S1Artifact:
    """Generate a default S1 artifact by normalizing requirements from local markdown.

    Rules:
    - If target_uri is a local path, scan *.md files for lines containing RFC 2119 keywords
      (MUST, MUST NOT, SHALL, SHALL NOT, SHOULD, SHOULD NOT, MAY) or "REQ:" prefix.
    - Build structured requirements with incremental IDs.
    - If target_uri is remote or missing, return empty requirements and summary.
    """
    now = datetime.now(UTC)
    meta = ArtifactMetadata(kind="s1.a", version="0.2.0", id=f"s1-{int(now.timestamp())}")
    target_uri = iteration.metadata.get("target_uri") if iteration.metadata else None

    if not target_uri:
        return S1Artifact(metadata=meta, content=S1Content().model_dump(mode="json"))

    # Remote URIs: produce empty normalized content
    if str(target_uri).startswith(("http://", "https://", "git@", "ssh://")):
        content = S1Content(
            summary="requirements normalized (remote)",
            requirements=[],
            count=0,
            source=str(target_uri),
        )
        return S1Artifact(metadata=meta, content=content.model_dump(mode="json"))

    # Local path: scan markdown files
    base = Path(str(target_uri))
    if not base.exists():
        # Mirror S0 behavior: error if local path missing
        raise FileNotFoundError(f"Target path does not exist: {base}")

    reqs: list[Requirement] = []
    for root, _dirs, files in os.walk(base):  # type: ignore[name-defined]
        for name in files:
            if not name.lower().endswith(".md"):
                continue
            full = Path(root, name)
            try:
                for line in full.read_text(encoding="utf-8").splitlines():
                    stripped = line.strip()
                    # Match RFC 2119 keywords or REQ: prefix
                    if stripped.startswith("REQ:"):
                        text = line.split("REQ:", 1)[1].strip()
                        reqs.append(Requirement(id=len(reqs) + 1, text=text))
                    elif any(kw in stripped for kw in [" MUST ", " SHALL ", " SHOULD ", " MAY "]):
                        # Capture full sentence containing RFC 2119 keyword
                        reqs.append(Requirement(id=len(reqs) + 1, text=stripped))
            except Exception:
                # Skip unreadable files
                continue

    content = S1Content(
        summary="requirements normalized (local)",
        requirements=reqs,
        count=len(reqs),
        source=str(base),
    )
    return S1Artifact(metadata=meta, content=content.model_dump(mode="json"))


def _make_artifact(
    iteration: Iteration, step_id: str
) -> S0Artifact | S1Artifact | S2Artifact | S3Artifact | S4Artifact | S5Artifact:
    """Create an artifact for a step, using plugin if registered, else default."""
    from stfwb.steps.plugin import get_plugin

    # Check if a plugin is registered for this step
    plugin = get_plugin(step_id)
    if plugin is not None:
        return plugin(iteration, step_id)

    # Default artifact generation
    now = datetime.now(UTC)
    if step_id == "s0":
        return _default_s0_artifact(iteration)
    if step_id == "s1":
        return _default_s1_artifact(iteration)
    if step_id == "s2":
        meta = ArtifactMetadata(
            kind="s2.a", version="0.2.0", id=f"{step_id}-{int(now.timestamp())}"
        )
        return S2Artifact(metadata=meta, content=S2Content().model_dump(mode="json"))
    if step_id == "s3":
        meta = ArtifactMetadata(
            kind="s3.a", version="0.2.0", id=f"{step_id}-{int(now.timestamp())}"
        )
        return S3Artifact(metadata=meta, content=S3Content().model_dump(mode="json"))
    if step_id == "s4":
        meta = ArtifactMetadata(
            kind="s4.a", version="0.2.0", id=f"{step_id}-{int(now.timestamp())}"
        )
        return S4Artifact(metadata=meta, content=S4Content().model_dump(mode="json"))
    # s5
    meta = ArtifactMetadata(kind="s5.a", version="0.2.0", id=f"{step_id}-{int(now.timestamp())}")
    return S5Artifact(metadata=meta, content=S5Content().model_dump(mode="json"))


def run_next_step(
    iteration: Iteration, action: Literal["normal", "skip", "redo"] = "normal"
) -> IterationStep | None:
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
        art = _make_artifact(iteration, prev_step_id)
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
    art = _make_artifact(iteration, step_id)
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


def run_steps(
    iteration: Iteration, count: int, action: Literal["normal", "skip", "redo"] = "normal"
) -> list[IterationStep]:
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
