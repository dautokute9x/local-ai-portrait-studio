import numpy as np
from PIL import Image
from PySide6.QtWidgets import QMessageBox

from app.ui.qt_image import rgb_to_qimage


def _photo(path, size=(3000, 2000)):
    rng = np.random.default_rng(1)
    arr = rng.integers(0, 256, (size[1], size[0], 3), dtype=np.uint8)
    Image.fromarray(arr).save(path, quality=90)
    return path


def test_rgb_to_qimage_copies_pixels():
    arr = np.zeros((2, 3, 3), np.uint8)
    arr[1, 2] = (10, 20, 30)
    image = rgb_to_qimage(arr)
    arr[:] = 0  # the QImage must not share memory with the array
    assert (image.width(), image.height()) == (3, 2)
    colour = image.pixelColor(2, 1)
    assert (colour.red(), colour.green(), colour.blue()) == (10, 20, 30)


def test_open_image_shows_preview_and_status(window, tmp_path):
    path = _photo(tmp_path / "portrait.jpg")
    assert window.open_image_path(path)

    assert window.image_view.has_image()
    assert window.current.original_size == (3000, 2000)
    assert max(window.current.size) == 1600  # preview, not full resolution
    assert "portrait.jpg" in window.windowTitle()
    status = window.statusBar().currentMessage()
    assert "portrait.jpg" in status and "3000×2000" in status
    assert window.zoom_label.text().endswith("%")


def test_zoom_label_is_relative_to_original_pixels(window, tmp_path):
    window.open_image_path(_photo(tmp_path / "p.jpg"))
    view = window.image_view
    expected = view.zoom_factor() * window.current.size[0] / 3000 * 100
    assert window.zoom_label.text() == f"Zoom: {expected:.0f}%"


def test_open_error_shows_message_and_keeps_previous_image(window, tmp_path, monkeypatch):
    good = _photo(tmp_path / "good.jpg", size=(800, 600))
    window.open_image_path(good)

    bad = tmp_path / "bad.jpg"
    bad.write_bytes(b"garbage")
    shown = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: shown.append(a))

    assert not window.open_image_path(bad)
    assert shown and "bad.jpg" in shown[0][2]
    assert window.current.path == good  # previous image still displayed
    assert window.image_view.has_image()


def test_last_directory_is_remembered(window, tmp_path):
    folder = tmp_path / "shoot"
    folder.mkdir()
    window.open_image_path(_photo(folder / "a.jpg", size=(400, 300)))
    assert window._settings.value("paths/last_open_dir") == str(folder)
