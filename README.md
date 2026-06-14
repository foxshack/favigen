# Favicon Generator

A Python CLI tool to generate favicons and web app icon bundles from images (JPEG, PNG, WEBP, or SVG).

## Installation

Install using pipx (recommended):

```bash
pipx install git+https://github.com/foxshack/favigen.git@0.6.0
```

## Usage

Basic usage:

```bash
favigen image.png
```

This will create `image.ico` in the same directory.

Specify a custom output filename:

```bash
favigen image.jpg -o my-favicon.ico
```

Crop image to square before processing:

```bash
favigen image.webp --crop -o favicon.ico
```

Generate a full app icon bundle (`.tar.gz`):

```bash
favigen image.png --app-icons
```

This creates `app-icons.tar.gz` in the same directory. Specify a custom output path with `-o`:

```bash
favigen image.png --app-icons -o my-project-icons.tar.gz
```

The `--crop` flag also works with `--app-icons`:

```bash
favigen image.jpg --app-icons --crop
```

### App Icon Bundle Contents

| File | Size | Purpose |
|------|------|---------|
| `favicon.ico` | 16, 32, 48px | Classic browser favicon |
| `favicon-16x16.png` | 16×16 | Small favicon PNG |
| `favicon-32x32.png` | 32×32 | Standard favicon PNG |
| `favicon-48x48.png` | 48×48 | High-DPI favicon PNG |
| `apple-touch-icon.png` | 180×180 | iOS home screen icon |
| `android-chrome-192x192.png` | 192×192 | Android home screen icon |
| `android-chrome-512x512.png` | 512×512 | Android splash / PWA icon |
| `maskable-icon-192x192.png` | 192×192 | Android/PWA maskable icon |
| `maskable-icon-512x512.png` | 512×512 | Android/PWA maskable icon |
| `site.webmanifest` | — | Web app manifest (PWA) |
| `README.md` | — | Usage instructions and HTML snippets |

If the input file is SVG, the bundle also includes `favicon.svg` for modern browsers.

### Options

- `INPUT_FILE`: Path to the input image (JPEG, PNG, WEBP, or SVG)
- `-o, --output`: Output filename (`.ico` by default; `.tar.gz` with `--app-icons`)
- `-c, --crop`: Crop image to square before processing
- `-a, --app-icons`: Generate full app icon bundle as a `.tar.gz` archive
- `--version`: Show version information
- `--help`: Show help message

## Supported Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- WEBP (.webp)
- SVG (.svg)

## Features

- Converts images to multi-resolution .ico files
- Generates a full app icon bundle (`.tar.gz`) covering browsers, Apple, and Android/PWA use cases
- Bundle includes `site.webmanifest` and a README with HTML snippets
- Supports common image formats (JPEG, PNG, WEBP, SVG)
- Optional center-crop to square
- Custom output filenames
- Generates multiple icon sizes for better compatibility (16×16 through 512×512)

## Recommended HTML

For best modern compatibility, use this in your page head:

```html
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#ffffff">
```

Notes:
- Keep ICO as a fallback for legacy compatibility.
- The SVG icon line is only applicable if your generated bundle includes `favicon.svg`.

## License

MIT License - see LICENSE file for details
