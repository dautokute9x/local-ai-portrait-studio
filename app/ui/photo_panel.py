"""Left panel: list of opened photos (thumbnails arrive in Step 1.4)."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QLabel, QListWidget, QVBoxLayout

THUMBNAIL_SIZE = 128  # display size; thumbnails are generated at 256 px


class PhotoPanel(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("SidePanel")
        self.setMinimumWidth(160)

        title = QLabel("Photos")
        title.setObjectName("PanelTitle")

        self.list = QListWidget()
        self.list.setViewMode(QListWidget.ViewMode.IconMode)
        self.list.setIconSize(QSize(THUMBNAIL_SIZE, THUMBNAIL_SIZE))
        self.list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list.setMovement(QListWidget.Movement.Static)
        self.list.setSpacing(6)
        self.list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)

        self.empty_hint = QLabel("Chưa có ảnh.\nFile → Open Image (Ctrl+O)")
        self.empty_hint.setObjectName("Hint")
        self.empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(title)
        layout.addWidget(self.empty_hint, 1)
        layout.addWidget(self.list, 1)
        self.list.hide()
