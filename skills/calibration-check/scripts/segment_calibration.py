#!/usr/bin/env python3
"""Walk-forward calibration slices: all / home / away / tails."""

from __future__ import annotations

import argparse

import numpy as np

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.models.baselines import fit_logistic_baseline
from sports_ds.pipelines.nfl_win_model import FEATURE_COLS
from sports_ds.validation.splits import season_walk_forward_masks

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from calibration_report import brier_score, expected_calibration_error, log_loss


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def _metrics(y, p):
    return {
        "n": int(len(y)),
        "brier": brier_score(y, p),
        "log_loss": log_loss(y, p),
        "ece": expected_calibration_error(y, p, n_bins=10),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seasons", default="2018-2024")
    args = ap.parse_args()

    df = add_pregame_form_features(load_team_game_panel(_parse_seasons(args.seasons)))
    df = df.dropna(subset=FEATURE_COLS + ["won"])
    df = df[(df.pre_games_played >= 3) & (df.opp_pre_games_played >= 3)].copy()

    ys, ps, homes = [], [], []
    for _, tr, te in season_walk_forward_masks(df):
        _, _, pred = fit_logistic_baseline(df, FEATURE_COLS, tr, te)
        part = df.loc[te]
        ys.append(part["won"].to_numpy(dtype=float))
        ps.append(np.asarray(pred, dtype=float))
        homes.append(part["is_home"].to_numpy(dtype=float))

    y = np.concatenate(ys)
    p = np.concatenate(ps)
    h = np.concatenate(homes)

    rows = {
        "all": _metrics(y, p),
        "home": _metrics(y[h == 1], p[h == 1]),
        "away": _metrics(y[h == 0], p[h == 0]),
        "tail_low": _metrics(y[p < 0.2], p[p < 0.2]) if (p < 0.2).any() else {"n": 0},
        "tail_high": _metrics(y[p > 0.8], p[p > 0.8]) if (p > 0.8).any() else {"n": 0},
    }
    print("segment,n,brier,log_loss,ece")
    for name, m in rows.items():
        if m.get("n", 0) == 0:
            print(f"{name},0,,,")
            continue
        print(f"{name},{m['n']},{m['brier']:.4f},{m['log_loss']:.4f},{m['ece']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
