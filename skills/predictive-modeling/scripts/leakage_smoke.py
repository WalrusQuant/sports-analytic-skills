#!/usr/bin/env python3
"""Run fast leakage checks on a user-owned modeling table."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV, Parquet, or JSON records file")
    parser.add_argument("--target", required=True, help="Outcome column")
    parser.add_argument("--features", required=True, help="Comma-separated feature columns")
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
    if not features:
        raise SystemExit("--features must name at least one column")
    df = load_frame(args.input)
    if df.empty:
        raise SystemExit("input contains no rows to check")
    missing = [c for c in [args.target, *features] if c not in df.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")
    banned_tokens = {"target", "label", "result", "score", "won", "win", "loss", "points_for", "points_against", "point_diff"}
    named = sorted(c for c in features if c == args.target or c.lower() in banned_tokens)
    identical = []
    for col in features:
        part = df[[col, args.target]].dropna()
        if len(part) and bool((part[col] == part[args.target]).all()):
            identical.append(col)
    if named:
        print(f"FAIL: target/outcome-like feature names: {named}")
    if identical:
        print(f"FAIL: features identical to target on complete rows: {identical}")
    if named or identical:
        return 2
    print(f"OK: {len(features)} features passed name and exact-target smoke checks")
    print("manual follow-up required: verify source timestamps, joins, shifts, and fold-local transforms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
