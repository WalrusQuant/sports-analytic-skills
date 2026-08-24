"""NBA player-game loading via sportsdataverse bulk player boxscores."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from sports_ds.data.panel import as_season_list, to_pandas
from sports_ds.data.sdv_common import MultiSportDataError, require_sportsdataverse


NBA_POSITIONS = {"PG", "SG", "SF", "PF", "C", "G", "F"}


def load_nba_player_boxscores(seasons: int | Iterable[int] | None = None) -> pd.DataFrame:
    """Load bulk NBA player boxscores for seasons."""
    require_sportsdataverse()
    from sportsdataverse.nba import load_nba_player_boxscore

    season_list = as_season_list(seasons, [2023, 2024])
    try:
        raw = load_nba_player_boxscore(season_list)
    except TypeError:
        frames = []
        for s in season_list:
            frames.append(to_pandas(load_nba_player_boxscore([s])))
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    df = to_pandas(raw)
    if not len(df):
        raise MultiSportDataError(f"NBA player boxscore empty for seasons={season_list}")
    return df


def load_nba_player_game_panel(
    seasons: int | Iterable[int] | None = None,
    *,
    positions: set[str] | None = None,
    season_types: tuple[int, ...] = (2,),  # 2=regular season in SDV dumps
    min_minutes: float = 1.0,
) -> pd.DataFrame:
    """
    Build NBA player-game modeling panel.

    One row per player per game with team, opponent, home flag, and counting stats.
    Default: regular season only, minutes >= 1.
    """
    raw = load_nba_player_boxscores(seasons)
    df = raw.copy()

    if "season_type" in df.columns and season_types is not None:
        df = df[df["season_type"].isin(list(season_types))].copy()

    if positions is not None and "athlete_position_abbreviation" in df.columns:
        df = df[df["athlete_position_abbreviation"].isin(positions)].copy()

    # minutes filter
    if "minutes" in df.columns:
        mins = pd.to_numeric(df["minutes"], errors="coerce").fillna(0.0)
        df = df[mins >= float(min_minutes)].copy()

    out = pd.DataFrame(
        {
            "game_id": df["game_id"].astype(str),
            "season": pd.to_numeric(df["season"], errors="coerce").astype("Int64"),
            "gameday": pd.to_datetime(df.get("game_date"), errors="coerce"),
            "player_id": df["athlete_id"].astype(str),
            "player_name": df.get("athlete_short_name", df.get("athlete_display_name")).astype(str),
            "player_display_name": df["athlete_display_name"].astype(str),
            "position": df.get("athlete_position_abbreviation", pd.Series([""] * len(df))).astype(str),
            "team": df.get("team_abbreviation", df.get("team_name")).astype(str),
            "opponent": df.get("opponent_team_abbreviation", df.get("opponent_team_name")).astype(str),
            "is_home": (df.get("home_away", "").astype(str).str.lower() == "home").astype(int),
            "minutes": pd.to_numeric(df.get("minutes"), errors="coerce").fillna(0.0),
            "points": pd.to_numeric(df.get("points"), errors="coerce").fillna(0.0),
            "rebounds": pd.to_numeric(df.get("rebounds"), errors="coerce").fillna(0.0),
            "assists": pd.to_numeric(df.get("assists"), errors="coerce").fillna(0.0),
            "steals": pd.to_numeric(df.get("steals"), errors="coerce").fillna(0.0),
            "blocks": pd.to_numeric(df.get("blocks"), errors="coerce").fillna(0.0),
            "turnovers": pd.to_numeric(df.get("turnovers"), errors="coerce").fillna(0.0),
            "fouls": pd.to_numeric(df.get("fouls"), errors="coerce").fillna(0.0),
            "fgm": pd.to_numeric(df.get("field_goals_made"), errors="coerce").fillna(0.0),
            "fga": pd.to_numeric(df.get("field_goals_attempted"), errors="coerce").fillna(0.0),
            "fg3m": pd.to_numeric(df.get("three_point_field_goals_made"), errors="coerce").fillna(0.0),
            "fg3a": pd.to_numeric(df.get("three_point_field_goals_attempted"), errors="coerce").fillna(0.0),
            "ftm": pd.to_numeric(df.get("free_throws_made"), errors="coerce").fillna(0.0),
            "fta": pd.to_numeric(df.get("free_throws_attempted"), errors="coerce").fillna(0.0),
            "plus_minus": pd.to_numeric(df.get("plus_minus"), errors="coerce").fillna(0.0),
            "starter": df.get("starter", False),
        }
    )
    out["week"] = out["gameday"].dt.isocalendar().week.astype("Int64")
    # simple fantasy-ish score (common 9-cat lite / fantasy points proxy)
    out["fantasy_points"] = (
        out["points"]
        + 1.2 * out["rebounds"]
        + 1.5 * out["assists"]
        + 3.0 * out["steals"]
        + 3.0 * out["blocks"]
        - 1.0 * out["turnovers"]
    )
    out = out.dropna(subset=["game_id", "season", "player_id", "team"])
    out = out.sort_values(["player_id", "season", "week", "gameday", "game_id"]).reset_index(drop=True)
    return out
