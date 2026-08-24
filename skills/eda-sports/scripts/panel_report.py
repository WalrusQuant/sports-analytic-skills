#!/usr/bin/env python3
"""Write a JSON EDA report for the NFL team-game panel."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.eda.summary import summarize_team_game_panel


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seasons", default="2023-2024")
    p.add_argument("--out", default="data/eda_panel.json")
    args = p.parse_args()

    seasons = _parse_seasons(args.seasons)
    panel = load_team_game_panel(seasons)
    summary = summarize_team_game_panel(panel)
    summary["leakage_suspects_pregame"] = [
        "points_for",
        "points_against",
        "won",
        "point_diff",
    ]
    summary["notes"] = [
        "overall_win_rate on team-game panel should be ~0.5 because each game contributes one win and one loss row",
        "use home rows (is_home==1) for home-field advantage estimates",
    ]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(
        f"rows={summary['rows']} games={summary['n_games']} teams={summary['n_teams']} "
        f"home_win_rate={summary.get('home_win_rate')}"
    )
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
