#!/usr/bin/env python3
"""Compare walk-forward logistic log-loss for roll features vs EWMA features."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.models.baselines import baseline_home_rate, fit_logistic_baseline
from sports_ds.validation.splits import season_walk_forward_masks

sys.path.append(str(Path(__file__).resolve().parent))
from ewma_form import add_ewma_form


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seasons", default="2018-2024")
    p.add_argument("--span", type=float, default=5.0)
    p.add_argument("--min-train-seasons", type=int, default=2)
    args = p.parse_args()

    base = load_team_game_panel(_parse_seasons(args.seasons))
    roll = add_pregame_form_features(base)
    ewma = add_ewma_form(base, span=args.span)
    df = roll.merge(
        ewma[["game_id", "team", "ewma_win_diff", "ewma_diff_diff"]],
        on=["game_id", "team"],
        how="left",
    )

    roll_cols = ["is_home", "feature_win_pct_diff", "feature_diff_diff", "feature_roll3_win_diff", "feature_roll5_diff_diff"]
    ewma_cols = ["is_home", "ewma_win_diff", "ewma_diff_diff"]
    df = df.dropna(subset=roll_cols + ewma_cols + ["won"])
    df = df[(df.pre_games_played >= 3) & (df.opp_pre_games_played >= 3)]

    print("season,n,const_ll,roll_ll,ewma_ll")
    for season, tr, te in season_walk_forward_masks(df, min_train_seasons=args.min_train_seasons):
        c = baseline_home_rate(df, tr, te)
        _, r, _ = fit_logistic_baseline(df, roll_cols, tr, te)
        _, e, _ = fit_logistic_baseline(df, ewma_cols, tr, te)
        print(f"{season},{c.n},{c.log_loss:.4f},{r.log_loss:.4f},{e.log_loss:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
