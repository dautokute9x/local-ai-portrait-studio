import os
import sys
from pathlib import Path


def _offscreen_platform() -> str:
    """Headless Qt with a 1920x1080 virtual screen (the default one is 800x800,
    smaller than the app's minimum window size).

    The config path must be relative: Qt splits platform arguments on ':',
    which would break a Windows drive letter such as C:\\.
    """
    config = Path(__file__).with_name("offscreen_screen.json")
    try:
        rel = Path(os.path.relpath(config)).as_posix()
    except ValueError:  # different drive on Windows
        return "offscreen"
    return "offscreen" if ":" in rel else f"offscreen:configfile={rel}"


# Run Qt without a visible window (works on Windows, Linux and CI).
os.environ.setdefault("QT_QPA_PLATFORM", _offscreen_platform())

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
