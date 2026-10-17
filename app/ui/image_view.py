"""Centre canvas: shows the photo, fitted to the window.

Zoom presets and panning arrive in Step 1.5; for now the image is always
fitted and re-fitted when the window is resized.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPixmap
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView

from app.ui import theme


class ImageView(QGraphicsView):
    zoom_changed = Signal(float)  # displayed pixels per image pixel

    def __init__(self) -> None:
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMinimumSize(400, 300)
        self._item: QGraphicsPixmapItem | None = None

    # ---------------------------------------------------------------- image
    def has_image(self) -> bool:
        return self._item is not None

    def set_image(self, image: QImage | None) -> None:
        scene = self.scene()
        scene.clear()
        self._item = None
        if image is None or image.isNull():
            scene.setSceneRect(QRectF())
            self.viewport().update()
            return
        self._item = scene.addPixmap(QPixmap.fromImage(image))
        self._item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        scene.setSceneRect(self._item.boundingRect())
        self.fit_to_window()

    def fit_to_window(self) -> None:
        if self._item is not None:
            self.fitInView(self._item, Qt.AspectRatioMode.KeepAspectRatio)
            self.zoom_changed.emit(self.zoom_factor())

    def zoom_factor(self) -> float:
        """Displayed pixels per image pixel."""
        return self.transform().m11()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self.fit_to_window()

    # ---------------------------------------------------------- empty state
    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:  # noqa: N802
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
