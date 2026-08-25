#!/usr/bin/env python3
"""Load NFL schedules and export a validated two-row-per-game team panel."""

from __future__ import annotations

import argparse
from pathlib import Path


SOURCE_COLUMNS = [
    "game_id",
    "season",
    "week",
    "gameday",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
]


def parse_game_types(raw: str) -> list[str]:
    values = sorted({item.strip().upper() for item in raw.split(",") if item.strip()})
    if not values:
        raise ValueError("at least one game type is required")
    return values


def parse_seasons(raw: str) -> list[int]:
    seasons: list[int] = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            start, end = chunk.split("-", 1)
            seasons.extend(range(int(start), int(end) + 1))
        else:
            seasons.append(int(chunk))
    return sorted(set(seasons))


def require_parquet_path(parser: argparse.ArgumentParser, value: str, flag: str) -> Path:
    path = Path(value)
    if path.suffix.lower() not in {".parquet", ".pq"}:
        parser.error(f"{flag} must end in .parquet or .pq")
    return path


def build_panel(schedule, game_types: list[str] | None = None):
    try:
        import polars as pl
    except ImportError as exc:
        raise SystemExit(
            "polars is required; install it with: python -m pip install polars pyarrow"
        ) from exc

    if not isinstance(schedule, pl.DataFrame):
        try:
            schedule = pl.from_pandas(schedule)
        except Exception as exc:
            raise SystemExit("nflreadpy returned an unsupported table type") from exc
    missing = [column for column in SOURCE_COLUMNS if column not in schedule.columns]
    if missing:
        raise SystemExit(
            "schedule release is missing required columns: " + ", ".join(missing)
        )
    if schedule["game_id"].is_duplicated().any():
        raise SystemExit("raw schedule contains duplicate game_id values")
    if game_types is not None:
        if "game_type" not in schedule.columns:
            raise SystemExit(
                "schedule release is missing game_type; requested scope cannot be verified"
            )
        schedule = schedule.filter(pl.col("game_type").cast(pl.String).is_in(game_types))
        if schedule.is_empty():
            raise SystemExit("no schedule rows matched requested game types")
    if "game_type" not in schedule.columns:
        schedule = schedule.with_columns(pl.lit("unknown").alias("game_type"))

    completed = schedule.filter(
        pl.col("home_score").is_not_null() & pl.col("away_score").is_not_null()
    )
    if completed.is_empty():
        raise SystemExit("no completed games with both scores were found")
    if sum(completed.select(SOURCE_COLUMNS).null_count().row(0)):
        raise SystemExit("completed schedule rows contain null required fields")
    try:
        completed = completed.with_columns(
            pl.col("home_score").cast(pl.Float64),
            pl.col("away_score").cast(pl.Float64),
        )
    except Exception as exc:
        raise SystemExit("completed game scores must be numeric") from exc
    if not (
        completed["home_score"].is_finite().all()
        and completed["away_score"].is_finite().all()
    ):
        raise SystemExit("completed game scores must be finite")
    if ((completed["home_score"] < 0) | (completed["away_score"] < 0)).any():
        raise SystemExit("completed game scores must be non-negative")
    if (completed["home_team"] == completed["away_team"]).any():
        raise SystemExit("completed schedule contains a self-opponent game")

    common = [
        pl.col("game_id"),
        pl.col("season"),
        pl.col("week"),
        pl.col("gameday"),
        pl.col("game_type").cast(pl.String),
    ]
    home = completed.select(
        *common,
        pl.col("home_team").alias("team"),
        pl.col("away_team").alias("opponent"),
        pl.lit(1).alias("is_home"),
        pl.col("home_score").alias("points_for"),
        pl.col("away_score").alias("points_against"),
        (pl.col("home_score") > pl.col("away_score")).cast(pl.Int8).alias("won"),
        (pl.col("home_score") == pl.col("away_score")).cast(pl.Int8).alias("tied"),
        (pl.col("home_score") - pl.col("away_score"))
        .cast(pl.Float64)
        .alias("point_diff"),
    )
    away = completed.select(
        *common,
        pl.col("away_team").alias("team"),
        pl.col("home_team").alias("opponent"),
        pl.lit(0).alias("is_home"),
        pl.col("away_score").alias("points_for"),
        pl.col("home_score").alias("points_against"),
        (pl.col("away_score") > pl.col("home_score")).cast(pl.Int8).alias("won"),
        (pl.col("away_score") == pl.col("home_score")).cast(pl.Int8).alias("tied"),
        (pl.col("away_score") - pl.col("home_score"))
        .cast(pl.Float64)
        .alias("point_diff"),
    )
    panel = pl.concat([home, away]).sort(["season", "week", "game_id", "is_home"])
    counts = panel.group_by("game_id").len()
    if counts["len"].min() != 2 or counts["len"].max() != 2:
        raise SystemExit("derived panel failed the two-rows-per-game invariant")
    if (panel["team"] == panel["opponent"]).any():
        raise SystemExit("derived panel contains a self-opponent row")
    return panel


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seasons", required=True, help="e.g. 2023,2024 or 2020-2024")
    parser.add_argument(
        "--game-types",
        default="REG",
        help="comma-separated nflverse game_type values to retain (default: REG)",
    )
    parser.add_argument("--out", required=True, help="team-game Parquet output")
    parser.add_argument(
        "--raw-out", help="optional raw schedule Parquet snapshot for provenance"
    )
    parser.add_argument(
        "--force", action="store_true", help="replace existing output files"
    )
    args = parser.parse_args()

    try:
        seasons = parse_seasons(args.seasons)
    except ValueError as exc:
        parser.error(f"invalid --seasons value: {exc}")
    if not seasons:
        parser.error("--seasons must contain at least one season")
    if any(season < 1999 or season > 2100 for season in seasons):
        parser.error("--seasons contains an implausible NFL season")
    try:
        game_types = parse_game_types(args.game_types)
    except ValueError as exc:
        parser.error(f"invalid --game-types value: {exc}")
    out = require_parquet_path(parser, args.out, "--out")
    raw_out = (
        require_parquet_path(parser, args.raw_out, "--raw-out")
        if args.raw_out
        else None
    )
    if raw_out and raw_out.resolve() == out.resolve():
        parser.error("--raw-out and --out must be different files")
    for flag, path in (("--out", out), ("--raw-out", raw_out)):
        if path is not None and path.exists() and not args.force:
            parser.error(f"{flag} already exists; pass --force to replace it")

    try:
        import nflreadpy as nfl
    except ImportError as exc:
        raise SystemExit(
            "nflreadpy is required; install it with: "
            "python -m pip install nflreadpy polars pyarrow"
        ) from exc

    schedule = nfl.load_schedules(seasons)
    panel = build_panel(schedule, game_types=game_types)
    out.parent.mkdir(parents=True, exist_ok=True)
    panel.write_parquet(out)
    if raw_out:
        raw_out.parent.mkdir(parents=True, exist_ok=True)
        if hasattr(schedule, "write_parquet"):
            schedule.write_parquet(raw_out)
        else:
            schedule.to_parquet(raw_out, index=False)
    print(
        f"OK: wrote {panel.height} team-game rows "
        f"({panel['game_id'].n_unique()} games) for seasons={seasons} "
        f"game_types={game_types} -> {out}"
    )
    if raw_out:
        print(f"raw schedule -> {raw_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
