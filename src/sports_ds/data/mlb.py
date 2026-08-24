"""MLB loaders via sportsdataverse MLB Stats API schedule."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from sports_ds.data.panel import as_season_list, schedule_to_team_game_panel, to_pandas
from sports_ds.data.sdv_common import MultiSportDataError, require_sportsdataverse


def load_mlb_schedules(seasons: int | Iterable[int] | None = None) -> pd.DataFrame:
    """Load MLB regular-season schedules/results for seasons."""
    require_sportsdataverse()
    from sportsdataverse import mlb
    from sportsdataverse.mlb import parse_mlb_api_schedule

    season_list = as_season_list(seasons, [2023, 2024])
    frames: list[pd.DataFrame] = []
    last_err: Exception | None = None
    for season in season_list:
        try:
            raw = mlb.mlb_schedule(season=int(season), sport_id=1, game_type="R")
            parsed = parse_mlb_api_schedule(raw)
            df = to_pandas(parsed)
            if not len(df):
                continue
            frames.append(df)
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            continue
    if not frames:
        raise MultiSportDataError(
            f"could not load MLB schedules for seasons={season_list}; last_error={last_err}"
        )

    df = pd.concat(frames, ignore_index=True)
    home = df.get("teams_home_team_name")
    away = df.get("teams_away_team_name")
    if home is None or away is None:
        raise MultiSportDataError(f"MLB schedule missing team name cols; have={list(df.columns)}")

    # final/completed games only when status present
    if "status_detailed_state" in df.columns:
        st = df["status_detailed_state"].astype(str).str.lower()
        df = df.loc[st.str.contains("final") | st.eq("completed")].copy()
        home = df["teams_home_team_name"]
        away = df["teams_away_team_name"]

    out = pd.DataFrame(
        {
            "game_id": df["game_pk"].astype(str),
            "season": pd.to_numeric(df["season"], errors="coerce").astype("Int64"),
            "gameday": pd.to_datetime(df.get("official_date", df.get("game_date")), errors="coerce"),
            "home_team": home.astype(str),
            "away_team": away.astype(str),
            "home_score": pd.to_numeric(df["teams_home_score"], errors="coerce"),
            "away_score": pd.to_numeric(df["teams_away_score"], errors="coerce"),
        }
    )
    out = out.dropna(subset=["game_id", "season", "home_team", "away_team", "home_score", "away_score"])
    out = out.drop_duplicates(subset=["game_id"], keep="first")
    out["week"] = out["gameday"].dt.isocalendar().week.astype("Int64")
    return out.reset_index(drop=True)


def load_mlb_team_game_panel(seasons: int | Iterable[int] | None = None) -> pd.DataFrame:
    """MLB team-game panel matching the shared panel contract."""
    return schedule_to_team_game_panel(load_mlb_schedules(seasons))
