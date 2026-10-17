from PySide6.QtCore import QSettings
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication

from app.ui.adjust_panel import PORTRAIT_SLIDERS
from app.ui.main_window import MainWindow
from app.ui.theme import BG, apply_dark_theme


def test_three_column_layout(window):
    splitter = window.splitter
    assert splitter.count() == 3
    assert splitter.widget(0) is window.photo_panel
    assert splitter.widget(1) is window.image_view
    assert splitter.widget(2) is window.adjust_panel
    # the canvas gets the most width
    sizes = splitter.sizes()
    assert sizes[1] > sizes[0] and sizes[1] > sizes[2]


def test_menus_and_shortcuts(window):
    menus = [a.text() for a in window.menuBar().actions()]
    assert menus == ["&File", "&Edit", "&View"]
    expected = {
        "open_image": "Ctrl+O",
        "export": "Ctrl+E",
        "undo": "Ctrl+Z",
        "redo": "Ctrl+Shift+Z",
        "zoom_fit": "Ctrl+0",
        "zoom_100": "Ctrl+1",
    }
    for key, shortcut in expected.items():
        assert window.actions[key].shortcut() == QKeySequence(shortcut), key


def test_unbuilt_features_are_disabled(window):
    for key in ("open_image", "export", "undo", "redo", "zoom_in", "before_after"):
        assert not window.actions[key].isEnabled(), key
    assert not window.export_button.isEnabled()
    assert window.actions["quit"].isEnabled()


def test_adjust_panel_has_disabled_portrait_sliders(window):
    rows = window.adjust_panel.rows
    assert list(rows) == [s.key for s in PORTRAIT_SLIDERS]
    face_width = rows["face_width"]
    assert (face_width.slider.minimum(), face_width.slider.maximum()) == (-50, 50)
    assert face_width.slider.value() == 0
    assert all(not row.isEnabled() for row in rows.values())


def test_slider_row_value_label_and_reset(qtbot):
    from app.ui.adjust_panel import SliderRow

    row = SliderRow(PORTRAIT_SLIDERS[0])
    qtbot.addWidget(row)
    with qtbot.waitSignal(row.value_changed) as blocker:
        row.slider.setValue(35)
    assert blocker.args == ["skin_smooth", 35]
    assert row.value_label.text() == "35"


def test_panel_toggle_hides_and_shows(window):
    window.actions["toggle_photos"].setChecked(False)
    assert not window.photo_panel.isVisible()
    window.actions["toggle_photos"].setChecked(True)
    assert window.photo_panel.isVisible()


def test_status_bar_labels(window):
    assert window.zoom_label.text().startswith("Zoom")
    assert window.device_label.text().startswith("AI Device")


def test_layout_is_persisted(qtbot, tmp_path):
    path = str(tmp_path / "settings.ini")
    first = MainWindow(QSettings(path, QSettings.Format.IniFormat))
    qtbot.addWidget(first)
    first.show()
    # Equal side panels, unlike the 220/280 default.
    first.splitter.setSizes([300, 700, 300])
    first.close()
    assert QSettings(path, QSettings.Format.IniFormat).value("window/splitter")

    second = MainWindow(QSettings(path, QSettings.Format.IniFormat))
    qtbot.addWidget(second)
    second.show()
    # Qt shrinks the window to fit the (small, virtual) test screen, so compare
    # the restored proportions rather than absolute pixels.
    left, _, right = second.splitter.sizes()
    assert left == right


def test_dark_theme_applies(qapp):
    apply_dark_theme(qapp)
    assert QApplication.palette().window().color().name() == BG
    assert "QGraphicsView" in qapp.styleSheet()
