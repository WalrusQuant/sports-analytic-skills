#!/usr/bin/env python3
"""Write a JSON EDA report for a user-owned team-game panel."""

from __future__ import annotations

import argparse
import json
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
    parser.add_argument("--out", type=Path, required=True, help="destination JSON report")
    parser.add_argument("--season-col", default="season")
    parser.add_argument("--game-col", default="game_id")
    parser.add_argument("--team-col", default="team")
    parser.add_argument("--home-col", default="is_home")
    parser.add_argument("--outcome-col", default="won")
    args = parser.parse_args()

    panel = load_table(args.input)
    required = [args.season_col, args.game_col, args.team_col, args.home_col, args.outcome_col]
    require_columns(panel, required)
    if panel.empty:
        raise SystemExit("panel contains no rows")
    try:
        panel[args.home_col] = panel[args.home_col].astype(float)
        panel[args.outcome_col] = panel[args.outcome_col].astype(float)
    except (TypeError, ValueError) as exc:
        raise SystemExit("home and outcome columns must be numeric") from exc
    if not panel[args.home_col].dropna().isin([0.0, 1.0]).all():
        raise SystemExit(f"{args.home_col} must contain binary 0/1 values")
    if not panel[args.outcome_col].dropna().isin([0.0, 1.0]).all():
        raise SystemExit(f"{args.outcome_col} must contain binary 0/1 outcomes")
    if panel[args.outcome_col].notna().sum() == 0:
        raise SystemExit(f"{args.outcome_col} contains no observed outcomes")
    key_duplicates = int(panel.duplicated([args.game_col, args.team_col]).sum())
    home = panel[panel[args.home_col] == 1]
    game_sizes = panel.groupby(args.game_col).size()
    unpaired_games = int((game_sizes != 2).sum())
    distinct_teams = panel.groupby(args.game_col)[args.team_col].nunique(dropna=True)
    games_not_two_distinct_teams = int((distinct_teams != 2).sum())
    home_counts = panel.groupby(args.game_col)[args.home_col].sum(min_count=1)
    games_not_one_home_team = int((home_counts != 1).sum())
    key_nulls = int(panel[[args.season_col, args.game_col, args.team_col]].isna().sum().sum())
    missing_outcomes = int(panel[args.outcome_col].isna().sum())
    by_season = {}
    for season, group in panel.groupby(args.season_col, dropna=False, sort=True):
        season_home = group[group[args.home_col] == 1]
        by_season[str(season)] = {
            "rows": int(len(group)),
            "games": int(group[args.game_col].nunique()),
            "teams": int(group[args.team_col].nunique()),
            "outcome_rate": float(group[args.outcome_col].mean()),
            "home_outcome_rate": (
                float(season_home[args.outcome_col].mean()) if len(season_home) else None
            ),
            "missing_cells": int(group.isna().sum().sum()),
        }
    structural_failures = {
        "duplicate_game_team_keys": key_duplicates,
        "games_not_exactly_two_rows": unpaired_games,
        "games_not_two_distinct_teams": games_not_two_distinct_teams,
        "games_not_exactly_one_home_team": games_not_one_home_team,
        "null_natural_key_cells": key_nulls,
        "missing_home_flags": int(panel[args.home_col].isna().sum()),
    }
    status = "STOP" if any(structural_failures.values()) else "REPAIR" if missing_outcomes else "GO"
    report = {
        "source": str(args.input),
        "grain": "team-game",
        "rows": int(len(panel)),
        "columns": panel.columns.tolist(),
        "seasons": sorted(panel[args.season_col].dropna().astype(str).unique().tolist()),
        "n_games": int(panel[args.game_col].nunique()),
        "n_teams": int(panel[args.team_col].nunique()),
        "duplicate_game_team_keys": key_duplicates,
        "games_not_exactly_two_rows": unpaired_games,
        "games_not_two_distinct_teams": games_not_two_distinct_teams,
        "games_not_exactly_one_home_team": games_not_one_home_team,
        "null_natural_key_cells": key_nulls,
        "missing_home_flags": structural_failures["missing_home_flags"],
        "missing_outcomes": missing_outcomes,
        "missing_by_column": {k: int(v) for k, v in panel.isna().sum().items()},
        "outcome_rate": float(panel[args.outcome_col].mean()),
        "home_outcome_rate": float(home[args.outcome_col].mean()) if len(home) else None,
        "by_season": by_season,
        "decision": status,
        "leakage_review": "Identify columns unavailable at the prediction timestamp before modeling.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        f"rows={report['rows']} games={report['n_games']} "
        f"teams={report['n_teams']} duplicate_keys={key_duplicates}"
    )
    print(f"wrote {args.out}")
    return 2 if status == "STOP" else 1 if status == "REPAIR" else 0


if __name__ == "__main__":
    raise SystemExit(main())
