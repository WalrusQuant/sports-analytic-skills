#!/usr/bin/env python3
"""Smoke checks that pre-game features are shifted (not equal to current outcomes)."""

from __future__ import annotations

import sys

import pandas as pd

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features


def main() -> int:
    panel = load_team_game_panel([2023, 2024])
    df = add_pregame_form_features(panel)
    # current won must not equal pre_win_pct identically on rows with history
    hist = df[df["pre_games_played"] >= 1].copy()
    if hist.empty:
        print("FAIL: no rows with history")
        return 1

    # pre_win_pct should not be perfectly identical to current won
    same = (hist["pre_win_pct"] == hist["won"]).mean()
    if same > 0.95:
        print(f"FAIL: pre_win_pct equals won too often ({same:.3f})")
        return 2

    # first game overall for each team should have NA pre features
    first = df.sort_values(["team", "season", "week"]).groupby(["team"], as_index=False).head(1)
    na_rate = first["pre_win_pct"].isna().mean()
    if na_rate < 0.9:
        print(f"FAIL: expected NA pre_win_pct on each team's first game; na_rate={na_rate:.3f}")
        return 3

    # current-game outcomes must not be in model feature list used by pipeline
    from sports_ds.pipelines.nfl_win_model import FEATURE_COLS

    banned = {"won", "points_for", "points_against", "point_diff"}
    overlap = banned.intersection(FEATURE_COLS)
    if overlap:
        print(f"FAIL: pipeline features include outcomes: {overlap}")
        return 4

    print(
        f"OK: leakage smoke passed (pre_win_pct==won rate={same:.3f}, "
        f"first_team_game_na={na_rate:.3f})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
