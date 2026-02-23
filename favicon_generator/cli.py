"""Command-line interface for favigen."""

import sys
from pathlib import Path

import click

from .converter import convert_to_ico, generate_app_icons_bundle


@click.command()
@click.argument(
    "input_file", type=click.Path(exists=True, dir_okay=False, readable=True)
)
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False, writable=True),
    help=(
        "Output filename (default: input name with .ico extension,"
        " or app-icons.tar.gz with --app-icons)"
    ),
)
@click.option(
    "-c", "--crop", is_flag=True, help="Crop image to square before processing"
)
@click.option(
    "-a",
    "--app-icons",
    "app_icons",
    is_flag=True,
    help="Generate a full set of app icons bundled into a .tar.gz archive",
)
@click.version_option()
def main(input_file, output, crop, app_icons):
    """
    Convert an image (JPEG, PNG, WEBP, or SVG) to .ico favicon format.

    SVG files are rasterised to 512 × 512 px before conversion.

    With --app-icons, generates a full set of web/app icons bundled into
    a .tar.gz archive including a README with usage instructions.

    INPUT_FILE: Path to the image file to convert

    Examples:

        favigen image.png

        favigen logo.svg

        favigen image.jpg -o my-favicon.ico

        favigen image.webp --crop -o favicon.ico

        favigen image.png --app-icons

        favigen logo.svg --app-icons -o my-icons.tar.gz
    """
    try:
        input_path = Path(input_file)

        if app_icons:
            # Determine output path for the tar.gz bundle
            if output:
                output_path = Path(output)
                if not str(output_path).endswith(".tar.gz"):
                    fixed = str(output_path).removesuffix(".tar") + ".tar.gz"
                    output_path = Path(fixed)
            else:
                output_path = input_path.parent / "app-icons.tar.gz"

            click.echo(f"Generating app icon bundle from {input_path}...")
            if crop:
                click.echo("Cropping to square...")

            generate_app_icons_bundle(input_path, output_path, crop_square=crop)

            click.echo(f"✓ Successfully created {output_path}")
            click.echo(
                "  Archive contains: favicon.ico, PNGs for"
                " browser/Apple/Android,\n"
                "  site.webmanifest, and README.md."
            )

        else:
            # Determine output path for the .ico file
            if output:
                output_path = Path(output)
            else:
                output_path = input_path.with_suffix(".ico")

            click.echo(f"Converting {input_path} to {output_path}...")
            if crop:
                click.echo("Cropping to square...")

            convert_to_ico(input_path, output_path, crop_square=crop)

            click.echo(f"✓ Successfully created {output_path}")

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: An unexpected error occurred: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
