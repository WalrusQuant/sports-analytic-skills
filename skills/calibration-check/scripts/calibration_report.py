#!/usr/bin/env python3
"""Walk-forward calibration report for sports_ds NFL win features."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

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


def brier_score(y: np.ndarray, p: np.ndarray) -> float:
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    return float(np.mean((p - y) ** 2))


def log_loss(y: np.ndarray, p: np.ndarray, eps: float = 1e-15) -> float:
    y = np.asarray(y, dtype=float)
    p = np.clip(np.asarray(p, dtype=float), eps, 1 - eps)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def calibration_table(y: np.ndarray, p: np.ndarray, n_bins: int = 10) -> list[dict]:
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    rows = []
    for i in range(n_bins):
        lo, hi = edges[i], edges[i + 1]
        if i == n_bins - 1:
            mask = (p >= lo) & (p <= hi)
        else:
            mask = (p >= lo) & (p < hi)
        n = int(mask.sum())
        if n == 0:
            rows.append({"bin": i, "lo": float(lo), "hi": float(hi), "n": 0, "pred_mean": None, "obs_rate": None, "abs_gap": None})
            continue
        pred_mean = float(p[mask].mean())
        obs_rate = float(y[mask].mean())
        rows.append(
            {
                "bin": i,
                "lo": float(lo),
                "hi": float(hi),
                "n": n,
                "pred_mean": pred_mean,
                "obs_rate": obs_rate,
                "abs_gap": abs(pred_mean - obs_rate),
            }
        )
    return rows


def expected_calibration_error(y: np.ndarray, p: np.ndarray, n_bins: int = 10) -> float:
    table = calibration_table(y, p, n_bins=n_bins)
    total = sum(r["n"] for r in table)
    if total == 0:
        return float("nan")
    ece = 0.0
    for r in table:
        if r["n"] == 0:
            continue
        ece += (r["n"] / total) * r["abs_gap"]
    return float(ece)


def verdict(ece: float, n: int) -> str:
    if n < 200:
        return "usable-with-caveats"
    if ece <= 0.03:
        return "well-calibrated"
    if ece <= 0.07:
        return "usable-with-caveats"
    return "poorly-calibrated"


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

    ys = []
    ps = []
    per_season = []
    for season, tr, te in season_walk_forward_masks(df, min_train_seasons=args.min_train_seasons):
        _, res, pred = fit_logistic_baseline(df, FEATURE_COLS, tr, te)
        y = df.loc[te, "won"].to_numpy(dtype=float)
        p = np.asarray(pred, dtype=float)
        ys.append(y)
        ps.append(p)
        per_season.append(
            {
                "season": int(season),
                "n": int(te.sum()),
                "brier": brier_score(y, p),
                "log_loss": log_loss(y, p),
                "ece": expected_calibration_error(y, p, n_bins=args.bins),
                "accuracy": float(res.accuracy),
            }
        )

    y_all = np.concatenate(ys) if ys else np.array([])
    p_all = np.concatenate(ps) if ps else np.array([])
    report = {
        "model": "logistic_baseline_sports_ds_features",
        "n": int(len(y_all)),
        "bins": args.bins,
        "brier": brier_score(y_all, p_all) if len(y_all) else None,
        "log_loss": log_loss(y_all, p_all) if len(y_all) else None,
        "ece": expected_calibration_error(y_all, p_all, n_bins=args.bins) if len(y_all) else None,
        "calibration_table": calibration_table(y_all, p_all, n_bins=args.bins) if len(y_all) else [],
        "per_season": per_season,
        "verdict": verdict(expected_calibration_error(y_all, p_all, n_bins=args.bins), len(y_all)) if len(y_all) else "invalid-eval",
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"n={report['n']} brier={report['brier']:.4f} ece={report['ece']:.4f} ll={report['log_loss']:.4f} verdict={report['verdict']}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
