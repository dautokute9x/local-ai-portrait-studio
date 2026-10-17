from PySide6.QtCore import QSettings
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.ui.theme import BG, apply_dark_theme


def test_three_column_layout(window):
    splitter = window.splitter
    assert splitter.count() == 3
    assert splitter.widget(0) is window.photo_panel
    assert splitter.widget(1) is window.canvas_area
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
    assert window.actions["open_image"].isEnabled()
    for key in ("export", "undo", "redo", "zoom_in", "before_after"):
        assert not window.actions[key].isEnabled(), key
    assert not window.export_button.isEnabled()
    assert window.actions["quit"].isEnabled()


def test_canvas_column_has_toolbar_above_view(window):
    layout = window.canvas_area.layout()
    assert layout.itemAt(0).widget() is window.canvas_toolbar
    assert layout.itemAt(1).widget() is window.image_view


def test_canvas_toolbar_tools_are_exclusive_and_disabled(window):
    toolbar = window.canvas_toolbar
    assert list(toolbar.tool_buttons) == ["pan", "blemish", "remove"]
    assert toolbar.tool_group.exclusive()
    assert all(not b.isEnabled() for b in toolbar.tool_buttons.values())
    assert [toolbar.zoom.itemText(i) for i in range(toolbar.zoom.count())][:1] == ["Fit"]


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
    first.splitter.setSizes([300, 700, 300])
    saved = first.splitter.sizes()
    first.close()
    assert QSettings(path, QSettings.Format.IniFormat).value("window/splitter")

    second = MainWindow(QSettings(path, QSettings.Format.IniFormat))
    qtbot.addWidget(second)
    second.show()
    assert second.splitter.sizes() == saved


def test_dark_theme_applies(qapp):
    apply_dark_theme(qapp)
    assert QApplication.palette().window().color().name() == BG
    assert "QGraphicsView" in qapp.styleSheet()
