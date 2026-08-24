#!/usr/bin/env python3
"""Describe sports_ds NFL team-game panel for given seasons."""

from __future__ import annotations

import argparse

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.eda.summary import format_summary, summarize_team_game_panel


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seasons", default="2024")
    args = p.parse_args()
    panel = load_team_game_panel(_parse_seasons(args.seasons))
    print(format_summary(summarize_team_game_panel(panel)))
    print("columns:", list(panel.columns))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
