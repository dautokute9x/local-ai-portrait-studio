"""Logging to console + rotating file. Local only — nothing is sent anywhere."""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.paths import LOGS_DIR, ensure_dir

LOG_FORMAT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"
LOG_FILE_NAME = "app.log"


def setup_logging(log_dir: Path = LOGS_DIR, level: int = logging.INFO) -> Path:
    """Configure the root logger once. Returns the log file path.

    Safe to call more than once (e.g. from tests): previous handlers we
    installed are replaced instead of duplicated.
    """
    log_file = ensure_dir(log_dir) / LOG_FILE_NAME
    root = logging.getLogger()
    root.setLevel(level)

    for handler in list(root.handlers):
        if getattr(handler, "_portrait_studio", False):
            root.removeHandler(handler)
            handler.close()

    formatter = logging.Formatter(LOG_FORMAT)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    console_handler = logging.StreamHandler(sys.stderr)
    for handler in (file_handler, console_handler):
        handler.setFormatter(formatter)
        handler._portrait_studio = True  # type: ignore[attr-defined]
        root.addHandler(handler)

    return log_file
