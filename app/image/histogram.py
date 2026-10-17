"""RGB + luminance histogram of an 8-bit image."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Rec.709 / sRGB luma weights.
LUMA_WEIGHTS = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
# Larger images are subsampled with a uniform stride; the shape of the
# histogram is unchanged for display purposes and it stays fast (< ~10 ms).
MAX_SAMPLES = 1_000_000


@dataclass(frozen=True)
class Histogram:
    red: np.ndarray    # shape (256,), int64 counts
    green: np.ndarray
    blue: np.ndarray
    luma: np.ndarray

    def channels(self) -> dict[str, np.ndarray]:
        return {"red": self.red, "green": self.green, "blue": self.blue, "luma": self.luma}


def compute_histogram(image: np.ndarray) -> Histogram:
    """Histogram of an HxWx3 (RGB) or HxWx4 (RGBA, alpha ignored) uint8 array."""
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] not in (3, 4):
        raise ValueError(f"expected HxWx3/4 uint8 image, got {image.dtype} {image.shape}")

    rgb = image[..., :3]
    pixels = rgb.shape[0] * rgb.shape[1]
    if pixels > MAX_SAMPLES:
        step = int(np.ceil(np.sqrt(pixels / MAX_SAMPLES)))
        rgb = rgb[::step, ::step]

    flat = rgb.reshape(-1, 3)
    luma = np.clip(flat.astype(np.float32) @ LUMA_WEIGHTS + 0.5, 0, 255).astype(np.uint8)

    def count(values: np.ndarray) -> np.ndarray:
        return np.bincount(values, minlength=256).astype(np.int64)

    return Histogram(
        red=count(flat[:, 0]),
        green=count(flat[:, 1]),
        blue=count(flat[:, 2]),
        luma=count(luma),
    )
