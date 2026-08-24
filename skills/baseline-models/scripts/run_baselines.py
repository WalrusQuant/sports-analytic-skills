#!/usr/bin/env python3
from __future__ import annotations

import argparse

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.models.baselines import baseline_home_rate, fit_logistic_baseline
from sports_ds.pipelines.nfl_win_model import FEATURE_COLS
from sports_ds.validation.splits import season_walk_forward_masks


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description="Walk-forward constant vs logistic baselines")
    p.add_argument("--seasons", default="2018-2024")
    p.add_argument("--min-train-seasons", type=int, default=2)
    args = p.parse_args()

    df = add_pregame_form_features(load_team_game_panel(_parse_seasons(args.seasons)))
    df = df.dropna(subset=FEATURE_COLS + ["won"])
    df = df[(df.pre_games_played >= 3) & (df.opp_pre_games_played >= 3)]

    print("season,n_test,constant_ll,logistic_ll,logistic_acc")
    for season, tr, te in season_walk_forward_masks(df, min_train_seasons=args.min_train_seasons):
        c = baseline_home_rate(df, tr, te)
        _, loc, _ = fit_logistic_baseline(df, FEATURE_COLS, tr, te)
        print(f"{season},{c.n},{c.log_loss:.4f},{loc.log_loss:.4f},{loc.accuracy:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
