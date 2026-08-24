#!/usr/bin/env python3
"""Print walk-forward constant / logistic / hist-GBM metrics for NFL wins."""

from __future__ import annotations

import argparse

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.models.baselines import baseline_home_rate, fit_logistic_baseline
from sports_ds.models.predict import fit_win_classifier
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
    p.add_argument("--min-train-seasons", type=int, default=2)
    p.add_argument("--min-pre-games", type=int, default=3)
    args = p.parse_args()

    df = add_pregame_form_features(load_team_game_panel(_parse_seasons(args.seasons)))
    df = df.dropna(subset=FEATURE_COLS + ["won"])
    df = df[
        (df["pre_games_played"] >= args.min_pre_games)
        & (df["opp_pre_games_played"] >= args.min_pre_games)
    ]

    print("season,n_test,const_ll,log_ll,gbm_ll,log_acc,gbm_acc")
    for season, tr, te in season_walk_forward_masks(df, min_train_seasons=args.min_train_seasons):
        c = baseline_home_rate(df, tr, te)
        _, log_res, _ = fit_logistic_baseline(df, FEATURE_COLS, tr, te)
        _, gbm_res, _ = fit_win_classifier(df, FEATURE_COLS, tr, te, model_type="hist_gbm")
        print(
            f"{season},{c.n},{c.log_loss:.4f},{log_res.log_loss:.4f},{gbm_res.log_loss:.4f},"
            f"{log_res.accuracy:.3f},{gbm_res.accuracy:.3f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
