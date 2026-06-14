"""Tests for favicon_generator.converter."""

import json
import tarfile
from pathlib import Path

from PIL import Image

from favicon_generator.converter import (
    _load_image,
    convert_to_ico,
    generate_app_icons_bundle,
)

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


def test_generate_app_icons_bundle_adds_maskable_icons_and_manifest_fields(
    tmp_path: Path,
) -> None:
    """Bundle output should include maskable icons and matching manifest entries."""
    input_path = tmp_path / "source.png"
    output_path = tmp_path / "app-icons.tar.gz"

    Image.new("RGBA", (1024, 1024), (200, 10, 10, 255)).save(input_path, format="PNG")

    generate_app_icons_bundle(input_path, output_path)

    with tarfile.open(output_path, "r:gz") as tar:
        names = {member.name for member in tar.getmembers()}
        assert "app-icons/maskable-icon-192x192.png" in names  # noqa: S101  # nosec B101
        assert "app-icons/maskable-icon-512x512.png" in names  # noqa: S101  # nosec B101

        manifest_member = tar.extractfile("app-icons/site.webmanifest")
        assert manifest_member is not None  # noqa: S101  # nosec B101
        manifest = json.loads(manifest_member.read().decode("utf-8"))

    purposes = {
        (entry["src"], entry.get("purpose", "")) for entry in manifest.get("icons", [])
    }
    assert ("/android-chrome-192x192.png", "any") in purposes  # noqa: S101  # nosec B101
    assert ("/android-chrome-512x512.png", "any") in purposes  # noqa: S101  # nosec B101
    assert ("/maskable-icon-192x192.png", "maskable") in purposes  # noqa: S101  # nosec B101
    assert ("/maskable-icon-512x512.png", "maskable") in purposes  # noqa: S101  # nosec B101


def test_generate_app_icons_bundle_includes_favicon_svg_for_svg_input(
    tmp_path: Path,
) -> None:
    """SVG sources should preserve a favicon.svg in the output bundle."""
    input_path = tmp_path / "logo.svg"
    output_path = tmp_path / "icons.tar.gz"
    input_path.write_text(
        (
            '<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512">'
            '<rect width="512" height="512" fill="#00aaee" />'
            "</svg>"
        ),
        encoding="utf-8",
    )

    generate_app_icons_bundle(input_path, output_path)

    with tarfile.open(output_path, "r:gz") as tar:
        names = {member.name for member in tar.getmembers()}
        assert "app-icons/favicon.svg" in names  # noqa: S101  # nosec B101


def test_convert_to_ico_pads_non_square_jpeg_with_white(tmp_path: Path) -> None:
    """JPEG input without --crop should be padded to square with white background."""
    input_path = tmp_path / "wide.jpg"
    output_path = tmp_path / "wide.ico"

    Image.new("RGB", (240, 120), (255, 0, 0)).save(input_path, format="JPEG")

    convert_to_ico(input_path, output_path, crop_square=False)

    ico = Image.open(output_path).convert("RGB")
    width, height = ico.size
    assert width == height  # noqa: S101  # nosec B101

    corner = ico.getpixel((2, 2))
    center = ico.getpixel((width // 2, height // 2))

    assert corner[0] > 230 and corner[1] > 230 and corner[2] > 230  # noqa: S101  # nosec B101
    assert center[0] > 200 and center[1] < 80 and center[2] < 80  # noqa: S101  # nosec B101


def test_convert_to_ico_pads_non_square_png_with_transparency(tmp_path: Path) -> None:
    """PNG input without --crop should be padded to square with transparent background."""
    input_path = tmp_path / "wide.png"
    output_path = tmp_path / "wide.ico"

    Image.new("RGBA", (240, 120), (0, 200, 0, 255)).save(input_path, format="PNG")

    convert_to_ico(input_path, output_path, crop_square=False)

    ico = Image.open(output_path).convert("RGBA")
    width, height = ico.size
    assert width == height  # noqa: S101  # nosec B101

    corner = ico.getpixel((2, 2))
    center = ico.getpixel((width // 2, height // 2))

    assert corner[3] == 0  # noqa: S101  # nosec B101
    assert center[1] > 150 and center[3] > 200  # noqa: S101  # nosec B101


def test_generate_app_icons_bundle_pads_non_square_jpeg_with_white(
    tmp_path: Path,
) -> None:
    """Bundle PNG assets should be generated from white-padded JPEG input by default."""
    input_path = tmp_path / "wide.jpg"
    output_path = tmp_path / "icons.tar.gz"
    Image.new("RGB", (300, 150), (255, 0, 0)).save(input_path, format="JPEG")

    generate_app_icons_bundle(input_path, output_path, crop_square=False)

    with tarfile.open(output_path, "r:gz") as tar:
        member = tar.extractfile("app-icons/favicon-32x32.png")
        assert member is not None  # noqa: S101  # nosec B101
        icon = Image.open(member).convert("RGB")

    corner = icon.getpixel((1, 1))
    center = icon.getpixel((16, 16))

    assert corner[0] > 230 and corner[1] > 230 and corner[2] > 230  # noqa: S101  # nosec B101
    assert center[0] > 200 and center[1] < 80 and center[2] < 80  # noqa: S101  # nosec B101
