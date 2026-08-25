#!/usr/bin/env python3
"""Summarize held-out probability errors across user-selected slices."""

from __future__ import annotations

import argparse
import json
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


def metrics(group, actual_col: str, prob_col: str) -> dict:
    import numpy as np

    actual = group[actual_col].to_numpy(dtype=float)
    probability = np.clip(group[prob_col].to_numpy(dtype=float), 1e-15, 1 - 1e-15)
    return {
        "n": int(len(group)),
        "log_loss": float(-np.mean(actual * np.log(probability) + (1 - actual) * np.log(1 - probability))),
        "brier": float(np.mean((actual - probability) ** 2)),
        "accuracy": float(((probability >= 0.5) == actual).mean()),
        "base_rate": float(actual.mean()),
        "mean_probability": float(probability.mean()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="held-out predictions in CSV, Parquet, or JSON")
    parser.add_argument("--actual-col", default="y_true")
    parser.add_argument("--prob-col", default="logistic_probability")
    parser.add_argument("--slice-cols", default="fold", help="comma-separated categorical columns")
    parser.add_argument("--filter-col", help="Optional column used to select one evaluation perspective")
    parser.add_argument("--filter-value", help="String value required in --filter-col")
    parser.add_argument("--min-n", type=int, default=20)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if args.min_n < 1:
        raise SystemExit("--min-n must be at least 1")
    if bool(args.filter_col) != bool(args.filter_value):
        raise SystemExit("--filter-col and --filter-value must be provided together")
    frame = load_table(args.input)
    slice_cols = [c.strip() for c in args.slice_cols.split(",") if c.strip()]
    required = [args.actual_col, args.prob_col, *slice_cols]
    required += [args.filter_col] if args.filter_col else []
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")
    frame = frame.dropna(subset=[args.actual_col, args.prob_col]).copy()
    if args.filter_col:
        frame = frame[frame[args.filter_col].astype(str) == args.filter_value].copy()
    if frame.empty:
        raise SystemExit("no complete rows remain after filtering")
    import pandas as pd

    for column in (args.actual_col, args.prob_col):
        converted = pd.to_numeric(frame[column], errors="coerce")
        if converted.isna().any():
            raise SystemExit(f"{column} must contain numeric values")
        frame[column] = converted.astype(float)
    if not frame[args.actual_col].isin([0.0, 1.0]).all():
        raise SystemExit(f"{args.actual_col} must contain binary 0/1 outcomes")
    import numpy as np

    if not np.isfinite(frame[args.prob_col].to_numpy()).all() or not frame[args.prob_col].between(0, 1).all():
        raise SystemExit(f"{args.prob_col} must contain finite probabilities in [0, 1]")

    rows = [{"slice_column": "all", "slice_value": "all", **metrics(frame, args.actual_col, args.prob_col)}]
    for column in slice_cols:
        for value, group in frame.groupby(column, dropna=False):
            if len(group) >= args.min_n:
                rows.append({"slice_column": column, "slice_value": str(value), **metrics(group, args.actual_col, args.prob_col)})
    report = {"source": str(args.input), "actual_column": args.actual_col, "probability_column": args.prob_col, "slices": rows}
    if args.filter_col:
        report["filter"] = {"column": args.filter_col, "value": args.filter_value}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    try:
        import pandas as pd
        print(pd.DataFrame(rows).to_string(index=False))
    except ImportError:
        pass
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
