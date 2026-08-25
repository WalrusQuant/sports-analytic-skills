#!/usr/bin/env python3
"""Evaluate an as-of Elo prediction table by season."""

from __future__ import annotations

import argparse
import math
from pathlib import Path


def load_table(path: Path):
    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit("This command requires pandas. Install it with: pip install pandas") from exc
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    if path.suffix.lower() in {".json", ".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=path.suffix.lower() != ".json")
    raise SystemExit("--input must be CSV, Parquet, JSON, JSONL, or NDJSON")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="as-of predictions in CSV, Parquet, or JSON")
    parser.add_argument("--season-col", default="season")
    parser.add_argument("--actual-col", default="actual")
    parser.add_argument("--prob-col", default="win_probability")
    parser.add_argument("--home-col", default="is_home", help="when present, only home rows are scored")
    parser.add_argument(
        "--baseline-prob-col",
        help="Optional matched pre-event baseline probability column to score",
    )
    args = parser.parse_args()

    frame = load_table(args.input)
    import pandas as pd

    required = [args.season_col, args.actual_col, args.prob_col, args.home_col]
    required += [args.baseline_prob_col] if args.baseline_prob_col else []
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")
    home = pd.to_numeric(frame[args.home_col], errors="coerce")
    invalid_home = frame[args.home_col].notna() & home.isna()
    if home.isna().any() or invalid_home.any() or not set(home.unique()) <= {0, 1}:
        raise SystemExit(f"{args.home_col!r} must contain non-null 0/1 values")
    frame = frame[home == 1]
    frame = frame.dropna(subset=required).copy()
    if frame.empty:
        raise SystemExit("no scoreable rows")
    try:
        frame[args.actual_col] = frame[args.actual_col].astype(float)
        probability_columns = [args.prob_col]
        probability_columns += [args.baseline_prob_col] if args.baseline_prob_col else []
        for column in probability_columns:
            frame[column] = frame[column].astype(float)
    except (TypeError, ValueError) as exc:
        raise SystemExit("actual and probability columns must be numeric") from exc
    if not frame[args.actual_col].isin([0.0, 0.5, 1.0]).all():
        raise SystemExit(f"{args.actual_col} must contain 0, 0.5, or 1")
    for column in probability_columns:
        if not frame[column].map(math.isfinite).all() or not frame[column].between(0, 1).all():
            raise SystemExit(f"{column} must contain finite probabilities in [0, 1]")
    import numpy as np

    unique_seasons = frame[args.season_col].drop_duplicates()
    numeric_order = pd.to_numeric(unique_seasons, errors="coerce")
    if numeric_order.notna().all():
        season_order = numeric_order
    else:
        season_order = pd.to_datetime(unique_seasons, errors="coerce", utc=True, format="mixed")
        if season_order.isna().any():
            raise SystemExit(f"{args.season_col!r} must contain sortable numeric or date values")
    ordered = pd.DataFrame({"season": unique_seasons.to_list(), "order": season_order.to_list()})
    if ordered["order"].duplicated().any():
        raise SystemExit(f"{args.season_col!r} has ambiguous season ordering")
    seasons = ordered.sort_values("order", kind="stable")["season"].to_list()

    def score(actual, probability) -> float:
        clipped = np.clip(probability, 1e-15, 1 - 1e-15)
        return float(-np.mean(actual * np.log(clipped) + (1 - actual) * np.log(1 - clipped)))

    rows = []
    for index, season in enumerate(seasons):
        group = frame[frame[args.season_col] == season]
        actual = group[args.actual_col].to_numpy(dtype=float)
        probability = group[args.prob_col].to_numpy(dtype=float)
        decided = np.isin(actual, [0.0, 1.0])
        row = {
            "season": season,
            "n": len(group),
            "ties": int((~decided).sum()),
            "elo_log_loss": score(actual, probability),
            "brier": np.mean((actual - probability) ** 2),
            "accuracy": np.mean((probability[decided] >= 0.5) == actual[decided]) if decided.any() else np.nan,
            "constant_0_5_log_loss": -np.log(0.5),
        }
        prior = frame[frame[args.season_col].isin(seasons[:index])]
        if prior.empty:
            row["prior_season_home_rate_log_loss"] = np.nan
        else:
            prior_rate = float(prior[args.actual_col].mean())
            row["prior_season_home_rate_log_loss"] = score(
                actual, np.full(len(group), prior_rate)
            )
        if args.baseline_prob_col:
            row["supplied_baseline_log_loss"] = score(
                actual, group[args.baseline_prob_col].to_numpy(dtype=float)
            )
        rows.append(row)
    print(pd.DataFrame(rows).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
