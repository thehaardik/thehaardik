#!/usr/bin/env python3
"""
make_info_card.py — Generate a neofetch-style info card SVG.

Hand-authored SVG with fade-in line-by-line animation.
Set STATIC=1 for a frozen frame (no animation).

Usage:
  python scripts/make_info_card.py
  STATIC=1 python scripts/make_info_card.py  # for local preview
"""

import os
from pathlib import Path

OUTPUT = "thehaardik-info-card.svg"
STATIC = os.environ.get("STATIC", "0") == "1"

# Content — edit these to update your profile
TITLE = "hardik@github"
SUBTITLE = "----------------"

ROWS = [
    ("role", "Senior TPM @ Kodo | Fintech & Payments"),
    ("stack", "Python, Node.js, SQL, REST APIs, AI Agents"),
    ("focus", "Banking Infra, Card Issuance, Reconciliation"),
    ("highlights", "7+ Banking Integrations | 20% Faster Go-Live"),
    ("avail", "Open to Opportunities"),
]

# Colors
BG_COLOR = "#0d1117"
KEY_COLOR = "#58a6ff"      # blue for keys
VALUE_COLOR = "#c9d1d9"    # light gray for values
TITLE_COLOR = "#f0f6fc"    # white for title
ACCENT_COLOR = "#238636"   # green accent

# Dimensions
WIDTH = 490
LINE_HEIGHT = 28
PADDING_X = 24
PADDING_Y = 20
TITLE_HEIGHT = 36
TOTAL_HEIGHT = PADDING_Y * 2 + TITLE_HEIGHT + len(ROWS) * LINE_HEIGHT + 10


def generate_svg() -> str:
    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {TOTAL_HEIGHT}" width="{WIDTH}" height="{TOTAL_HEIGHT}">')
    lines.append(f'<rect width="{WIDTH}" height="{TOTAL_HEIGHT}" rx="8" fill="{BG_COLOR}"/>')

    # Border
    lines.append(f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{TOTAL_HEIGHT - 1}" rx="8" fill="none" stroke="#30363d" stroke-width="1"/>')

    # Title bar
    y = PADDING_Y + 14
    lines.append(f'<text x="{PADDING_X}" y="{y}" fill="{TITLE_COLOR}" font-family="monospace" font-size="15" font-weight="bold">{TITLE}</text>')
    lines.append(f'<text x="{PADDING_X}" y="{y + 18}" fill="#484f58" font-family="monospace" font-size="12">{SUBTITLE}</text>')

    # Accent dot
    lines.append(f'<circle cx="{PADDING_X + 8}" cy="{y + 40}" r="3" fill="{ACCENT_COLOR}"/>')

    # Data rows
    for i, (key, value) in enumerate(ROWS):
        row_y = PADDING_Y + TITLE_HEIGHT + 30 + i * LINE_HEIGHT

        anim_delay = f'{i * 0.15}s' if not STATIC else '0s'
        anim_dur = '0.3s' if not STATIC else '0s'
        opacity_attr = '' if not STATIC else ' opacity="1"'

        # Fade-in + slide-up animation
        if not STATIC:
            lines.append(f'<g opacity="0">')
            lines.append(f'  <animate attributeName="opacity" from="0" to="1" dur="{anim_dur}" begin="{anim_delay}" fill="freeze"/>')
            lines.append(f'  <animateTransform attributeName="transform" type="translate" from="0 8" to="0 0" dur="{anim_dur}" begin="{anim_delay}" fill="freeze"/>')

        # Key
        lines.append(f'  <text x="{PADDING_X}" y="{row_y}" fill="{KEY_COLOR}" font-family="monospace" font-size="13">{key}</text>')
        # Colon
        lines.append(f'  <text x="{PADDING_X + 80}" y="{row_y}" fill="#484f58" font-family="monospace" font-size="13">:</text>')
        # Value
        lines.append(f'  <text x="{PADDING_X + 96}" y="{row_y}" fill="{VALUE_COLOR}" font-family="monospace" font-size="13">{value}</text>')

        if not STATIC:
            lines.append(f'</g>')

    lines.append('</svg>')
    return "\n".join(lines)


def main():
    svg = generate_svg()
    Path(OUTPUT).write_text(svg, encoding="utf-8")
    print(f"Done! Output: {OUTPUT}")
    print(f"SVG size: {len(svg):,} bytes")
    if STATIC:
        print("(Static mode — no animation)")


if __name__ == "__main__":
    main()
