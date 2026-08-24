#!/usr/bin/env python3
"""Plot home win rate by season from a user-owned team-game panel."""

from __future__ import annotations

import argparse
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
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--season-col", default="season")
    parser.add_argument("--home-col", default="is_home")
    parser.add_argument("--outcome-col", default="won")
    parser.add_argument("--title", default="Home win rate by season")
    args = parser.parse_args()
    panel = load_table(args.input)
    required = [args.season_col, args.home_col, args.outcome_col]
    missing = [c for c in required if c not in panel.columns]
    if missing: raise SystemExit(f"missing required columns: {', '.join(missing)}")
    try:
        panel[args.home_col] = panel[args.home_col].astype(float)
        panel[args.outcome_col] = panel[args.outcome_col].astype(float)
    except (TypeError, ValueError) as exc:
        raise SystemExit("home and outcome columns must be numeric") from exc
    if not panel[args.home_col].dropna().isin([0.0, 1.0]).all():
        raise SystemExit(f"{args.home_col} must contain binary 0/1 values")
    if not panel[args.outcome_col].dropna().isin([0.0, 1.0]).all():
        raise SystemExit(f"{args.outcome_col} must contain binary 0/1 outcomes")
    home = panel[panel[args.home_col] == 1]
    rates = home.groupby(args.season_col)[args.outcome_col].mean().sort_index()
    if rates.empty: raise SystemExit("no home rows found")
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit("This command requires matplotlib. Install it with: pip install matplotlib") from exc
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(rates.index.astype(str), rates.values, color="steelblue", edgecolor="black")
    ax.axhline(0.5, color="red", linestyle="--", linewidth=1)
    ax.set(title=f"{args.title} (n={len(home)})", xlabel=args.season_col, ylabel="home win rate")
    ax.grid(alpha=0.25, axis="y")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(); fig.savefig(args.out, dpi=140); plt.close(fig)
    print(rates.to_string()); print(f"wrote {args.out}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
