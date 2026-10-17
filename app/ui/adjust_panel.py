"""Right panel: adjustment sliders.

In Phase 1 the sliders are shown disabled so the final layout can be
reviewed; each one is enabled by the phase that implements it.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)


@dataclass(frozen=True)
class SliderSpec:
    key: str          # parameter name in EditParams (Phase 4+)
    label: str
    minimum: int
    maximum: int
    available_in: str  # shown as tooltip while disabled


PORTRAIT_SLIDERS: tuple[SliderSpec, ...] = (
    SliderSpec("skin_smooth", "Skin Smooth", 0, 100, "Phase 4"),
    SliderSpec("eye_brightness", "Eye Brightness", 0, 100, "Phase 5"),
    SliderSpec("teeth_whitening", "Teeth Whitening", 0, 100, "Phase 5"),
    SliderSpec("face_width", "Face Width", -50, 50, "Phase 6"),
)


class SliderRow(QWidget):
    """Label + numeric value on one line, slider below. Double-click resets."""

    value_changed = Signal(str, int)

    def __init__(self, spec: SliderSpec) -> None:
        super().__init__()
        self.spec = spec
        self.default = 0 if spec.minimum <= 0 <= spec.maximum else spec.minimum

        self.name_label = QLabel(spec.label)
        self.value_label = QLabel(str(self.default))
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.value_label.setMinimumWidth(32)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(spec.minimum, spec.maximum)
        self.slider.setValue(self.default)
        self.slider.valueChanged.connect(self._on_value)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(self.name_label)
        header.addStretch(1)
        header.addWidget(self.value_label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(2)
        layout.addLayout(header)
        layout.addWidget(self.slider)

    def _on_value(self, value: int) -> None:
        self.value_label.setText(str(value))
        self.value_changed.emit(self.spec.key, value)

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        if self.isEnabled():
            self.slider.setValue(self.default)
        super().mouseDoubleClickEvent(event)


class AdjustPanel(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("SidePanel")
        self.setMinimumWidth(240)

        title = QLabel("Adjustments")
        title.setObjectName("PanelTitle")

        content = QWidget()
        body = QVBoxLayout(content)
        body.setContentsMargins(12, 0, 12, 12)
        body.setSpacing(2)

        section = QLabel("PORTRAIT")
        section.setObjectName("SectionTitle")
        body.addWidget(section)

        self.rows: dict[str, SliderRow] = {}
        for spec in PORTRAIT_SLIDERS:
            row = SliderRow(spec)
            row.setEnabled(False)
            row.setToolTip(f"Có từ {spec.available_in}")
            self.rows[spec.key] = row
            body.addWidget(row)
        body.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(content)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(title)
        layout.addWidget(scroll, 1)
