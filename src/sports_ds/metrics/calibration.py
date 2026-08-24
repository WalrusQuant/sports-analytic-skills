"""Probability calibration helpers."""

from __future__ import annotations

import numpy as np


def calibration_table(y_true, y_prob, n_bins: int = 10) -> list[dict]:
    y = np.asarray(y_true, dtype=float)
    p = np.asarray(y_prob, dtype=float)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    rows: list[dict] = []
    for i in range(n_bins):
        lo, hi = float(edges[i]), float(edges[i + 1])
        if i == n_bins - 1:
            mask = (p >= lo) & (p <= hi)
        else:
            mask = (p >= lo) & (p < hi)
        n = int(mask.sum())
        if n == 0:
            rows.append(
                {
                    "bin": i,
                    "lo": lo,
                    "hi": hi,
                    "n": 0,
                    "pred_mean": None,
                    "obs_rate": None,
                    "abs_gap": None,
                }
            )
            continue
        pred_mean = float(p[mask].mean())
        obs_rate = float(y[mask].mean())
        rows.append(
            {
                "bin": i,
                "lo": lo,
                "hi": hi,
                "n": n,
                "pred_mean": pred_mean,
                "obs_rate": obs_rate,
                "abs_gap": abs(pred_mean - obs_rate),
            }
        )
    return rows


def expected_calibration_error(y_true, y_prob, n_bins: int = 10) -> float:
    table = calibration_table(y_true, y_prob, n_bins=n_bins)
    total = sum(int(r["n"]) for r in table)
    if total == 0:
        return float("nan")
    ece = 0.0
    for r in table:
        if r["n"] == 0:
            continue
        ece += (r["n"] / total) * float(r["abs_gap"])
    return float(ece)


def verdict_from_ece(ece: float, n: int) -> str:
    if n < 200:
        return "usable-with-caveats"
    if ece <= 0.03:
        return "well-calibrated"
    if ece <= 0.07:
        return "usable-with-caveats"
    return "poorly-calibrated"
