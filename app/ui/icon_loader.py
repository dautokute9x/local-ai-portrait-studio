"""Tinted icons from the bundled Lucide SVGs (ISC, see icons/LICENSE-lucide.txt).

Lucide draws with stroke="currentColor", which Qt's SVG renderer does not
resolve, so each icon is rendered once per state with an explicit colour:
normal, disabled and checked ("On") — that is what makes icons follow the
dark theme and grey out together with their button.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from app.ui import theme

log = logging.getLogger(__name__)

ICONS_DIR = Path(__file__).resolve().parent / "icons"
# Rendered sizes; Qt picks the closest one (2x entries cover HiDPI screens).
SIZES = (16, 18, 20, 32, 36, 40)


def icon_path(name: str) -> Path:
    return ICONS_DIR / f"{name}.svg"


def _render(svg: str, colour: str, size: int) -> QPixmap:
    data = QByteArray(svg.replace("currentColor", colour).encode("utf-8"))
    renderer = QSvgRenderer(data)
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    return pixmap


@lru_cache(maxsize=None)
def icon(name: str) -> QIcon:
    """Themed QIcon for `name` (e.g. "hand"). Missing files give an empty icon."""
    path = icon_path(name)
    try:
        svg = path.read_text(encoding="utf-8")
    except OSError:
        log.warning("Icon not found: %s", path)
        return QIcon()

    result = QIcon()
    states = (
        (QIcon.Mode.Normal, QIcon.State.Off, theme.TEXT),
        (QIcon.Mode.Active, QIcon.State.Off, "#ffffff"),
        (QIcon.Mode.Disabled, QIcon.State.Off, theme.TEXT_DIM),
        (QIcon.Mode.Normal, QIcon.State.On, "#ffffff"),
        (QIcon.Mode.Active, QIcon.State.On, "#ffffff"),
        (QIcon.Mode.Disabled, QIcon.State.On, theme.TEXT_DIM),
    )
    for mode, state, colour in states:
        for size in SIZES:
            result.addPixmap(_render(svg, colour, size), mode, state)
    return result

