"""NFL data loading via nflverse/nflreadpy."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from sports_ds.data.panel import schedule_to_team_game_panel


def _to_pandas(obj):
    if hasattr(obj, "to_pandas"):
        return obj.to_pandas()
    return obj


def _as_season_list(seasons: int | Iterable[int] | None) -> list[int]:
    if seasons is None:
        import nflreadpy as nfl

        return [int(nfl.get_current_season())]
    if isinstance(seasons, int):
        return [seasons]
    return [int(s) for s in seasons]


def load_schedules(seasons: int | Iterable[int] | None = None) -> pd.DataFrame:
    """Load NFL schedules/results for one or more seasons."""
    import nflreadpy as nfl

    season_list = _as_season_list(seasons)
    df = _to_pandas(nfl.load_schedules(season_list)).copy()
    df["season"] = df["season"].astype(int)
    if "gameday" in df.columns:
        df["gameday"] = pd.to_datetime(df["gameday"], errors="coerce")
    return df


def load_team_game_panel(seasons: int | Iterable[int] | None = None) -> pd.DataFrame:
    """
    Build a team-game panel for modeling.

    One row per team per game with opponent, home flag, result, and points.
    Only completed games with non-null scores are kept.
    """
    return schedule_to_team_game_panel(load_schedules(seasons))
