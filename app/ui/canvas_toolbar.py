"""Toolbar above the image canvas: tools, Before/After and zoom."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QToolButton,
)


@dataclass(frozen=True)
class ToolSpec:
    key: str
    label: str
    shortcut: str
    tooltip: str
    available_in: str


TOOLS: tuple[ToolSpec, ...] = (
    ToolSpec("pan", "Pan", "H", "Kéo để di chuyển ảnh", "Step 1.5"),
    ToolSpec("blemish", "Blemish", "B", "Blemish Brush: click/tô vùng mụn", "Phase 5"),
    ToolSpec("remove", "Remove", "R", "Object Removal: tô vùng cần xóa", "Phase 8"),
)

ZOOM_PRESETS = ("Fit", "25%", "50%", "100%", "200%", "400%")


class CanvasToolbar(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("CanvasToolbar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)
        self.tool_buttons: dict[str, QToolButton] = {}
        for spec in TOOLS:
            button = QToolButton()
            button.setText(spec.label)
            button.setCheckable(True)
            button.setToolTip(f"{spec.tooltip} ({spec.shortcut}) — có từ {spec.available_in}")
            button.setEnabled(False)
            self.tool_group.addButton(button)
            self.tool_buttons[spec.key] = button
            layout.addWidget(button)

        layout.addSpacing(12)
        self.before_after = QToolButton()
        self.before_after.setText("Before / After")
        self.before_after.setCheckable(True)
        self.before_after.setToolTip("So sánh ảnh gốc (\\) — có từ Phase 4")
        self.before_after.setEnabled(False)
        layout.addWidget(self.before_after)

        layout.addStretch(1)
        layout.addWidget(QLabel("Zoom"))
        self.zoom = QComboBox()
        self.zoom.addItems(ZOOM_PRESETS)
        self.zoom.setEnabled(False)
        self.zoom.setToolTip("Có từ Step 1.5")
        layout.addWidget(self.zoom)
