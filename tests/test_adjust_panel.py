import numpy as np
from PySide6.QtCore import Qt

from app.image.histogram import compute_histogram
from app.ui.adjust_panel import SLIDER_GROUPS, AdjustPanel, SliderRow
from app.ui.collapsible import CollapsibleSection


def _panel(qtbot) -> AdjustPanel:
    panel = AdjustPanel()
    qtbot.addWidget(panel)
    panel.show()
    return panel


def test_groups_and_ranges_match_spec(qtbot):
    panel = _panel(qtbot)
    assert list(panel.sections) == ["skin", "eyes", "teeth", "reshape", "background", "upscale"]
    expected = {
        "skin_smooth": (0, 100),
        "eye_brightness": (0, 100),
        "eye_sharpness": (0, 100),
        "teeth_whitening": (0, 100),
        "face_width": (-50, 50),
        "jaw": (-50, 50),
        "chin": (-50, 50),
        "eye_size": (-30, 30),
    }
    ranges = {k: (r.slider.minimum(), r.slider.maximum()) for k, r in panel.rows.items()}
    assert ranges == expected
    assert all(r.value() == 0 for r in panel.rows.values())


def test_unbuilt_sections_are_greyed_out_but_visible(qtbot):
    panel = _panel(qtbot)
    for key, section in panel.sections.items():
        assert section.isVisible(), key
        assert not section.content.isEnabled(), key
        assert "Phase" in section.toggle.toolTip()


def test_slider_and_spinbox_stay_in_sync(qtbot):
    row = SliderRow(SLIDER_GROUPS[3].sliders[0])  # face_width -50..50
    qtbot.addWidget(row)
    with qtbot.waitSignal(row.value_changed) as blocker:
        row.slider.setValue(-12)
    assert blocker.args == ["face_width", -12]
    assert row.spin.value() == -12

    row.spin.setValue(30)
    assert row.slider.value() == 30

    row.spin.setValue(999)  # clamped by the range
    assert row.value() == 50


def test_double_click_resets_row(qtbot):
    row = SliderRow(SLIDER_GROUPS[0].sliders[0])
    qtbot.addWidget(row)
    row.set_value(40)
    qtbot.mouseDClick(row, Qt.MouseButton.LeftButton)
    assert row.value() == 0


def test_section_reset_resets_only_its_rows(qtbot):
    panel = _panel(qtbot)
    panel.rows["face_width"].set_value(20)
    panel.rows["jaw"].set_value(-10)
    panel.rows["skin_smooth"].set_value(35)
    panel.sections["reshape"].reset_requested.emit()
    assert panel.rows["face_width"].value() == 0
    assert panel.rows["jaw"].value() == 0
    assert panel.rows["skin_smooth"].value() == 35


def test_panel_forwards_value_changes(qtbot):
    panel = _panel(qtbot)
    with qtbot.waitSignal(panel.value_changed) as blocker:
        panel.rows["teeth_whitening"].set_value(15)
    assert blocker.args == ["teeth_whitening", 15]


def test_collapsible_section_toggles_content(qtbot):
    section = CollapsibleSection("Test")
    qtbot.addWidget(section)
    section.show()
    assert section.is_expanded() and section.content.isVisible()
    section.toggle.click()
    assert not section.is_expanded() and not section.content.isVisible()
    assert section.toggle.arrowType() == Qt.ArrowType.RightArrow
    section.toggle.click()
    assert section.content.isVisible()


def test_histogram_widget_paints_with_and_without_data(qtbot):
    panel = _panel(qtbot)
    assert panel.histogram.histogram() is None
    panel.histogram.grab()  # empty state must paint without error
    rng = np.random.default_rng(0)
    img = rng.integers(0, 256, (64, 64, 3), dtype=np.uint8)
    panel.histogram.set_histogram(compute_histogram(img))
    assert not panel.histogram.grab().isNull()


def test_spinbox_text_field_is_not_collapsed_by_theme(qtbot, qapp):
    """Regression: a styled QSpinBox with NoButtons shrinks its editor to 1 px."""
    from app.ui.theme import apply_dark_theme

    apply_dark_theme(qapp)
    panel = _panel(qtbot)
    spin = panel.rows["skin_smooth"].spin
    assert spin.lineEdit().width() >= spin.width() - 8
    assert spin.text() == "0"
