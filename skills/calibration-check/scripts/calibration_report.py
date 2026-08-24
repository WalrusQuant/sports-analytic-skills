#!/usr/bin/env python3
"""Walk-forward calibration report using sports_ds metrics helpers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.metrics.calibration import (
    calibration_table,
    expected_calibration_error,
    verdict_from_ece,
)
from sports_ds.metrics.classification import brier_score, log_loss_binary
from sports_ds.models.baselines import fit_logistic_baseline
from sports_ds.pipelines.nfl_win_model import FEATURE_COLS
from sports_ds.validation.splits import season_walk_forward_masks


def _parse_seasons(raw: str) -> list[int]:
    if "-" in raw and "," not in raw:
        a, b = raw.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seasons", default="2018-2024")
    ap.add_argument("--bins", type=int, default=10)
    ap.add_argument("--min-train-seasons", type=int, default=2)
    ap.add_argument("--out", default="data/calibration_report.json")
    args = ap.parse_args()

    df = add_pregame_form_features(load_team_game_panel(_parse_seasons(args.seasons)))
    df = df.dropna(subset=FEATURE_COLS + ["won"])
    df = df[(df.pre_games_played >= 3) & (df.opp_pre_games_played >= 3)].copy()

    ys, ps, per_season = [], [], []
    for season, tr, te in season_walk_forward_masks(df, min_train_seasons=args.min_train_seasons):
        _, res, pred = fit_logistic_baseline(df, FEATURE_COLS, tr, te)
        test = df.loc[te].dropna(subset=FEATURE_COLS + ["won"])
        y = test["won"].to_numpy(dtype=float)
        p = np.asarray(pred, dtype=float)
        ys.append(y)
        ps.append(p)
        per_season.append(
            {
                "season": int(season),
                "n": int(len(test)),
                "brier": brier_score(y, p),
                "log_loss": log_loss_binary(y, p),
                "ece": expected_calibration_error(y, p, n_bins=args.bins),
                "accuracy": float(res.accuracy),
            }
        )

    y_all = np.concatenate(ys) if ys else np.array([])
    p_all = np.concatenate(ps) if ps else np.array([])
    ece = expected_calibration_error(y_all, p_all, n_bins=args.bins) if len(y_all) else None
    report = {
        "model": "logistic_baseline_sports_ds_features",
        "n": int(len(y_all)),
        "bins": args.bins,
        "brier": brier_score(y_all, p_all) if len(y_all) else None,
        "log_loss": log_loss_binary(y_all, p_all) if len(y_all) else None,
        "ece": ece,
        "calibration_table": calibration_table(y_all, p_all, n_bins=args.bins) if len(y_all) else [],
        "per_season": per_season,
        "verdict": verdict_from_ece(ece, len(y_all)) if len(y_all) else "invalid-eval",
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if report["n"]:
        print(
            f"n={report['n']} brier={report['brier']:.4f} ece={report['ece']:.4f} "
            f"ll={report['log_loss']:.4f} verdict={report['verdict']}"
        )
    else:
        print("no folds")
    print(f"wrote {out}")
    return 0 if report["n"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
