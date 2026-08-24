#!/usr/bin/env python3
"""Print largest probability misses from walk-forward logistic/Elo models."""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.models.baselines import fit_logistic_baseline
from sports_ds.pipelines.team_win import FEATURE_COLS
from sports_ds.ratings.elo import add_elo_asof
from sports_ds.validation.splits import season_walk_forward_masks


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def _load_panel(sport: str, seasons: list[int]) -> pd.DataFrame:
    if sport == "nfl":
        from sports_ds.data.nfl import load_team_game_panel

        return load_team_game_panel(seasons)
    if sport == "nba":
        from sports_ds.data.nba import load_nba_team_game_panel

        return load_nba_team_game_panel(seasons)
    if sport == "mlb":
        from sports_ds.data.mlb import load_mlb_team_game_panel

        return load_mlb_team_game_panel(seasons)
    raise ValueError(sport)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sport", default="nfl", choices=["nfl", "nba", "mlb"])
    p.add_argument("--seasons", default="2018-2024")
    p.add_argument("--model", default="form", choices=["form", "elo"])
    p.add_argument("--min-train-seasons", type=int, default=2)
    p.add_argument("--top", type=int, default=20)
    args = p.parse_args()

    seasons = _parse_seasons(args.seasons)
    panel = _load_panel(args.sport, seasons)
    if args.model == "form":
        df = add_pregame_form_features(panel)
        feats = FEATURE_COLS
        df = df.dropna(subset=feats + ["won"]).copy()
        df = df[(df.pre_games_played >= 3) & (df.opp_pre_games_played >= 3)]
    else:
        df = add_elo_asof(panel)
        feats = ["is_home", "elo_diff"]
        df = df.dropna(subset=feats + ["won"]).copy()

    parts = []
    for season, tr, te in season_walk_forward_masks(df, min_train_seasons=args.min_train_seasons):
        _, _, pred = fit_logistic_baseline(df, feats, tr, te)
        cols = [c for c in ["season", "week", "team", "opponent", "is_home", "won", "elo_diff", "feature_win_pct_diff"] if c in df.columns]
        part = df.loc[te].dropna(subset=feats + ["won"])[cols].copy()
        part["p"] = np.asarray(pred, dtype=float)
        part["abs_err"] = (part["won"].astype(float) - part["p"]).abs()
        parts.append(part)

    if not parts:
        print("no folds")
        return 1
    out = pd.concat(parts, ignore_index=True).sort_values("abs_err", ascending=False).head(args.top)
    print(out.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
