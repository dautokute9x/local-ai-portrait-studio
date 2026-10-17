"""Main application window (Step 1.1: empty shell; layout comes in Step 1.2)."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMainWindow
from PySide6.QtCore import Qt

from app import APP_NAME, __version__


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {__version__}")
        self.resize(1400, 900)
        self.setMinimumSize(900, 600)

        placeholder = QLabel("Local AI Portrait Studio — skeleton OK")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(placeholder)
        self.statusBar().showMessage("Ready")
