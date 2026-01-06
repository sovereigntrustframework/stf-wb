"""Local JSON storage for projects and iterations.

Provides simple, strictly-typed helpers to persist Pydantic models
under a workspace directory (default: `.stfwb/`).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final

from stfwb.core.iteration import Iteration
from stfwb.core.project import Project
from stfwb.core.schemas import JsonObject
from stfwb.utils.logging import get_logger

DEFAULT_STORE_DIR: Final[str] = ".stfwb"

_log = get_logger("stfwb.storage")


def _ensure_dir(path: Path) -> None:
    if not path.exists():
        _log.debug(f"Creating directory {path}")
    path.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, data: JsonObject) -> None:
    _log.debug(f"Writing JSON to {path}")
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _read_json(path: Path) -> JsonObject:
    _log.debug(f"Reading JSON from {path}")
    text = path.read_text(encoding="utf-8")
    loaded = json.loads(text)
    if not isinstance(loaded, dict):
        raise ValueError("Expected JSON object at root")
    # json loads returns dict[str, Any]; it's JsonObject-compatible
    return loaded  # type: ignore[return-value]


def _projects_dir(root: Path) -> Path:
    return root / "projects"


def _iterations_dir(root: Path) -> Path:
    return root / "iterations"


def project_path(root: Path, project_id: str) -> Path:
    return _projects_dir(root) / f"{project_id}.json"


def iteration_path(root: Path, iteration_id: str) -> Path:
    return _iterations_dir(root) / f"{iteration_id}.json"


def save_project(project: Project, root: Path | None = None) -> Path:
    base = Path(root) if root is not None else Path(DEFAULT_STORE_DIR)
    _ensure_dir(_projects_dir(base))
    path = project_path(base, project.id)
    _log.info(f"Saving project {project.id} -> {path}")
    _write_json(path, project.to_dict())
    return path


def load_project(project_id: str, root: Path | None = None) -> Project:
    base = Path(root) if root is not None else Path(DEFAULT_STORE_DIR)
    path = project_path(base, project_id)
    _log.info(f"Loading project {project_id} from {path}")
    data = _read_json(path)
    return Project.from_dict(data)


def save_iteration(iteration: Iteration, root: Path | None = None) -> Path:
    base = Path(root) if root is not None else Path(DEFAULT_STORE_DIR)
    _ensure_dir(_iterations_dir(base))
    path = iteration_path(base, iteration.id)
    _log.info(f"Saving iteration {iteration.id} -> {path}")
    _write_json(path, iteration.to_dict())
    return path


def load_iteration(iteration_id: str, root: Path | None = None) -> Iteration:
    base = Path(root) if root is not None else Path(DEFAULT_STORE_DIR)
    path = iteration_path(base, iteration_id)
    _log.info(f"Loading iteration {iteration_id} from {path}")
    data = _read_json(path)
    return Iteration.from_dict(data)


def list_project_ids(root: Path | None = None) -> list[str]:
    base = Path(root) if root is not None else Path(DEFAULT_STORE_DIR)
    pdir = _projects_dir(base)
    if not pdir.exists():
        return []
    ids = [p.stem for p in pdir.glob("*.json") if p.is_file()]
    ids.sort()
    _log.debug(f"Found {len(ids)} projects under {pdir}")
    return ids


def list_iteration_ids(root: Path | None = None) -> list[str]:
    base = Path(root) if root is not None else Path(DEFAULT_STORE_DIR)
    idir = _iterations_dir(base)
    if not idir.exists():
        return []
    ids = [p.stem for p in idir.glob("*.json") if p.is_file()]
    ids.sort()
    _log.debug(f"Found {len(ids)} iterations under {idir}")
    return ids


def load_all_projects(root: Path | None = None) -> list[Project]:
    return [load_project(pid, root) for pid in list_project_ids(root)]


def load_all_iterations(root: Path | None = None) -> list[Iteration]:
    return [load_iteration(iid, root) for iid in list_iteration_ids(root)]


def delete_project(project_id: str, root: Path | None = None) -> None:
    base = Path(root) if root is not None else Path(DEFAULT_STORE_DIR)
    path = project_path(base, project_id)
    if not path.exists():
        raise FileNotFoundError(f"Project {project_id} not found")
    _log.info(f"Deleting project {project_id} at {path}")
    path.unlink()


def delete_iteration(iteration_id: str, root: Path | None = None) -> None:
    base = Path(root) if root is not None else Path(DEFAULT_STORE_DIR)
    path = iteration_path(base, iteration_id)
    if not path.exists():
        raise FileNotFoundError(f"Iteration {iteration_id} not found")
    _log.info(f"Deleting iteration {iteration_id} at {path}")
    path.unlink()
