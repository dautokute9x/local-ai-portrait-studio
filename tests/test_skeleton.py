import logging

import app
from app.core import paths
from app.core.logging_setup import LOG_FILE_NAME, setup_logging


def test_package_metadata():
    assert app.APP_NAME == "Local AI Portrait Studio"
    assert app.__version__.count(".") == 2


def test_paths_are_relative_to_project_root():
    assert (paths.PROJECT_ROOT / "app" / "__init__.py").is_file()
    assert paths.MODELS_DIR.parent == paths.PROJECT_ROOT
    assert paths.LOGS_DIR.parent == paths.PROJECT_ROOT


def test_setup_logging_writes_file_and_is_idempotent(tmp_path):
    log_file = setup_logging(tmp_path)
    setup_logging(tmp_path)  # second call must not duplicate handlers
    ours = [h for h in logging.getLogger().handlers if getattr(h, "_portrait_studio", False)]
    assert len(ours) == 2  # one file + one console

    logging.getLogger("test").info("hello from test")
    for h in ours:
        h.flush()
    assert log_file.name == LOG_FILE_NAME
    assert "hello from test" in log_file.read_text(encoding="utf-8")


def test_main_window_opens(window):
    assert window.isVisible()
    assert "Local AI Portrait Studio" in window.windowTitle()


def test_excepthook_logs_instead_of_crashing(qtbot, monkeypatch, caplog):
    import sys

    from PySide6.QtWidgets import QMessageBox

    from app import main

    shown = []
    monkeypatch.setattr(QMessageBox, "critical", lambda *a, **k: shown.append(a))
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)  # restored after test
    main._install_excepthook()

    try:
        raise ValueError("boom")
    except ValueError:
        sys.excepthook(*sys.exc_info())

    assert "Unhandled exception" in caplog.text
    assert shown and "boom" in shown[0][2]
