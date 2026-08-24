#!/usr/bin/env python3
from __future__ import annotations

import argparse

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.validation.splits import season_walk_forward_masks


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description="Print season walk-forward fold sizes")
    p.add_argument("--seasons", default="2018-2024")
    p.add_argument("--min-train-seasons", type=int, default=2)
    args = p.parse_args()

    df = add_pregame_form_features(load_team_game_panel(_parse_seasons(args.seasons)))
    df = df.dropna(subset=["won", "is_home", "feature_win_pct_diff"])
    print("test_season,n_train,n_test")
    for season, tr, te in season_walk_forward_masks(df, min_train_seasons=args.min_train_seasons):
        print(f"{season},{int(tr.sum())},{int(te.sum())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
