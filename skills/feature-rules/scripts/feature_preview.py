#!/usr/bin/env python3
from __future__ import annotations

import argparse

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.pipelines.nfl_win_model import FEATURE_COLS


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description="Preview time-safe team form features")
    p.add_argument("--seasons", default="2023-2024")
    args = p.parse_args()

    df = add_pregame_form_features(load_team_game_panel(_parse_seasons(args.seasons)))
    print("rows", len(df))
    print("feature cols", FEATURE_COLS)
    print("null rates:")
    for c in FEATURE_COLS:
        print(f"  {c}: {df[c].isna().mean():.3f}")
    cols = ["season", "week", "team", "opponent", "is_home", "won"] + FEATURE_COLS
    print(df[cols].head(8).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
