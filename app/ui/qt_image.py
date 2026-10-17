"""numpy <-> Qt image conversion."""

from __future__ import annotations

import numpy as np
from PySide6.QtGui import QImage


def rgb_to_qimage(rgb: np.ndarray) -> QImage:
    """HxWx3 uint8 -> QImage (deep copy, so the array may be freed afterwards)."""
    if rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError(f"expected HxWx3 uint8, got {rgb.dtype} {rgb.shape}")
    rgb = np.ascontiguousarray(rgb)
    h, w = rgb.shape[:2]
    image = QImage(rgb.data, w, h, rgb.strides[0], QImage.Format.Format_RGB888)
    return image.copy()
