"""Application entry point: logging, crash guard, QApplication, main window."""

from __future__ import annotations

import logging
import platform
import sys
import traceback
from types import TracebackType

from PySide6.QtCore import qVersion
from PySide6.QtWidgets import QApplication, QMessageBox

from app import APP_ID, APP_NAME, __version__
from app.core.logging_setup import setup_logging
from app.ui.main_window import MainWindow
from app.ui.theme import apply_dark_theme

log = logging.getLogger(__name__)


def _install_excepthook() -> None:
    """Log uncaught exceptions and show them in a dialog instead of exiting.

    PySide6 aborts the process on an unhandled exception inside a slot unless
    a custom excepthook is installed, so this is what keeps the app alive.
    """

    def hook(
        exc_type: type[BaseException],
        exc: BaseException,
        tb: TracebackType | None,
    ) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc, tb)
            return
        log.critical("Unhandled exception", exc_info=(exc_type, exc, tb))
        if QApplication.instance() is not None:
            QMessageBox.critical(
                None,
                APP_NAME,
                f"Đã xảy ra lỗi không mong muốn:\n\n{exc}\n\n"
                "Chi tiết đã được ghi vào logs/app.log.",
            )
        else:
            traceback.print_exception(exc_type, exc, tb)

    sys.excepthook = hook


def run(argv: list[str] | None = None) -> int:
    log_file = setup_logging()
    log.info(
        "Starting %s %s | Python %s | Qt %s | %s",
        APP_NAME,
        __version__,
        platform.python_version(),
        qVersion(),
        platform.platform(),
    )
    log.info("Log file: %s", log_file)
    _install_excepthook()

    app = QApplication(sys.argv if argv is None else argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_ID)
    app.setApplicationVersion(__version__)
    apply_dark_theme(app)

    window = MainWindow()
    window.show()
    code = app.exec()
    log.info("Exited with code %s", code)
    return code


if __name__ == "__main__":
    sys.exit(run())
