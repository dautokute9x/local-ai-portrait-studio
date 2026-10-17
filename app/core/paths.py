"""Well-known project directories, resolved relative to this file (no absolute paths)."""

from __future__ import annotations

from pathlib import Path

# app/core/paths.py -> project root is two levels above the `app` package.
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
MODELS_DIR: Path = PROJECT_ROOT / "models"
LOGS_DIR: Path = PROJECT_ROOT / "logs"
DEFAULT_OUTPUT_DIR: Path = PROJECT_ROOT / "output"


def ensure_dir(path: Path) -> Path:
    """Create `path` (and parents) if missing and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path
