# favicon-generator

A Python CLI tool to generate .ico favicon files from images (JPEG, PNG, or WEBP).

## Installation

Install using pipx (recommended):

```bash
pipx install git+https://github.com/mikeh74/favicon-generator.git@v1.0
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
| `site.webmanifest` | — | Web app manifest (PWA) |
| `README.md` | — | Usage instructions and HTML snippets |

### Options

- `INPUT_FILE`: Path to the input image (JPEG, PNG, or WEBP)
- `-o, --output`: Output filename (`.ico` by default; `.tar.gz` with `--app-icons`)
- `-c, --crop`: Crop image to square before processing
- `-a, --app-icons`: Generate full app icon bundle as a `.tar.gz` archive
- `--version`: Show version information
- `--help`: Show help message

## Supported Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- WEBP (.webp)

## Features

- Converts images to multi-resolution .ico files
- Generates a full app icon bundle (`.tar.gz`) covering browsers, Apple, Android, and Windows
- Bundle includes `site.webmanifest` and a README with HTML snippets
- Supports common image formats (JPEG, PNG, WEBP)
- Optional center-crop to square
- Custom output filenames
- Generates multiple icon sizes for better compatibility (16×16 through 512×512)

## License

MIT License - see LICENSE file for details
