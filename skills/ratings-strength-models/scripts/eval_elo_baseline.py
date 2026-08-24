#!/usr/bin/env python3
"""Evaluate an as-of Elo prediction table by season."""

from __future__ import annotations

import argparse
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
    args = parser.parse_args()

    frame = load_table(args.input)
    required = [args.season_col, args.actual_col, args.prob_col]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")
    if args.home_col in frame.columns:
        frame = frame[frame[args.home_col] == 1]
    frame = frame.dropna(subset=required).copy()
    if frame.empty:
        raise SystemExit("no scoreable rows")
    try:
        frame[args.actual_col] = frame[args.actual_col].astype(float)
        frame[args.prob_col] = frame[args.prob_col].astype(float)
    except (TypeError, ValueError) as exc:
        raise SystemExit("actual and probability columns must be numeric") from exc
    if not frame[args.actual_col].isin([0.0, 0.5, 1.0]).all():
        raise SystemExit(f"{args.actual_col} must contain 0, 0.5, or 1")
    if not frame[args.prob_col].between(0, 1).all():
        raise SystemExit(f"{args.prob_col} must contain probabilities in [0, 1]")
    import numpy as np
    import pandas as pd
    rows = []
    for season, group in frame.groupby(args.season_col):
        actual = group[args.actual_col].to_numpy(dtype=float)
        probability = np.clip(group[args.prob_col].to_numpy(dtype=float), 1e-15, 1 - 1e-15)
        decided = np.isin(actual, [0.0, 1.0])
        rows.append({
            "season": season,
            "n": len(group),
            "ties": int((~decided).sum()),
            "log_loss": -np.mean(actual * np.log(probability) + (1 - actual) * np.log(1 - probability)),
            "brier": np.mean((actual - probability) ** 2),
            "accuracy": np.mean((probability[decided] >= 0.5) == actual[decided]) if decided.any() else np.nan,
            "constant_0_5_log_loss": -np.log(0.5),
        })
    print(pd.DataFrame(rows).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
