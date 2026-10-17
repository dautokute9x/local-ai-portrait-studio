"""Loading photos from disk into numpy arrays (no Qt).

- JPEG and PNG only, detected from the file *content* (not the extension).
- EXIF orientation is applied, so arrays are always upright.
- `max_dim` loads a downscaled copy (e.g. the ~1600 px preview); for JPEG
  this uses Pillow's draft mode, decoding at reduced size, which is several
  times faster and lighter than decoding full resolution and resizing.
- Original EXIF and ICC bytes are kept for export (Step 1.6).
- Every failure is raised as ImageLoadError with a message for the user.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

log = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png")
SUPPORTED_FORMATS = {"JPEG", "PNG"}
# Pillow refuses images above 2x this as a "decompression bomb". 200 MP covers
# every current camera (e.g. 100 MP medium format) with headroom.
MAX_PIXELS = 200_000_000
# Background used when flattening PNG transparency for display.
FLATTEN_BACKGROUND = (255, 255, 255)

Image.MAX_IMAGE_PIXELS = MAX_PIXELS


class ImageLoadError(Exception):
    """Raised with a user-facing (Vietnamese) message."""


@dataclass(frozen=True)
class LoadedImage:
    path: Path
    rgb: np.ndarray                 # HxWx3 uint8, upright (EXIF applied)
    original_size: tuple[int, int]  # (width, height) at full resolution, upright
    format: str                     # "JPEG" | "PNG"
    file_size: int                  # bytes
    exif: bytes | None              # raw EXIF block, for export
    icc_profile: bytes | None
    had_alpha: bool                 # PNG transparency was flattened onto white

    @property
    def size(self) -> tuple[int, int]:
        """(width, height) of `rgb`."""
        return self.rgb.shape[1], self.rgb.shape[0]

    @property
    def is_downscaled(self) -> bool:
        return self.size != self.original_size


def is_supported_path(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def load_image(path: Path | str, max_dim: int | None = None) -> LoadedImage:
    """Load `path` as an upright RGB uint8 array, optionally downscaled so the
    longest side is at most `max_dim`."""
    path = Path(path)
    started = time.perf_counter()

    if not path.is_file():
        raise ImageLoadError(f"Không tìm thấy file:\n{path}")
    if not is_supported_path(path):
        raise ImageLoadError(
            f"Định dạng chưa hỗ trợ: {path.suffix or '(không có đuôi)'}\n"
            "Hiện chỉ mở được JPG, JPEG và PNG."
        )

    try:
        with Image.open(path) as img:
            if img.format not in SUPPORTED_FORMATS:
                raise ImageLoadError(
                    f"File “{path.name}” thực chất là {img.format}, không phải JPG/PNG."
                )
            fmt = img.format
            exif = img.info.get("exif")
            icc = img.info.get("icc_profile")
            orientation = img.getexif().get(0x0112, 1)
            stored_w, stored_h = img.size
            # Orientations 5-8 swap width and height.
            original_size = (stored_h, stored_w) if orientation in (5, 6, 7, 8) else (stored_w, stored_h)

            if max_dim is not None and fmt == "JPEG":
                # Decode at the smallest power-of-two reduction still >= max_dim.
                img.draft("RGB", (max_dim, max_dim))
            img.load()  # force decoding now so corrupt data fails here
            img = ImageOps.exif_transpose(img)
            rgb, had_alpha = _to_rgb_array(img)
    except ImageLoadError:
        raise
    except Image.DecompressionBombError as exc:
        raise ImageLoadError(
            f"Ảnh “{path.name}” quá lớn (vượt {MAX_PIXELS // 1_000_000} megapixel)."
        ) from exc
    except PermissionError as exc:
        raise ImageLoadError(f"Không có quyền đọc file:\n{path}") from exc
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError) as exc:
        log.warning("Failed to decode %s: %s", path, exc)
        raise ImageLoadError(
            f"Không đọc được ảnh “{path.name}”.\nFile có thể bị hỏng hoặc chưa tải về đầy đủ."
        ) from exc

    if max_dim is not None:
        rgb = _fit_within(rgb, max_dim)

    log.info(
        "image_load: %s %dx%d -> %dx%d in %.0f ms",
        path.name,
        *original_size,
        rgb.shape[1],
        rgb.shape[0],
        (time.perf_counter() - started) * 1000,
    )
    return LoadedImage(
        path=path,
        rgb=rgb,
        original_size=original_size,
        format=fmt,
        file_size=path.stat().st_size,
        exif=exif,
        icc_profile=icc,
        had_alpha=had_alpha,
    )


def _to_rgb_array(img: Image.Image) -> tuple[np.ndarray, bool]:
    """Any Pillow mode -> HxWx3 uint8. Transparency is flattened onto white."""
    if img.mode in ("I;16", "I;16B", "I;16L", "I"):
        # 16-bit greyscale PNG: Pillow's convert("RGB") would clip, scale instead.
        grey = (np.asarray(img, dtype=np.uint32) >> 8).clip(0, 255).astype(np.uint8)
        return np.ascontiguousarray(np.stack([grey] * 3, axis=-1)), False

    has_alpha = img.mode in ("RGBA", "LA", "PA") or (
        img.mode == "P" and "transparency" in img.info
    )
    if has_alpha:
        rgba = img.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (*FLATTEN_BACKGROUND, 255))
        img = Image.alpha_composite(background, rgba)
    rgb = img.convert("RGB")
    return np.ascontiguousarray(np.asarray(rgb, dtype=np.uint8)), has_alpha


def _fit_within(rgb: np.ndarray, max_dim: int) -> np.ndarray:
    h, w = rgb.shape[:2]
    scale = max_dim / max(h, w)
    if scale >= 1:
        return rgb
    size = (max(1, round(w * scale)), max(1, round(h * scale)))
    resized = Image.fromarray(rgb).resize(size, Image.Resampling.LANCZOS, reducing_gap=2.0)
    return np.ascontiguousarray(np.asarray(resized, dtype=np.uint8))
