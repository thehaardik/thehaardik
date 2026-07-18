#!/usr/bin/env python3
"""
render_heatmap_svg.py — Render contribution data as an animated heatmap SVG.

Reads data/contributions.json and generates contrib-heatmap.svg with:
  - 53-week × 7-day grid of rounded boxes
  - GitHub-ish green palette
  - Diagonal slide-in animation (plays once, freezes)
  - Stats footer

Usage:
  python scripts/render_heatmap_svg.py
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

INPUT = "data/contributions.json"
OUTPUT = "thehaardik-contrib-heatmap.svg"

# GitHub green palette: none -> brightest
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

# Dimensions
BOX_SIZE = 11
BOX_GAP = 3
CELL_SIZE = BOX_SIZE + BOX_GAP
WEEKS = 53
DAYS_IN_WEEK = 7
LEGEND_HEIGHT = 28
STATS_HEIGHT = 24
PADDING_LEFT = 40
PADDING_TOP = 30
PADDING_BOTTOM = 16

GRID_WIDTH = PADDING_LEFT + WEEKS * CELL_SIZE + 10
GRID_HEIGHT = PADDING_TOP + DAYS_IN_WEEK * CELL_SIZE
SVG_WIDTH = GRID_WIDTH
SVG_HEIGHT = GRID_HEIGHT + LEGEND_HEIGHT + STATS_HEIGHT + PADDING_BOTTOM

# Day labels
DAY_LABELS = ["", "Mon", "", "Wed", "", "Fri", ""]

# Month labels
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_data() -> dict:
    with open(INPUT, "r") as f:
        return json.load(f)


def build_date_map(days: list) -> dict:
    """Map date strings to contribution counts."""
    return {d["date"]: d["count"] for d in days}


def get_month_labels(weeks_data: list) -> list:
    """Determine which months appear at which week columns."""
    labels = []
    last_month = None
    for week_idx, week in enumerate(weeks_data):
        # Use the Monday of each week
        if week:
            day_date = datetime.strptime(week[0], "%Y-%m-%d")
            month = day_date.month
            if month != last_month:
                labels.append((week_idx, MONTH_NAMES[month - 1]))
                last_month = month
    return labels


def generate_svg(data: dict) -> str:
    days = data.get("days", [])
    stats = data.get("stats", {})
    date_map = build_date_map(days)

    # Build 53 weeks × 7 days grid
    # Find the most recent Saturday (GitHub weeks end on Saturday)
    if days:
        last_date = datetime.strptime(days[-1]["date"], "%Y-%m-%d")
    else:
        last_date = datetime.now()

    # Go back 52 weeks from the last Saturday
    end_saturday = last_date + timedelta(days=(5 - last_date.weekday()) % 7)
    start_monday = end_saturday - timedelta(weeks=52, days=6)

    weeks_data = []
    current = start_monday
    for week in range(WEEKS):
        week_days = []
        for day in range(DAYS_IN_WEEK):
            date_str = current.strftime("%Y-%m-%d")
            count = date_map.get(date_str, 0)
            week_days.append(date_str)
            current += timedelta(days=1)
        weeks_data.append(week_days)

    # Month labels
    month_labels = get_month_labels(weeks_data)

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" width="{SVG_WIDTH}" height="{SVG_HEIGHT}">')
    lines.append(f'<rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" fill="#0d1117"/>')

    # Title
    lines.append(f'<text x="{PADDING_LEFT}" y="18" fill="#c9d1d9" font-family="monospace" font-size="13" font-weight="bold">Contribution Activity</text>')

    # Day labels
    for day_idx, label in enumerate(DAY_LABELS):
        if label:
            y = PADDING_TOP + day_idx * CELL_SIZE + BOX_SIZE - 1
            lines.append(f'<text x="0" y="{y}" fill="#484f58" font-family="monospace" font-size="10">{label}</text>')

    # Month labels
    for week_idx, month_name in month_labels:
        x = PADDING_LEFT + week_idx * CELL_SIZE
        lines.append(f'<text x="{x}" y="{PADDING_TOP - 8}" fill="#484f58" font-family="monospace" font-size="10">{month_name}</text>')

    # Contribution boxes with diagonal slide-in animation
    for week_idx, week in enumerate(weeks_data):
        for day_idx, date_str in enumerate(week):
            count = date_map.get(date_str, 0)
            level = min(count, 5) if count > 0 else 0
            color = PALETTE[level]

            x = PADDING_LEFT + week_idx * CELL_SIZE
            y = PADDING_TOP + day_idx * CELL_SIZE

            # Animation: diagonal slide-in, staggered by week + day
            delay = f"{(week_idx * 0.01 + day_idx * 0.005):.3f}s"

            lines.append(f'<g opacity="0">')
            lines.append(f'  <animate attributeName="opacity" from="0" to="1" dur="0.2s" begin="{delay}" fill="freeze"/>')
            lines.append(f'  <animateTransform attributeName="transform" type="translate" from="-4 -4" to="0 0" dur="0.2s" begin="{delay}" fill="freeze"/>')
            lines.append(f'  <rect x="{x}" y="{y}" width="{BOX_SIZE}" height="{BOX_SIZE}" rx="2" fill="{color}">')
            lines.append(f'    <title>{count} contributions on {date_str}</title>')
            lines.append(f'  </rect>')
            lines.append(f'</g>')

    # Legend
    legend_y = GRID_HEIGHT + 8
    lines.append(f'<text x="{PADDING_LEFT}" y="{legend_y + 10}" fill="#484f58" font-family="monospace" font-size="10">Less</text>')
    for i, color in enumerate(PALETTE):
        x = PADDING_LEFT + 36 + i * (BOX_SIZE + BOX_GAP)
        lines.append(f'<rect x="{x}" y="{legend_y}" width="{BOX_SIZE}" height="{BOX_SIZE}" rx="2" fill="{color}"/>')
    lines.append(f'<text x="{PADDING_LEFT + 36 + len(PALETTE) * (BOX_SIZE + BOX_GAP) + 6}" y="{legend_y + 10}" fill="#484f58" font-family="monospace" font-size="10">More</text>')

    # Stats footer
    stats_y = GRID_HEIGHT + LEGEND_HEIGHT + 8
    total = stats.get("total", 0)
    streak = stats.get("current_streak", 0)
    lines.append(f'<text x="{PADDING_LEFT}" y="{stats_y + 10}" fill="#8b949e" font-family="monospace" font-size="11">{total:,} contributions in the last year | {streak} day streak</text>')

    lines.append('</svg>')
    return "\n".join(lines)


def main():
    if not Path(INPUT).exists():
        print(f"Error: {INPUT} not found. Run fetch_contributions.py first.")
        exit(1)

    data = load_data()
    svg = generate_svg(data)

    Path(OUTPUT).write_text(svg, encoding="utf-8")
    print(f"Done! Output: {OUTPUT}")
    print(f"SVG size: {len(svg):,} bytes")
    print(f"Contributions: {data['stats']['total']:,}")


if __name__ == "__main__":
    main()
