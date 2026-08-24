"""NFL player-game loading via nflverse/nflreadpy."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from sports_ds.data.nfl import _as_season_list, _to_pandas, load_schedules


SKILL_POSITIONS = {"QB", "RB", "WR", "TE"}


def load_player_stats(seasons: int | Iterable[int] | None = None) -> pd.DataFrame:
    """Load nflverse player weekly stats (offense/defense/special teams)."""
    import nflreadpy as nfl

    season_list = _as_season_list(seasons)
    df = _to_pandas(nfl.load_player_stats(season_list)).copy()
    if "season" in df.columns:
        df["season"] = df["season"].astype(int)
    if "week" in df.columns:
        df["week"] = pd.to_numeric(df["week"], errors="coerce")
    return df


def load_player_game_panel(
    seasons: int | Iterable[int] | None = None,
    *,
    positions: set[str] | None = None,
    season_types: tuple[str, ...] = ("REG",),
    min_targets_or_carries_or_attempts: int | None = None,
) -> pd.DataFrame:
    """
    Build a player-game modeling panel.

    One row per player per game with team, opponent, home flag, and core counting stats.
    Regular season by default.
    """
    if positions is None:
        positions = set(SKILL_POSITIONS)

    stats = load_player_stats(seasons)
    if "season_type" in stats.columns:
        stats = stats[stats["season_type"].isin(season_types)].copy()
    if "position" in stats.columns:
        stats = stats[stats["position"].isin(positions)].copy()

    # normalize team column
    if "team" not in stats.columns:
        raise ValueError("player stats missing team column")

    sched = load_schedules(seasons)
    sched_cols = ["game_id", "season", "week", "gameday", "home_team", "away_team"]
    missing = [c for c in sched_cols if c not in sched.columns]
    if missing:
        raise ValueError(f"schedule missing columns: {missing}")
    s = sched[sched_cols].drop_duplicates("game_id").copy()
    if "gameday" in s.columns:
        s["gameday"] = pd.to_datetime(s["gameday"], errors="coerce")

    df = stats.merge(s, on=["game_id", "season", "week"], how="left", suffixes=("", "_sched"))
    # home flag from schedule
    df["is_home"] = (df["team"] == df["home_team"]).astype(int)
    # opponent if missing
    if "opponent_team" in df.columns:
        df["opponent"] = df["opponent_team"]
    else:
        df["opponent"] = df.apply(
            lambda r: r["away_team"] if r["is_home"] == 1 else r["home_team"], axis=1
        )

    # core numeric targets
    for c in [
        "completions",
        "attempts",
        "passing_yards",
        "passing_tds",
        "interceptions",
        "carries",
        "rushing_yards",
        "rushing_tds",
        "receptions",
        "targets",
        "receiving_yards",
        "receiving_tds",
        "fantasy_points",
        "fantasy_points_ppr",
        "target_share",
        "air_yards_share",
        "passing_epa",
        "rushing_epa",
        "receiving_epa",
    ]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

    if min_targets_or_carries_or_attempts is not None:
        thr = int(min_targets_or_carries_or_attempts)
        usage = (
            df.get("targets", 0).fillna(0)
            + df.get("carries", 0).fillna(0)
            + df.get("attempts", 0).fillna(0)
        )
        df = df[usage >= thr].copy()

    keep = [
        "game_id",
        "season",
        "week",
        "gameday",
        "player_id",
        "player_name",
        "player_display_name",
        "position",
        "position_group",
        "team",
        "opponent",
        "is_home",
        "attempts",
        "completions",
        "passing_yards",
        "passing_tds",
        "interceptions",
        "carries",
        "rushing_yards",
        "rushing_tds",
        "targets",
        "receptions",
        "receiving_yards",
        "receiving_tds",
        "fantasy_points",
        "fantasy_points_ppr",
        "target_share",
        "air_yards_share",
        "passing_epa",
        "rushing_epa",
        "receiving_epa",
    ]
    keep = [c for c in keep if c in df.columns]
    out = df[keep].sort_values(["player_id", "season", "week", "gameday", "game_id"]).reset_index(drop=True)
    return out
