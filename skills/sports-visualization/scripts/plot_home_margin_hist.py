#!/usr/bin/env python3
"""Plot the home-team margin distribution from a user-owned panel."""

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
    parser.add_argument("--home-col", default="is_home")
    parser.add_argument("--margin-col", default="point_diff")
    parser.add_argument("--title", default="Home-team margin distribution")
    parser.add_argument("--bins", type=int, default=40)
    args = parser.parse_args()
    panel = load_table(args.input)
    missing = [c for c in [args.home_col, args.margin_col] if c not in panel.columns]
    if missing: raise SystemExit(f"missing required columns: {', '.join(missing)}")
    try:
        panel[args.home_col] = panel[args.home_col].astype(float)
        panel[args.margin_col] = panel[args.margin_col].astype(float)
    except (TypeError, ValueError) as exc:
        raise SystemExit("home and margin columns must be numeric") from exc
    if not panel[args.home_col].dropna().isin([0.0, 1.0]).all():
        raise SystemExit(f"{args.home_col} must contain binary 0/1 values")
    home = panel.loc[panel[args.home_col] == 1, args.margin_col].dropna()
    if home.empty: raise SystemExit("no home rows with a non-missing margin")
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit("This command requires matplotlib. Install it with: pip install matplotlib") from exc
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(home, bins=args.bins, color="steelblue", edgecolor="black", alpha=0.85)
    ax.axvline(0, color="red", linestyle="--", linewidth=1.5)
    ax.set(title=f"{args.title} (n={len(home)})", xlabel=args.margin_col, ylabel="games")
    ax.grid(alpha=0.25, axis="y")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(); fig.savefig(args.out, dpi=140); plt.close(fig)
    print(f"wrote {args.out} n={len(home)} mean_margin={home.mean():.2f}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
