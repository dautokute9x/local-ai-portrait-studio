import os
import sys
from pathlib import Path

# Run Qt without a visible window (works on Windows, Linux and CI).
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Make `import app` work when pytest is run from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


import pytest  # noqa: E402


@pytest.fixture
def window(qtbot, tmp_path):
    """MainWindow with settings stored in a temp INI file (not the real registry)."""
    from PySide6.QtCore import QSettings

    from app.ui.main_window import MainWindow

    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    win = MainWindow(settings)
    qtbot.addWidget(win)
    win.show()
    return win
