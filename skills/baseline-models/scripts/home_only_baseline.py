#!/usr/bin/env python3
"""Estimate a home-only binary-outcome baseline from a user-owned table."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV, Parquet, or JSON records file")
    parser.add_argument("--target", default="won", help="Binary 0/1 outcome column")
    parser.add_argument("--home-col", default="is_home", help="Binary 0/1 home indicator")
    return parser.parse_args()


def load_frame(path: str):
    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit("pandas is required; install it with: python -m pip install pandas") from exc
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    if suffix in {".json", ".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=suffix != ".json")
    raise SystemExit("--input must be CSV, Parquet, JSON, JSONL, or NDJSON")


def main() -> int:
    args = parse_args()
    df = load_frame(args.input)
    missing = [c for c in (args.target, args.home_col) if c not in df.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")
    clean = df[[args.target, args.home_col]].dropna().copy()
    for col in (args.target, args.home_col):
        if not set(clean[col].unique()) <= {0, 1, False, True}:
            raise SystemExit(f"{col!r} must contain only 0/1 values")
    if clean.empty or clean[args.home_col].nunique() < 2:
        raise SystemExit("need non-empty home and away groups")
    import math

    home = clean[clean[args.home_col].astype(int) == 1][args.target].astype(int)
    away = clean[clean[args.home_col].astype(int) == 0][args.target].astype(int)
    # A 0.5 continuity correction keeps the estimate finite when a cell is zero.
    home_wins = float(home.sum()) + 0.5
    home_losses = float(len(home) - home.sum()) + 0.5
    away_wins = float(away.sum()) + 0.5
    away_losses = float(len(away) - away.sum()) + 0.5
    odds_ratio = (home_wins / home_losses) / (away_wins / away_losses)
    standard_error = math.sqrt(
        1 / home_wins + 1 / home_losses + 1 / away_wins + 1 / away_losses
    )
    log_or = math.log(odds_ratio)
    ci = [math.exp(log_or - 1.96 * standard_error), math.exp(log_or + 1.96 * standard_error)]
    print("group,n,event_rate")
    print(f"away,{len(away)},{away.mean():.6f}")
    print(f"home,{len(home)},{home.mean():.6f}")
    print(f"home odds ratio (0.5 correction): {odds_ratio:.3f} CI95=[{ci[0]:.3f}, {ci[1]:.3f}]")
    print("note: the Wald interval is descriptive; pooled inference is not walk-forward validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
