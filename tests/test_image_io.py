import numpy as np
import pytest
from PIL import Image

from app.image import io as image_io
from app.image.io import ImageLoadError, load_image


def _save(path, size=(40, 20), colour=(200, 100, 50), mode="RGB", **kwargs):
    Image.new(mode, size, colour).save(path, **kwargs)
    return path


def _exif_with_orientation(value: int) -> bytes:
    exif = Image.Exif()
    exif[0x0112] = value
    return exif.tobytes()


def test_loads_jpeg_as_rgb_uint8(tmp_path):
    path = _save(tmp_path / "a.jpg", quality=95)
    img = load_image(path)
    assert img.rgb.dtype == np.uint8 and img.rgb.shape == (20, 40, 3)
    assert img.format == "JPEG"
    assert img.original_size == (40, 20) and not img.is_downscaled
    assert img.file_size == path.stat().st_size
    assert np.abs(img.rgb[10, 20].astype(int) - (200, 100, 50)).max() <= 3


@pytest.mark.parametrize("orientation", [6, 8])
def test_exif_rotation_is_applied(tmp_path, orientation):
    # 40x20 stored landscape, EXIF says rotate 90 degrees -> upright 20x40.
    path = _save(tmp_path / "rot.jpg", exif=_exif_with_orientation(orientation))
    img = load_image(path)
    assert img.size == (20, 40)
    assert img.original_size == (20, 40)
    assert img.exif is not None


def test_exif_rotation_with_downscale_reports_upright_original_size(tmp_path):
    path = _save(tmp_path / "rot.jpg", size=(4000, 2000), exif=_exif_with_orientation(6))
    img = load_image(path, max_dim=1000)
    assert img.original_size == (2000, 4000)
    assert max(img.size) == 1000 and img.size[0] < img.size[1]


def test_max_dim_downscales_and_keeps_aspect(tmp_path):
    path = _save(tmp_path / "big.jpg", size=(4000, 3000))
    img = load_image(path, max_dim=1600)
    assert img.size == (1600, 1200)
    assert img.original_size == (4000, 3000)
    assert img.is_downscaled


def test_max_dim_never_upscales(tmp_path):
    path = _save(tmp_path / "small.png", size=(300, 200))
    assert load_image(path, max_dim=1600).size == (300, 200)


def test_png_alpha_is_flattened_on_white(tmp_path):
    path = _save(tmp_path / "t.png", mode="RGBA", colour=(255, 0, 0, 0))
    img = load_image(path)
    assert img.had_alpha
    assert tuple(img.rgb[0, 0]) == (255, 255, 255)


def test_greyscale_and_16bit_png(tmp_path):
    grey = _save(tmp_path / "g.png", mode="L", colour=128)
    assert tuple(load_image(grey).rgb[0, 0]) == (128, 128, 128)

    arr = np.full((10, 10), 65535, dtype=np.uint16)
    Image.fromarray(arr).save(tmp_path / "g16.png")
    assert tuple(load_image(tmp_path / "g16.png").rgb[0, 0]) == (255, 255, 255)


def test_unicode_path(tmp_path):
    folder = tmp_path / "Ảnh cưới"
    folder.mkdir()
    path = _save(folder / "chân_dung_01.jpg")
    assert load_image(path).size == (40, 20)


def test_icc_profile_is_kept(tmp_path):
    from PIL import ImageCms

    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    path = _save(tmp_path / "icc.jpg", icc_profile=icc)
    assert load_image(path).icc_profile == icc


# ------------------------------------------------------------------ errors
def test_missing_file(tmp_path):
    with pytest.raises(ImageLoadError, match="Không tìm thấy"):
        load_image(tmp_path / "nope.jpg")


def test_unsupported_extension(tmp_path):
    path = _save(tmp_path / "a.gif", mode="P", colour=1)
    with pytest.raises(ImageLoadError, match="chưa hỗ trợ"):
        load_image(path)


def test_wrong_content_behind_supported_extension(tmp_path):
    path = tmp_path / "fake.jpg"
    Image.new("RGB", (10, 10)).save(path, format="BMP")
    with pytest.raises(ImageLoadError, match="BMP"):
        load_image(path)


@pytest.mark.parametrize("content", [b"", b"not an image at all", bytes(range(256)) * 10])
def test_garbage_file(tmp_path, content):
    path = tmp_path / "bad.jpg"
    path.write_bytes(content)
    with pytest.raises(ImageLoadError, match="Không đọc được"):
        load_image(path)


def test_truncated_jpeg(tmp_path):
    full = _save(tmp_path / "full.jpg", size=(400, 300))
    rng = np.random.default_rng(0)
    Image.fromarray(rng.integers(0, 256, (300, 400, 3), dtype=np.uint8)).save(full, quality=95)
    data = full.read_bytes()
    cut = tmp_path / "cut.jpg"
    cut.write_bytes(data[: len(data) // 2])
    with pytest.raises(ImageLoadError, match="Không đọc được"):
        load_image(cut)


def test_decompression_bomb_gives_friendly_error(tmp_path, monkeypatch):
    path = _save(tmp_path / "huge.png", size=(100, 100))
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 1000)
    with pytest.raises(ImageLoadError, match="quá lớn"):
        load_image(path)


def test_is_supported_path_is_case_insensitive():
    from pathlib import Path

    assert image_io.is_supported_path(Path("A.JPG"))
    assert image_io.is_supported_path(Path("b.Png"))
    assert not image_io.is_supported_path(Path("c.heic"))
