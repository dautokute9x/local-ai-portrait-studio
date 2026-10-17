"""Collapsible panel section with a header (arrow + title + reset button)."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.ui.icon_loader import icon


class CollapsibleSection(QFrame):
    reset_requested = Signal()

    def __init__(self, title: str, expanded: bool = True) -> None:
        super().__init__()
        self.setObjectName("Section")

        self.toggle = QToolButton()
        self.toggle.setObjectName("SectionHeader")
        self.toggle.setText(title)
        self.toggle.setCheckable(True)
        self.toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toggle.toggled.connect(self.set_expanded)

        self.reset_button = QToolButton()
        self.reset_button.setObjectName("SectionReset")
        self.reset_button.setText("Reset")
        self.reset_button.setIcon(icon("rotate-ccw"))
        self.reset_button.setIconSize(QSize(13, 13))
        self.reset_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.reset_button.setToolTip(f"Đặt lại nhóm {title}")
        self.reset_button.clicked.connect(self.reset_requested)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(self.toggle, 1)
        header.addWidget(self.reset_button)

        self.content = QWidget()
        self.body = QVBoxLayout(self.content)
        self.body.setContentsMargins(14, 2, 0, 8)
        self.body.setSpacing(2)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(header)
        layout.addWidget(self.content)

        self.toggle.setChecked(expanded)
        self.set_expanded(expanded)

    def set_expanded(self, expanded: bool) -> None:
        self.toggle.setArrowType(
            Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow
        )
        if self.toggle.isChecked() != expanded:
            self.toggle.setChecked(expanded)
        self.content.setVisible(expanded)

    def is_expanded(self) -> bool:
        return self.toggle.isChecked()

    def add_widget(self, widget: QWidget) -> None:
        self.body.addWidget(widget)
