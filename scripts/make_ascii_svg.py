#!/usr/bin/env python3
"""
make_ascii_svg.py — Convert a prepped grayscale photo into a self-typing ASCII SVG.

Each row wipes left-to-right with a small "cursor" block, staggered top to bottom.
The portrait prints once and freezes (SMIL, no loop).

Usage:
  python scripts/make_ascii_svg.py
"""

import sys
from pathlib import Path
from PIL import Image

# ASCII density ramp: bright (sparse) -> dark (dense)
RAMP = " .`:-=+*cs#%@"
WIDTH_CHARS = 100  # character width of the grid
OUTPUT = "thehaardik-ascii.svg"

# Monochrome color — light gray for all characters
FILL_COLOR = "#c9d1d9"


def brightness_to_char(brightness: int) -> str:
    """Map 0-255 brightness to an ASCII character."""
    # Invert: 0 (black) -> densest char, 255 (white) -> space
    idx = int((255 - brightness) / 256 * len(RAMP))
    idx = min(idx, len(RAMP) - 1)
    return RAMP[idx]


def load_and_resize(path: str, target_width: int) -> list[list[int]]:
    """Load image, resize to target_width maintaining aspect ratio."""
    img = Image.open(path).convert("L")  # grayscale
    w, h = img.size
    # ASCII chars are ~2x taller than wide, so halve the height
    target_height = int(h / w * target_width * 0.45)
    img = img.resize((target_width, target_height), Image.LANCZOS)
    return [list(row) for row in img.getdata()], target_width, target_height


def generate_svg(pixels: list[list[int]], width: int, height: int) -> str:
    """Generate self-typing ASCII SVG with SMIL animations."""
    char_width = 7.2  # px per character
    char_height = 14  # px per line
    svg_width = int(width * char_width)
    svg_height = int(height * char_height)

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">')
    lines.append(f'<rect width="{svg_width}" height="{svg_height}" fill="#0d1117"/>')

    # Define a clip path for the typing animation per row
    for row_idx, row in enumerate(pixels):
        y = row_idx * char_height
        clip_id = f"row-{row_idx}"

        # Each row wipes left-to-right
        delay = f"{row_idx * 0.03}s"  # stagger
        duration = "0.4s"

        lines.append(f'<defs>')
        lines.append(f'  <clipPath id="{clip_id}">')
        lines.append(f'    <rect x="0" y="{y}" width="0" height="{char_height}">')
        lines.append(f'      <animate attributeName="width" from="0" to="{svg_width}" dur="{duration}" begin="{delay}" fill="freeze"/>')
        lines.append(f'    </rect>')
        lines.append(f'  </clipPath>')
        lines.append(f'</defs>')

        # Cursor block that rides the wipe edge
        lines.append(f'<rect x="0" y="{y}" width="8" height="{char_height}" fill="{FILL_COLOR}" opacity="0.6">')
        lines.append(f'  <animate attributeName="x" from="0" to="{svg_width}" dur="{duration}" begin="{delay}" fill="freeze"/>')
        lines.append(f'  <animate attributeName="opacity" from="0.6" to="0" dur="0.1s" begin="{float(row_idx * 0.03) + 0.4}s" fill="freeze"/>')
        lines.append(f'</rect>')

        # Characters for this row
        lines.append(f'<g clip-path="url(#{clip_id})">')
        for col_idx, brightness in enumerate(row):
            char = brightness_to_char(brightness)
            if char == " ":
                continue  # skip spaces for cleaner rendering
            x = col_idx * char_width
            # Escape XML special characters
            char_escaped = char.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            lines.append(f'  <text x="{x:.1f}" y="{y + char_height - 2}" fill="{FILL_COLOR}" font-family="monospace" font-size="13">{char_escaped}</text>')
        lines.append(f'</g>')

    lines.append('</svg>')
    return "\n".join(lines)


def main():
    source = Path("data/source-prepped.png")
    if not source.exists():
        print(f"Error: {source} not found. Run prep_photo.py first.")
        sys.exit(1)

    print(f"Loading {source}...")
    pixels, w, h = load_and_resize(str(source), WIDTH_CHARS)
    print(f"Grid: {w}x{h} characters")

    print("Generating SVG...")
    svg = generate_svg(pixels, w, h)

    output_path = Path(OUTPUT)
    output_path.write_text(svg, encoding="utf-8")
    print(f"Done! Output: {output_path}")
    print(f"SVG size: {len(svg):,} bytes")


if __name__ == "__main__":
    main()
