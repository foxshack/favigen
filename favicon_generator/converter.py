"""Core image processing module for converting images to .ico format."""

import io
import json
import tarfile
import tempfile
from pathlib import Path

from PIL import Image, ImageOps
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

# Full set of app icon definitions: (width, height, filename)
APP_ICON_SIZES = [
    # Standard favicon PNGs
    (16, 16, "favicon-16x16.png"),
    (32, 32, "favicon-32x32.png"),
    (48, 48, "favicon-48x48.png"),
    # Apple touch icons
    (180, 180, "apple-touch-icon.png"),
    # Android / Chrome
    (192, 192, "android-chrome-192x192.png"),
    (512, 512, "android-chrome-512x512.png"),
]

SITE_WEBMANIFEST = {
    "name": "",
    "short_name": "",
    "icons": [
        {
            "src": "/android-chrome-192x192.png",
            "sizes": "192x192",
            "type": "image/png",
        },
        {
            "src": "/android-chrome-512x512.png",
            "sizes": "512x512",
            "type": "image/png",
        },
    ],
    "theme_color": "#ffffff",
    "background_color": "#ffffff",
    "display": "standalone",
}

BUNDLE_README = """\
# App Icons

This package contains a full set of icons for use with websites and web apps.

## Files Included

| File | Size | Purpose |
|------|------|---------|
| `favicon.ico` | 16, 32, 48px | Classic favicon for browsers |
| `favicon-16x16.png` | 16×16 | Small favicon PNG |
| `favicon-32x32.png` | 32×32 | Standard favicon PNG |
| `favicon-48x48.png` | 48×48 | High-DPI favicon PNG |
| `apple-touch-icon.png` | 180×180 | iOS home screen icon |
| `android-chrome-192x192.png` | 192×192 | Android home screen icon |
| `android-chrome-512x512.png` | 512×512 | Android splash / PWA icon |
| `site.webmanifest` | — | Web app manifest (PWA) |

## Usage

Place all files in the root of your website (e.g. `/public/` or `/static/`), then
add the following snippet to the `<head>` of your HTML:

```html
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="48x48" href="/favicon-48x48.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#ffffff">
```

### Notes

- Edit `site.webmanifest` to set your app `name`, `short_name`, and `theme_color`.
- For Next.js / Vite projects, place files in the `public/` directory.
- For a plain HTML site, place files in the web root alongside `index.html`.
"""


def rasterize_svg(svg_path: Path, target_size: int = 512) -> Image.Image:
    """
    Rasterise an SVG file to a PIL Image.

    The SVG is scaled so its longest dimension equals *target_size* pixels.
    The returned image is in RGBA mode with a transparent background.

    Args:
        svg_path: Path to the .svg file.
        target_size: Pixel size for the longest dimension (default 512).

    Returns:
        PIL Image in RGBA mode.

    Raises:
        ValueError: If the SVG file cannot be parsed.
    """
    drawing = svg2rlg(str(svg_path))
    if drawing is None:
        raise ValueError(f"Could not parse SVG file: {svg_path}")

    longest = max(drawing.width, drawing.height)
    if longest == 0:
        raise ValueError(f"SVG has zero dimensions: {svg_path}")

    scale = target_size / longest
    drawing.width = drawing.width * scale
    drawing.height = drawing.height * scale
    drawing.transform = (scale, 0, 0, scale, 0, 0)

    png_bytes = renderPM.drawToString(drawing, fmt="PNG", bg=-1)
    img = Image.open(io.BytesIO(png_bytes))
    return img.convert("RGBA")


def _load_image(input_path: Path) -> Image.Image:
    """
    Open an image file and return a PIL Image in RGB or RGBA mode.

    SVG files are rasterised via :func:`rasterize_svg`; all other
    formats are opened directly with Pillow.

    Args:
        input_path: Path to the image file.

    Returns:
        PIL Image in RGBA mode (SVG / images with alpha) or RGB mode.
    """
    if input_path.suffix.lower() == ".svg":
        return rasterize_svg(input_path)

    img = Image.open(input_path)
    # Apply EXIF orientation so camera images are not rotated/flipped incorrectly.
    img = ImageOps.exif_transpose(img)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    return img


def crop_to_square(image: Image.Image) -> Image.Image:
    """
    Crop an image to a square by taking the center portion.

    Args:
        image: PIL Image object to crop

    Returns:
        Cropped square PIL Image object
    """
    width, height = image.size

    if width == height:
        return image

    # Determine the size of the square (smallest dimension)
    size = min(width, height)

    # Calculate crop coordinates for center crop
    left = (width - size) // 2
    top = (height - size) // 2
    right = left + size
    bottom = top + size

    return image.crop((left, top, right, bottom))


def convert_to_ico(
    input_path: str | Path,
    output_path: str | Path,
    crop_square: bool = False,
) -> None:
    """
    Convert an image (JPEG, PNG, or WEBP) to .ico format.

    Args:
        input_path: Path to the input image file
        output_path: Path where the .ico file will be saved
        crop_square: If True, crop the image to a square before conversion

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If image format is not supported
        IOError: If there's an error reading or writing files
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    # Validate input file exists
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Validate input file format
    supported_formats = {".jpg", ".jpeg", ".png", ".webp", ".svg"}
    if input_path.suffix.lower() not in supported_formats:
        raise ValueError(
            f"Unsupported file format: {input_path.suffix}. "
            f"Supported formats: {', '.join(supported_formats)}"
        )

    # Ensure output has .ico extension
    if output_path.suffix.lower() != ".ico":
        output_path = output_path.with_suffix(".ico")

    # Open and process the image (SVG is rasterised automatically)
    img = _load_image(input_path)

    # Crop to square if requested
    if crop_square:
        img = crop_to_square(img)

    # Save as .ico with multiple sizes for better compatibility
    # Common favicon sizes: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256
    sizes = [
        (16, 16),
        (32, 32),
        (48, 48),
        (64, 64),
        (128, 128),
        (256, 256),
    ]
    img.save(output_path, format="ICO", sizes=sizes)


def generate_app_icons_bundle(
    input_path: str | Path,
    output_path: str | Path,
    crop_square: bool = False,
) -> None:
    """
    Generate a full set of app icons from a source image and bundle them
    into a .tar.gz archive with supporting manifest files and a README.

    The archive contains:
      - favicon.ico (16, 32, 48 px multi-resolution)
      - PNG icons at standard sizes for browsers, Apple, and Android
      - site.webmanifest  (PWA web app manifest)
      - README.md         (usage instructions and HTML snippets)

    Args:
        input_path:  Path to the source image (JPEG, PNG, or WEBP).
        output_path: Destination path for the .tar.gz archive.
        crop_square: If True, centre-crop the image to a square first.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If the image format is not supported.
        IOError: If there is an error reading or writing files.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    supported_formats = {".jpg", ".jpeg", ".png", ".webp", ".svg"}
    if input_path.suffix.lower() not in supported_formats:
        raise ValueError(
            f"Unsupported file format: {input_path.suffix}. "
            f"Supported formats: {', '.join(supported_formats)}"
        )

    if not output_path.suffix == ".gz":
        output_path = output_path.with_suffix(".tar.gz")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)

        # Open and process the image (SVG is rasterised automatically)
        img = _load_image(input_path)

        if crop_square:
            img = crop_to_square(img)

        # --- favicon.ico (multi-resolution) ---
        ico_path = tmp / "favicon.ico"
        ico_sizes = [(16, 16), (32, 32), (48, 48)]
        img.save(ico_path, format="ICO", sizes=ico_sizes)

        # --- PNG icons ---
        for width, height, filename in APP_ICON_SIZES:
            resized = img.resize((width, height), Image.LANCZOS)
            resized.save(tmp / filename, format="PNG")

        # --- site.webmanifest ---
        manifest_path = tmp / "site.webmanifest"
        manifest_path.write_text(
            json.dumps(SITE_WEBMANIFEST, indent=4), encoding="utf-8"
        )

        # --- README.md ---
        readme_path = tmp / "README.md"
        readme_path.write_text(BUNDLE_README, encoding="utf-8")

        # --- Bundle into tar.gz ---
        with tarfile.open(output_path, "w:gz") as tar:
            for file in sorted(tmp.iterdir()):
                tar.add(file, arcname=f"app-icons/{file.name}")
