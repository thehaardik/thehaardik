#!/usr/bin/env python3
"""
fetch_contributions.py — Scrape public contribution calendar from GitHub.

No token needed. GitHub serves the contribution HTML at:
  https://github.com/users/<username>/contributions

Output: data/contributions.json with raw days + derived stats.

Usage:
  python scripts/fetch_contributions.py
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path

USERNAME = "thehaardik"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT = "data/contributions.json"

# Level to approximate contribution count mapping
LEVEL_TO_COUNT = {0: 0, 1: 1, 2: 3, 3: 5, 4: 8}


def fetch_contributions():
    print(f"Fetching contributions for {USERNAME}...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    resp = requests.get(URL, headers=headers, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Parse td cells with data-date and data-level
    days = []
    for td in soup.find_all("td"):
        date = td.get("data-date")
        level = td.get("data-level")
        if date and level is not None:
            level = int(level)
            count = LEVEL_TO_COUNT.get(level, 0)
            days.append({
                "date": date,
                "count": count,
                "level": level,
            })

    # Sort by date
    days.sort(key=lambda d: d["date"])

    if not days:
        print("Warning: No contribution data found.")

    return days


def compute_stats(days: list) -> dict:
    """Compute derived statistics from raw day data."""
    if not days:
        return {
            "total": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "best_day": {"date": "", "count": 0},
            "monthly": {},
            "active_days": 0,
            "avg_per_active_day": 0,
        }

    total = sum(d["count"] for d in days)
    active_days = sum(1 for d in days if d["count"] > 0)

    # Current streak (from most recent day going backwards)
    today = datetime.now().date()
    current_streak = 0
    for d in reversed(days):
        day_date = datetime.strptime(d["date"], "%Y-%m-%d").date()
        if d["count"] > 0 and day_date <= today:
            current_streak += 1
        elif day_date < today:
            break

    # Longest streak
    longest_streak = 0
    streak = 0
    for d in days:
        if d["count"] > 0:
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            streak = 0

    # Best day
    best = max(days, key=lambda d: d["count"])

    # Monthly totals
    monthly = {}
    for d in days:
        month = d["date"][:7]  # YYYY-MM
        monthly[month] = monthly.get(month, 0) + d["count"]

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": monthly,
        "active_days": active_days,
        "avg_per_active_day": round(total / active_days, 1) if active_days > 0 else 0,
    }


def main():
    days = fetch_contributions()
    stats = compute_stats(days)

    data = {
        "username": USERNAME,
        "fetched_at": datetime.now().isoformat(),
        "days": days,
        "stats": stats,
    }

    Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    Path(OUTPUT).write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"Done! Output: {OUTPUT}")
    print(f"Total contributions: {stats['total']:,}")
    print(f"Current streak: {stats['current_streak']} days")
    print(f"Longest streak: {stats['longest_streak']} days")
    print(f"Active days: {stats['active_days']}")


if __name__ == "__main__":
    main()
