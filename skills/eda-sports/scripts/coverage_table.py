#!/usr/bin/env python3
"""Print season-by-period coverage from a user-owned sports panel."""

from __future__ import annotations

import argparse
from pathlib import Path


def load_table(path: Path):
    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit("This command requires pandas. Install it with: pip install pandas") from exc
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    if suffix in {".json", ".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=suffix != ".json")
    raise SystemExit("--input must be CSV, Parquet, JSON, JSONL, or NDJSON")


def require_columns(frame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="CSV, Parquet, or JSON team-game panel")
    parser.add_argument("--season-col", default="season")
    parser.add_argument("--period-col", default="week", help="week, round, date bucket, or other period column")
    parser.add_argument("--game-col", default="game_id")
    parser.add_argument("--team-col", default="team")
    args = parser.parse_args()

    panel = load_table(args.input)
    require_columns(panel, [args.season_col, args.period_col, args.game_col, args.team_col])
    coverage = (
        panel.groupby([args.season_col, args.period_col], as_index=False)
        .agg(rows=(args.game_col, "size"), games=(args.game_col, "nunique"), teams=(args.team_col, "nunique"))
        .sort_values([args.season_col, args.period_col])
    )
    print(coverage.to_string(index=False))
    print(f"\nrows={len(panel)} games={panel[args.game_col].nunique()} teams={panel[args.team_col].nunique()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
