#!/usr/bin/env python3
"""Print the largest errors from an out-of-sample prediction table."""

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
    parser.add_argument("--input", type=Path, required=True, help="held-out predictions in CSV, Parquet, or JSON")
    parser.add_argument("--actual-col", default="actual", help="binary outcome column")
    parser.add_argument("--prob-col", default="probability", help="predicted probability column")
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--columns", default="", help="comma-separated identifier/context columns to print")
    parser.add_argument("--filter-col", help="Optional column used to select one evaluation perspective")
    parser.add_argument("--filter-value", help="String value required in --filter-col")
    args = parser.parse_args()

    if bool(args.filter_col) != bool(args.filter_value):
        raise SystemExit("--filter-col and --filter-value must be provided together")
    frame = load_table(args.input)
    required = [args.actual_col, args.prob_col]
    required += [args.filter_col] if args.filter_col else []
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")
    numeric = frame.dropna(subset=required).copy()
    if args.filter_col:
        numeric = numeric[numeric[args.filter_col].astype(str) == args.filter_value].copy()
    if numeric.empty:
        raise SystemExit("no complete rows remain after filtering")
    numeric[args.actual_col] = numeric[args.actual_col].astype(float)
    numeric[args.prob_col] = numeric[args.prob_col].astype(float)
    if not numeric[args.actual_col].isin([0.0, 1.0]).all():
        raise SystemExit(f"{args.actual_col} must contain binary 0/1 outcomes")
    if not numeric[args.prob_col].between(0, 1).all():
        raise SystemExit(f"{args.prob_col} must contain probabilities in [0, 1]")
    numeric["absolute_error"] = (numeric[args.actual_col] - numeric[args.prob_col]).abs()
    context = [c.strip() for c in args.columns.split(",") if c.strip()]
    unknown = [column for column in context if column not in numeric.columns]
    if unknown:
        raise SystemExit(f"unknown --columns: {', '.join(unknown)}")
    output_columns = context + required + ["absolute_error"]
    print(numeric.nlargest(args.top, "absolute_error")[output_columns].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
