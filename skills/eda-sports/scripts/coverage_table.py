#!/usr/bin/env python3
"""Print season x week coverage counts for NFL team-game panel."""

from __future__ import annotations

import argparse

from sports_ds.data.nfl import load_team_game_panel


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seasons", default="2023-2024")
    args = p.parse_args()

    panel = load_team_game_panel(_parse_seasons(args.seasons))
    # games per season-week = team-game rows / 2
    g = (
        panel.groupby(["season", "week"], as_index=False)
        .agg(team_game_rows=("game_id", "size"), games=("game_id", "nunique"), teams=("team", "nunique"))
        .sort_values(["season", "week"])
    )
    print(g.to_string(index=False))
    print(
        f"\nseasons={sorted(panel.season.unique().tolist())} "
        f"rows={len(panel)} games={panel.game_id.nunique()} teams={panel.team.nunique()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
