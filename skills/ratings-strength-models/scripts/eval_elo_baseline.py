#!/usr/bin/env python3
"""Walk-forward evaluate logistic baseline on Elo differential features."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.models.baselines import baseline_home_rate, fit_logistic_baseline
from sports_ds.validation.splits import season_walk_forward_masks

sys.path.append(str(Path(__file__).resolve().parent))
from elo_asof import build_elo_asof_table


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seasons", default="2018-2024")
    p.add_argument("--k", type=float, default=20.0)
    p.add_argument("--home-adv", type=float, default=65.0)
    p.add_argument("--min-train-seasons", type=int, default=2)
    args = p.parse_args()

    panel = load_team_game_panel(_parse_seasons(args.seasons))
    elo = build_elo_asof_table(panel, k=args.k, home_adv=args.home_adv)
    df = elo.dropna(subset=["elo_diff", "won", "is_home"]).copy()
    df["is_home"] = df["is_home"].astype(float)

    print("season,n_test,const_ll,elo_log_ll,elo_acc")
    for season, tr, te in season_walk_forward_masks(df, min_train_seasons=args.min_train_seasons):
        c = baseline_home_rate(df, tr, te)
        _, res, _ = fit_logistic_baseline(df, ["is_home", "elo_diff"], tr, te)
        print(f"{season},{c.n},{c.log_loss:.4f},{res.log_loss:.4f},{res.accuracy:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
