"""Centre canvas: shows the photo. Zoom/pan arrive in Step 1.5."""

from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

from app.ui import theme


class ImageView(QGraphicsView):
    def __init__(self) -> None:
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(400, 300)

    def has_image(self) -> bool:
        return bool(self.scene().items())

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:  # noqa: N802
        """Empty-state hint, drawn in viewport coordinates."""
        if self.has_image():
            return
        painter.save()
        painter.resetTransform()
        painter.setPen(QColor(theme.TEXT_DIM))
        font = QFont(painter.font())
        font.setPointSizeF(font.pointSizeF() * 1.2)
        painter.setFont(font)
        painter.drawText(
            self.viewport().rect(),
            Qt.AlignmentFlag.AlignCenter,
            "Mở ảnh để bắt đầu\nFile → Open Image (Ctrl+O)",
        )
        painter.restore()
