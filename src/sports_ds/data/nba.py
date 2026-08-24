"""NBA loaders via sportsdataverse bulk schedule releases."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from sports_ds.data.panel import as_season_list, schedule_to_team_game_panel, to_pandas
from sports_ds.data.sdv_common import MultiSportDataError, require_sportsdataverse


def load_nba_schedules(seasons: int | Iterable[int] | None = None) -> pd.DataFrame:
    """Load NBA schedules/results for seasons via sportsdataverse.load_nba_schedule."""
    require_sportsdataverse()
    from sportsdataverse.nba import load_nba_schedule

    season_list = as_season_list(seasons, [2023, 2024])
    try:
        raw = load_nba_schedule(season_list, return_as_pandas=True)
    except TypeError:
        raw = load_nba_schedule(season_list)
    df = to_pandas(raw)
    if not len(df):
        raise MultiSportDataError(f"NBA schedule empty for seasons={season_list}")

    # completed games only when status available
    if "status_type_completed" in df.columns:
        done = df["status_type_completed"]
        if done.dtype == bool or str(done.dtype).startswith("bool"):
            df = df.loc[done.fillna(False)].copy()
        else:
            df = df.loc[done.astype(str).str.lower().isin(["true", "1", "yes"])].copy()

    out = pd.DataFrame(
        {
            "game_id": df.get("game_id", df.get("id")).astype(str),
            "season": pd.to_numeric(df["season"], errors="coerce").astype("Int64"),
            "gameday": pd.to_datetime(df.get("game_date", df.get("date")), errors="coerce"),
            "home_team": df["home_abbreviation"].astype(str),
            "away_team": df["away_abbreviation"].astype(str),
            "home_score": pd.to_numeric(df["home_score"], errors="coerce"),
            "away_score": pd.to_numeric(df["away_score"], errors="coerce"),
        }
    )
    out = out.dropna(subset=["game_id", "season", "home_team", "away_team", "home_score", "away_score"])
    out = out.drop_duplicates(subset=["game_id"], keep="first")
    out["week"] = out["gameday"].dt.isocalendar().week.astype("Int64")
    return out.reset_index(drop=True)


def load_nba_team_game_panel(seasons: int | Iterable[int] | None = None) -> pd.DataFrame:
    """NBA team-game panel matching the shared panel contract."""
    return schedule_to_team_game_panel(load_nba_schedules(seasons))
