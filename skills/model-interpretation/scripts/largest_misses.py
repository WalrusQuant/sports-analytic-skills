#!/usr/bin/env python3
"""Print largest probability misses from walk-forward logistic model."""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.models.baselines import fit_logistic_baseline
from sports_ds.pipelines.nfl_win_model import FEATURE_COLS
from sports_ds.validation.splits import season_walk_forward_masks


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seasons", default="2018-2024")
    p.add_argument("--top", type=int, default=20)
    args = p.parse_args()

    df = add_pregame_form_features(load_team_game_panel(_parse_seasons(args.seasons)))
    df = df.dropna(subset=FEATURE_COLS + ["won"]).copy()
    df = df[(df.pre_games_played >= 3) & (df.opp_pre_games_played >= 3)]

    parts = []
    for season, tr, te in season_walk_forward_masks(df):
        _, _, pred = fit_logistic_baseline(df, FEATURE_COLS, tr, te)
        part = df.loc[te, ["season", "week", "team", "opponent", "is_home", "won"]].copy()
        part["p"] = np.asarray(pred, dtype=float)
        part["abs_err"] = (part["won"].astype(float) - part["p"]).abs()
        parts.append(part)

    out = pd.concat(parts, ignore_index=True).sort_values("abs_err", ascending=False).head(args.top)
    print(out.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
