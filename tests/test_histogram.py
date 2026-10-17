import numpy as np
import pytest

from app.image import histogram as hist_mod
from app.image.histogram import compute_histogram


def test_solid_colour_lands_in_single_bins():
    img = np.zeros((10, 20, 3), np.uint8)
    img[...] = (255, 0, 128)
    h = compute_histogram(img)
    assert h.red[255] == 200 and h.red.sum() == 200
    assert h.green[0] == 200
    assert h.blue[128] == 200
    # luma = 0.2126*255 + 0.0722*128 = 63.47 -> 63
    assert h.luma[63] == 200


def test_grey_ramp_luma_matches_channels():
    ramp = np.tile(np.arange(256, dtype=np.uint8), (4, 1))
    img = np.stack([ramp] * 3, axis=-1)
    h = compute_histogram(img)
    for counts in h.channels().values():
        assert counts.shape == (256,)
        assert (counts == 4).all()


def test_rgba_alpha_is_ignored():
    img = np.full((5, 5, 4), 10, np.uint8)
    img[..., 3] = 255
    assert compute_histogram(img).red[10] == 25


def test_large_images_are_subsampled(monkeypatch):
    monkeypatch.setattr(hist_mod, "MAX_SAMPLES", 100)
    img = np.full((100, 100, 3), 7, np.uint8)
    h = compute_histogram(img)
    assert h.red.sum() <= 100
    assert h.red[7] == h.red.sum()


@pytest.mark.parametrize(
    "bad",
    [np.zeros((4, 4), np.uint8), np.zeros((4, 4, 3), np.float32), np.zeros((4, 4, 2), np.uint8)],
)
def test_rejects_invalid_input(bad):
    with pytest.raises(ValueError):
        compute_histogram(bad)
