#!/usr/bin/env python3
"""Preview candidate features and their missingness in a user-owned table."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV, Parquet, or JSON records file")
    parser.add_argument("--features", required=True, help="Comma-separated candidate feature columns")
    parser.add_argument("--context", default="", help="Comma-separated identifier/time columns to display")
    parser.add_argument("--rows", type=int, default=8)
    return parser.parse_args()


def load_frame(path: str):
    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit("pandas is required; install it with: python -m pip install pandas") from exc
    suffix = Path(path).suffix.lower()
    if suffix == ".csv": return pd.read_csv(path)
    if suffix in {".parquet", ".pq"}: return pd.read_parquet(path)
    if suffix in {".json", ".jsonl", ".ndjson"}: return pd.read_json(path, lines=suffix != ".json")
    raise SystemExit("--input must be CSV, Parquet, JSON, JSONL, or NDJSON")


def main() -> int:
    args = parse_args()
    features = [c.strip() for c in args.features.split(",") if c.strip()]
    context = [c.strip() for c in args.context.split(",") if c.strip()]
    if not features:
        raise SystemExit("--features must name at least one column")
    df = load_frame(args.input)
    missing = [c for c in [*context, *features] if c not in df.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")
    print(f"rows: {len(df)}")
    print("feature,null_rate,dtype,unique")
    for col in features:
        print(f"{col},{df[col].isna().mean():.6f},{df[col].dtype},{df[col].nunique(dropna=True)}")
    print("\npreview:")
    print(df[[*context, *features]].head(max(args.rows, 0)).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
