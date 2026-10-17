"""Right panel: histogram + collapsible adjustment groups.

Groups whose feature is not built yet are shown disabled (greyed out) with a
tooltip naming the phase that enables them.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.ui.collapsible import CollapsibleSection
from app.ui.histogram_widget import HistogramWidget


@dataclass(frozen=True)
class SliderSpec:
    key: str      # parameter name in EditParams (Phase 4+)
    label: str
    minimum: int
    maximum: int


@dataclass(frozen=True)
class SliderGroup:
    key: str
    title: str
    available_in: str  # shown as tooltip while disabled
    sliders: tuple[SliderSpec, ...]


SLIDER_GROUPS: tuple[SliderGroup, ...] = (
    SliderGroup("skin", "Skin", "Phase 4", (
        SliderSpec("skin_smooth", "Smooth", 0, 100),
    )),
    SliderGroup("eyes", "Eyes", "Phase 5", (
        SliderSpec("eye_brightness", "Brightness", 0, 100),
        SliderSpec("eye_sharpness", "Sharpness", 0, 100),
    )),
    SliderGroup("teeth", "Teeth", "Phase 5", (
        SliderSpec("teeth_whitening", "Whitening", 0, 100),
    )),
    SliderGroup("reshape", "Face Reshape", "Phase 6", (
        SliderSpec("face_width", "Face Width", -50, 50),
        SliderSpec("jaw", "Jaw", -50, 50),
        SliderSpec("chin", "Chin", -50, 50),
        SliderSpec("eye_size", "Eye Size", -30, 30),
    )),
)

BACKGROUND_MODES = ("Transparent", "White", "Custom Color", "Custom Image")
UPSCALE_FACTORS = ("1x", "2x", "4x")


class SliderRow(QWidget):
    """Label + numeric box on one line, slider below; both stay in sync.

    Double-click the row to reset it to its default.
    """

    value_changed = Signal(str, int)

    def __init__(self, spec: SliderSpec) -> None:
        super().__init__()
        self.spec = spec
        self.default = 0 if spec.minimum <= 0 <= spec.maximum else spec.minimum

        self.name_label = QLabel(spec.label)

        self.spin = QSpinBox()
        self.spin.setRange(spec.minimum, spec.maximum)
        # Arrow buttons are hidden by the theme (zero width). Do not use
        # NoButtons: with a styled border, Qt 6 then collapses the text field.
        self.spin.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.spin.setFixedWidth(44)
        self.spin.setKeyboardTracking(False)  # commit on Enter / focus-out

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(spec.minimum, spec.maximum)

        for widget in (self.spin, self.slider):
            widget.setValue(self.default)
        self.slider.valueChanged.connect(self._on_value)
        self.spin.valueChanged.connect(self.slider.setValue)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(self.name_label)
        header.addStretch(1)
        header.addWidget(self.spin)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 3, 0, 3)
        layout.setSpacing(1)
        layout.addLayout(header)
        layout.addWidget(self.slider)

    def value(self) -> int:
        return self.slider.value()

    def set_value(self, value: int) -> None:
        self.slider.setValue(value)

    def reset(self) -> None:
        self.set_value(self.default)

    def _on_value(self, value: int) -> None:
        if self.spin.value() != value:
            self.spin.setValue(value)
        self.value_changed.emit(self.spec.key, value)

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        if self.isEnabled():
            self.reset()
        super().mouseDoubleClickEvent(event)


class AdjustPanel(QFrame):
    value_changed = Signal(str, int)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("SidePanel")
        self.setMinimumWidth(260)

        title = QLabel("Adjustments")
        title.setObjectName("PanelTitle")

        self.histogram = HistogramWidget()

        content = QWidget()
        body = QVBoxLayout(content)
        body.setContentsMargins(10, 4, 10, 12)
        body.setSpacing(4)

        self.sections: dict[str, CollapsibleSection] = {}
        self.rows: dict[str, SliderRow] = {}
        for group in SLIDER_GROUPS:
            section = CollapsibleSection(group.title)
            for spec in group.sliders:
                row = SliderRow(spec)
                row.value_changed.connect(self.value_changed)
                self.rows[spec.key] = row
                section.add_widget(row)
            section.reset_requested.connect(
                lambda keys=[s.key for s in group.sliders]: self._reset_rows(keys)
            )
            self._add_section(body, group.key, section, group.available_in)

        self._add_section(body, "background", self._build_background(), "Phase 7")
        self._add_section(body, "upscale", self._build_upscale(), "Phase 9")
        body.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(content)

        histogram_box = QVBoxLayout()
        histogram_box.setContentsMargins(10, 0, 10, 6)
        histogram_box.addWidget(self.histogram)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(title)
        layout.addLayout(histogram_box)
        layout.addWidget(scroll, 1)

    # ----------------------------------------------------------------------
    def _add_section(
        self, body: QVBoxLayout, key: str, section: CollapsibleSection, available_in: str
    ) -> None:
        # Not built yet -> greyed out; the implementing phase enables it.
        section.content.setEnabled(False)
        section.reset_button.setEnabled(False)
        section.content.setToolTip(f"Có từ {available_in}")
        section.toggle.setToolTip(f"Có từ {available_in}")
        self.sections[key] = section
        body.addWidget(section)
        separator = QFrame()
        separator.setObjectName("Separator")
        separator.setFixedHeight(1)
        body.addWidget(separator)

    def _reset_rows(self, keys: list[str]) -> None:
        for key in keys:
            self.rows[key].reset()

    def _build_background(self) -> CollapsibleSection:
        section = CollapsibleSection("Background", expanded=False)
        self.remove_bg_button = QPushButton("Remove Background")
        section.add_widget(self.remove_bg_button)
        self.background_modes = QButtonGroup(section)
        for i, name in enumerate(BACKGROUND_MODES):
            radio = QRadioButton(name)
            radio.setChecked(i == 0)
            self.background_modes.addButton(radio, i)
            section.add_widget(radio)
        return section

    def _build_upscale(self) -> CollapsibleSection:
        section = CollapsibleSection("Upscale", expanded=False)
        grid = QWidget()
        layout = QGridLayout(grid)
        layout.setContentsMargins(0, 2, 0, 2)
        self.upscale_factor = QComboBox()
        self.upscale_factor.addItems(UPSCALE_FACTORS)
        self.face_enhance = QCheckBox("Face Enhancement")
        layout.addWidget(QLabel("Scale"), 0, 0)
        layout.addWidget(self.upscale_factor, 0, 1)
        layout.addWidget(self.face_enhance, 1, 0, 1, 2)
        section.add_widget(grid)
        return section
