"""Configuration management for STF-WB.

Loads stfwb.yaml from home or project directory with env var overrides.
Priority: env vars > stfwb.yaml > defaults.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]  # pragma: no cover


class Config:
    """Configuration container with yaml and env var support."""

    def __init__(self) -> None:
        self.store_dir: str | None = None
        self.log_file: str | None = None
        self.github_token: str | None = None
        self.github_repo: str | None = None
        self.verbose: int = 0
        self.quiet: bool = False
        self._load()

    def _load(self) -> None:
        """Load config from yaml and env vars."""
        # Try to load yaml from home or current directory
        yaml_path = self._find_config_file()
        yaml_config: dict[str, Any] = {}
        if yaml_path:
            yaml_config = self._load_yaml(yaml_path)

        # Set from yaml
        if yaml_config.get("store_dir"):
            self.store_dir = yaml_config["store_dir"]
        if yaml_config.get("log_file"):
            self.log_file = yaml_config["log_file"]
        if yaml_config.get("github_token"):
            self.github_token = yaml_config["github_token"]
        if yaml_config.get("github_repo"):
            self.github_repo = yaml_config["github_repo"]
        if "verbose" in yaml_config:
            self.verbose = int(yaml_config["verbose"])
        if "quiet" in yaml_config:
            self.quiet = bool(yaml_config["quiet"])

        # Override with env vars
        if os.getenv("STFWB_STORE_DIR"):
            self.store_dir = os.getenv("STFWB_STORE_DIR")
        if os.getenv("STFWB_LOG_FILE"):
            self.log_file = os.getenv("STFWB_LOG_FILE")
        if os.getenv("STFWB_GITHUB_TOKEN"):
            self.github_token = os.getenv("STFWB_GITHUB_TOKEN")
        if os.getenv("STFWB_GITHUB_REPO"):
            self.github_repo = os.getenv("STFWB_GITHUB_REPO")
        if os.getenv("STFWB_VERBOSE"):
            self.verbose = int(os.getenv("STFWB_VERBOSE", "0"))
        if os.getenv("STFWB_QUIET"):
            self.quiet = os.getenv("STFWB_QUIET", "").lower() in ("1", "true", "yes")

    def _find_config_file(self) -> Path | None:
        """Find stfwb.yaml in home or current directory."""
        home_config = Path.home() / ".stfwb" / "stfwb.yaml"
        if home_config.exists():
            return home_config
        current_config = Path.cwd() / "stfwb.yaml"
        if current_config.exists():
            return current_config
        return None

    def _load_yaml(self, path: Path) -> dict[str, Any]:
        """Load yaml config file."""
        if yaml is None:  # pragma: no cover
            return {}
        try:
            content = path.read_text(encoding="utf-8")
            loaded = yaml.safe_load(content)
            return loaded if isinstance(loaded, dict) else {}
        except Exception:  # pragma: no cover
            return {}


_instance: Config | None = None


def get_config() -> Config:
    """Get or create the global config instance."""
    global _instance
    if _instance is None:
        _instance = Config()
    return _instance
