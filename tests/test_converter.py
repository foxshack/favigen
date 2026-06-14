"""Tests for favicon_generator.converter."""

from pathlib import Path

from PIL import Image

from favicon_generator.converter import _load_image, convert_to_ico

# EXIF orientation tag for image rotation and mirroring metadata.
EXIF_ORIENTATION_TAG = 274


def test_load_image_applies_exif_orientation(tmp_path: Path) -> None:
    """Load JPEG images with EXIF orientation and normalize orientation."""
    input_path = tmp_path / "oriented.jpg"

    image = Image.new("RGB", (20, 20))
    for y in range(20):
        for x in range(20):
            if y < 10:
                image.putpixel((x, y), (255, 0, 0))
            else:
                image.putpixel((x, y), (0, 0, 255))

    exif = Image.Exif()
    exif[EXIF_ORIENTATION_TAG] = 3  # Rotate 180° for display.
    image.save(input_path, format="JPEG", quality=100, subsampling=0, exif=exif)

    loaded = _load_image(input_path)

    top_pixel = loaded.getpixel((10, 2))
    bottom_pixel = loaded.getpixel((10, 17))

    assert top_pixel[2] > top_pixel[0]  # noqa: S101  # nosec B101
    assert bottom_pixel[0] > bottom_pixel[2]  # noqa: S101  # nosec B101


def test_convert_to_ico_applies_exif_orientation(tmp_path: Path) -> None:
    """Convert JPEG to ICO and preserve display orientation from EXIF."""
    input_path = tmp_path / "oriented-source.jpg"
    output_path = tmp_path / "favicon.ico"

    image = Image.new("RGB", (256, 256))
    for y in range(256):
        for x in range(256):
            if y < 128:
                image.putpixel((x, y), (255, 0, 0))
            else:
                image.putpixel((x, y), (0, 0, 255))

    exif = Image.Exif()
    exif[EXIF_ORIENTATION_TAG] = 3  # Rotate 180° for display.
    image.save(input_path, format="JPEG", quality=100, subsampling=0, exif=exif)

    convert_to_ico(input_path, output_path)

    ico = Image.open(output_path).convert("RGB")
    width, height = ico.size
    top_pixel = ico.getpixel((width // 2, height // 8))
    bottom_pixel = ico.getpixel((width // 2, (height * 7) // 8))

    assert top_pixel[2] > top_pixel[0]  # noqa: S101  # nosec B101
    assert bottom_pixel[0] > bottom_pixel[2]  # noqa: S101  # nosec B101
