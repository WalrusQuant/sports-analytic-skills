#!/usr/bin/env python3
"""Fit a numeric additive binomial GLM and export robust diagnostics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_table(path: Path):
    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit("This command requires pandas. Install it with: pip install pandas") from exc
    if path.suffix.lower() == ".csv": return pd.read_csv(path)
    if path.suffix.lower() in {".parquet", ".pq"}: return pd.read_parquet(path)
    if path.suffix.lower() in {".json", ".jsonl", ".ndjson"}: return pd.read_json(path, lines=path.suffix.lower() != ".json")
    raise SystemExit("--input must be CSV, Parquet, JSON, JSONL, or NDJSON")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="model frame in CSV, Parquet, or JSON")
    parser.add_argument("--formula", required=True, help="numeric additive formula, for example: won ~ is_home + rating_diff")
    parser.add_argument("--outcome-col", default="won", help="binary outcome used for validation and calibration")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    frame = load_table(args.input)
    if args.outcome_col not in frame.columns:
        raise SystemExit(f"missing required column: {args.outcome_col}")
    try:
        outcome = frame[args.outcome_col].dropna().astype(float)
    except (TypeError, ValueError) as exc:
        raise SystemExit(f"{args.outcome_col} must be numeric") from exc
    if not outcome.isin([0, 1]).all():
        raise SystemExit(f"{args.outcome_col} must contain binary 0/1 outcomes")
    try:
        import numpy as np
        from scipy.special import expit
        from scipy.stats import norm
    except ImportError as exc:
        raise SystemExit("This command requires numpy and scipy. Install them with: pip install numpy scipy") from exc
    if args.formula.count("~") != 1:
        raise SystemExit("--formula must contain exactly one ~")
    left, right = [part.strip() for part in args.formula.split("~")]
    if left != args.outcome_col:
        raise SystemExit("the formula outcome must match --outcome-col")
    if any(token in right for token in ["*", ":", "(", ")", "-"]):
        raise SystemExit("only additive numeric predictors joined by + are supported")
    predictors = [term.strip() for term in right.split("+") if term.strip() not in {"", "1"}]
    missing = [column for column in predictors if column not in frame.columns]
    if missing:
        raise SystemExit(f"missing formula columns: {', '.join(missing)}")
    if not predictors:
        raise SystemExit("formula must contain at least one predictor")
    model_rows = frame.dropna(subset=[args.outcome_col, *predictors]).copy()
    if len(model_rows) <= len(predictors) + 1:
        raise SystemExit("not enough complete rows for the requested model")
    try:
        raw_x = model_rows[predictors].to_numpy(dtype=float)
    except (TypeError, ValueError) as exc:
        raise SystemExit("all predictors must be numeric") from exc
    y = model_rows[args.outcome_col].to_numpy(dtype=float)
    if not np.isfinite(raw_x).all():
        raise SystemExit("all predictors must contain finite values")
    if not np.isfinite(y).all():
        raise SystemExit(f"{args.outcome_col} must contain finite binary outcomes")
    x = np.column_stack([np.ones(len(raw_x)), raw_x])
    names = ["Intercept", *predictors]
    beta = np.zeros(x.shape[1])
    for _ in range(100):
        probability = np.clip(expit(x @ beta), 1e-9, 1 - 1e-9)
        weights = probability * (1 - probability)
        information = x.T @ (weights[:, None] * x)
        try:
            step = np.linalg.solve(information, x.T @ (y - probability))
        except np.linalg.LinAlgError as exc:
            raise SystemExit("model information matrix is singular; remove redundant predictors") from exc
        beta += step
        if np.max(np.abs(step)) < 1e-8:
            break
    else:
        raise SystemExit("model did not converge; check separation and predictor scaling")
    probability = np.clip(expit(x @ beta), 1e-15, 1 - 1e-15)
    weights = probability * (1 - probability)
    information = x.T @ (weights[:, None] * x)
    inverse_information = np.linalg.inv(information)
    leverage = np.sum((x @ inverse_information) * x, axis=1) * weights
    adjusted_residual = (y - probability) / np.clip(1 - leverage, 1e-8, None)
    meat = x.T @ ((adjusted_residual ** 2)[:, None] * x)
    covariance = inverse_information @ meat @ inverse_information
    standard_errors = np.sqrt(np.clip(np.diag(covariance), 0, None))
    odds = {}
    for index, name in enumerate(names):
        lower, upper = beta[index] - 1.96 * standard_errors[index], beta[index] + 1.96 * standard_errors[index]
        z_value = beta[index] / standard_errors[index] if standard_errors[index] else np.nan
        odds[name] = {
            "coefficient": float(beta[index]), "standard_error_hc3": float(standard_errors[index]),
            "odds_ratio": float(np.exp(beta[index])), "ci95": [float(np.exp(lower)), float(np.exp(upper))],
            "pvalue": float(2 * norm.sf(abs(z_value))) if np.isfinite(z_value) else None,
        }
    calibration = []
    bin_index = np.minimum((probability * 10).astype(int), 9)
    for index in range(10):
        mask = bin_index == index
        if mask.any():
            calibration.append({"bin": index, "n": int(mask.sum()), "predicted": float(probability[mask].mean()), "observed": float(y[mask].mean())})
    log_likelihood = float(np.sum(y * np.log(probability) + (1 - y) * np.log(1 - probability)))
    report = {
        "source": str(args.input), "n": int(len(y)), "formula": args.formula,
        "row_accounting": {
            "input_rows": int(len(frame)),
            "complete_model_rows": int(len(model_rows)),
            "rows_dropped_missing_outcome_or_predictor": int(len(frame) - len(model_rows)),
        },
        "aic": float(2 * len(beta) - 2 * log_likelihood), "log_likelihood": log_likelihood,
        "covariance": "HC3 sandwich", "odds_ratios": odds, "calibration_bins": calibration,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"n={report['n']} aic={report['aic']:.1f} formula={args.formula}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
