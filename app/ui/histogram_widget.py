"""Histogram display (RGB overlaid + luminance outline)."""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from app.image.histogram import Histogram
from app.ui import theme

CHANNEL_COLOURS = {
    "red": QColor(230, 70, 70, 150),
    "green": QColor(70, 200, 90, 150),
    "blue": QColor(70, 120, 240, 150),
}


class HistogramWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._histogram: Histogram | None = None
        self.setMinimumHeight(96)
        self.setMaximumHeight(120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setToolTip("Histogram (RGB + độ sáng)")

    def set_histogram(self, histogram: Histogram | None) -> None:
        self._histogram = histogram
        self.update()

    def histogram(self) -> Histogram | None:
        return self._histogram

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        area = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        painter.fillRect(area, QColor(theme.CANVAS))
        painter.setPen(QPen(QColor(theme.BORDER), 1))
        painter.drawRect(area)

        if self._histogram is None:
            painter.setPen(QColor(theme.TEXT_DIM))
            painter.drawText(area, Qt.AlignmentFlag.AlignCenter, "No image")
            return

        plot = area.adjusted(2, 4, -2, -2)
        channels = self._histogram.channels()
        # Scale by the largest bin excluding pure black/white, so a clipped
        # background does not flatten the rest of the curve.
        peak = max(int(c[1:255].max()) for c in channels.values()) or 1

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Plus)
        for name, colour in CHANNEL_COLOURS.items():
            painter.setBrush(colour)
            painter.drawPath(_curve(channels[name], peak, plot, closed=True))
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(220, 220, 220, 200), 1))
        painter.drawPath(_curve(channels["luma"], peak, plot, closed=False))


def _curve(counts: np.ndarray, peak: int, rect: QRectF, closed: bool) -> QPainterPath:
    heights = np.minimum(counts / peak, 1.0)
    dx = rect.width() / 255.0
    path = QPainterPath()
    if closed:
        path.moveTo(QPointF(rect.left(), rect.bottom()))
    for i, h in enumerate(heights):
        point = QPointF(rect.left() + i * dx, rect.bottom() - float(h) * rect.height())
        if i == 0 and not closed:
            path.moveTo(point)
        else:
            path.lineTo(point)
    if closed:
        path.lineTo(QPointF(rect.right(), rect.bottom()))
        path.closeSubpath()
    return path
