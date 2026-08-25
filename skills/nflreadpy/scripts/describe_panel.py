#!/usr/bin/env python3
"""Validate and summarize a user-owned NFL team-game panel."""

from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED = [
    "game_id",
    "season",
    "week",
    "gameday",
    "game_type",
    "team",
    "opponent",
    "is_home",
    "points_for",
    "points_against",
    "won",
    "point_diff",
    "tied",
]


def load_table(path: Path):
    try:
        import polars as pl
    except ImportError as exc:
        raise SystemExit(
            "polars is required; install it with: python -m pip install polars pyarrow"
        ) from exc
    suffix = path.suffix.lower()
    if suffix in {".parquet", ".pq"}:
        return pl.read_parquet(path)
    if suffix == ".csv":
        return pl.read_csv(path)
    if suffix == ".json":
        return pl.read_json(path)
    if suffix in {".jsonl", ".ndjson"}:
        return pl.read_ndjson(path)
    raise SystemExit("--input must be CSV, Parquet, JSON, JSONL, or NDJSON")


def summarize_panel(panel) -> dict:
    try:
        import polars as pl
    except ImportError as exc:
        raise SystemExit(
            "polars is required; install it with: python -m pip install polars pyarrow"
        ) from exc

    if not isinstance(panel, pl.DataFrame):
        raise SystemExit("panel must be a Polars DataFrame")
    missing = [column for column in REQUIRED if column not in panel.columns]
    if missing:
        raise SystemExit(f"missing required columns: {', '.join(missing)}")
    if panel.is_empty():
        raise SystemExit("panel contains no rows")
    if panel.select(["game_id", "team"]).is_duplicated().any():
        raise SystemExit("(game_id, team) must be unique")
    counts = panel.group_by("game_id").len()
    paired = bool(counts["len"].min() == 2 and counts["len"].max() == 2)
    shared = ["season", "week", "gameday", "game_type"]
    value_columns = [
        "team", "opponent", "points_for", "points_against", "point_diff", "won", "tied"
    ]
    home = panel.filter(pl.col("is_home") == 1).select(
        "game_id", *[pl.col(c).alias(f"home_{c}") for c in [*shared, *value_columns]]
    )
    away = panel.filter(pl.col("is_home") == 0).select(
        "game_id", *[pl.col(c).alias(f"away_{c}") for c in [*shared, *value_columns]]
    )
    pairs = home.join(away, on="game_id", how="inner")
    complementary = bool(
        paired
        and pairs.height == counts.height
        and all((pairs[f"home_{c}"] == pairs[f"away_{c}"]).all() for c in shared)
        and (pairs["home_team"] == pairs["away_opponent"]).all()
        and (pairs["home_opponent"] == pairs["away_team"]).all()
        and (pairs["home_points_for"] == pairs["away_points_against"]).all()
        and (pairs["home_points_against"] == pairs["away_points_for"]).all()
        and ((pairs["home_point_diff"] + pairs["away_point_diff"]).abs() < 1e-9).all()
        and (pairs["home_tied"] == pairs["away_tied"]).all()
        and (
            ((pairs["home_tied"] == 1) & (pairs["home_point_diff"].abs() < 1e-9))
            | ((pairs["home_tied"] == 0) & ((pairs["home_won"] + pairs["away_won"]) == 1))
        ).all()
    )
    row_logic = panel.select(
        (
            pl.col("is_home").is_in([0, 1])
            & ((pl.col("points_for") - pl.col("points_against") - pl.col("point_diff")).abs() < 1e-9)
            & (
                pl.col("won")
                == (pl.col("points_for") > pl.col("points_against")).cast(pl.Int8)
            )
            & pl.col("tied").is_in([0, 1])
            & (
                pl.col("tied")
                == (pl.col("points_for") == pl.col("points_against")).cast(pl.Int8)
            )
        ).fill_null(False).all().alias("valid")
    ).item()
    return {
        "rows": panel.height,
        "games": panel["game_id"].n_unique(),
        "teams": panel["team"].n_unique(),
        "seasons": sorted(panel["season"].unique().to_list()),
        "game_types": sorted(panel["game_type"].unique().to_list()),
        "two_rows_per_game": paired,
        "complementary_rows": complementary,
        "valid_row_logic": bool(row_logic),
        "missing_cells": sum(panel.null_count().row(0)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()

    panel = load_table(args.input)
    summary = summarize_panel(panel)
    print(f"source: {args.input}")
    for key, value in summary.items():
        print(f"{key}: {value}")
    valid = (
        summary["two_rows_per_game"]
        and summary["complementary_rows"]
        and summary["valid_row_logic"]
    )
    return 0 if valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
