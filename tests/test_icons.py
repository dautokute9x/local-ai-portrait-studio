import pytest
from PySide6.QtCore import QSize
from PySide6.QtGui import QColor, QIcon

from app.ui import icon_loader, theme
from app.ui.canvas_toolbar import TOOLS

USED_ICONS = sorted({t.icon for t in TOOLS} | {"square-split-horizontal", "rotate-ccw"})


def _first_opaque_colour(pixmap) -> QColor:
    image = pixmap.toImage()
    for y in range(image.height()):
        for x in range(image.width()):
            colour = image.pixelColor(x, y)
            if colour.alpha() > 200:
                return colour
    raise AssertionError("icon rendered fully transparent")


@pytest.mark.parametrize("name", USED_ICONS)
def test_bundled_icon_exists_and_renders(qapp, name):
    assert icon_loader.icon_path(name).is_file()
    ic = icon_loader.icon(name)
    assert not ic.isNull()
    _first_opaque_colour(ic.pixmap(QSize(20, 20)))


def test_icon_is_tinted_per_state(qapp):
    ic = icon_loader.icon("hand")
    size = QSize(20, 20)
    normal = _first_opaque_colour(ic.pixmap(size, QIcon.Mode.Normal, QIcon.State.Off))
    disabled = _first_opaque_colour(ic.pixmap(size, QIcon.Mode.Disabled, QIcon.State.Off))
    checked = _first_opaque_colour(ic.pixmap(size, QIcon.Mode.Normal, QIcon.State.On))
    assert normal.name() == theme.TEXT
    assert disabled.name() == theme.TEXT_DIM
    assert checked.name() == "#ffffff"


def test_missing_icon_returns_empty_icon(qapp):
    assert icon_loader.icon("does-not-exist").isNull()


def test_lucide_license_is_bundled():
    text = (icon_loader.ICONS_DIR / "LICENSE-lucide.txt").read_text(encoding="utf-8")
    assert "ISC License" in text


def test_toolbar_buttons_are_icon_only(window):
    from PySide6.QtCore import Qt

    toolbar = window.canvas_toolbar
    buttons = list(toolbar.tool_buttons.values()) + [toolbar.before_after]
    for button in buttons:
        assert not button.icon().isNull()
        assert button.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly
        assert button.text()  # accessible label kept
        assert button.toolTip().startswith(button.text())
