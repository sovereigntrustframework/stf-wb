"""Logging utilities for STF-WB.

Provides setup and configuration for standard logging with
optional file output and level management.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Literal

_Initialized = False
_LogFile: Path | None = None


def setup_logging(
    level: Literal["ERROR", "WARNING", "INFO", "DEBUG"],
    log_file: Path | None = None,
) -> None:
    """Configure root logger with console and optional file handlers.

    Args:
        level: Log level (ERROR, WARNING, INFO, DEBUG).
        log_file: Optional path to write logs to file as well.
    """
    global _Initialized, _LogFile
    root = logging.getLogger()

    if not _Initialized:
        import sys

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        root.addHandler(console_handler)
        _Initialized = True

    # Update root level
    root.setLevel(getattr(logging, level))

    # File handler
    if log_file is not None and (not _LogFile or _LogFile != log_file):
        # Remove old file handler if exists
        for h in root.handlers[:]:
            if isinstance(h, logging.FileHandler):
                root.removeHandler(h)
        # Add new one
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        root.addHandler(file_handler)
        _LogFile = log_file


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

