"""NFL data loading via nflverse/nflreadpy."""

from __future__ import annotations

from typing import Iterable

import pandas as pd


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
    sched = load_schedules(seasons)
    needed = ["game_id", "season", "week", "gameday", "home_team", "away_team", "home_score", "away_score"]
    missing = [c for c in needed if c not in sched.columns]
    if missing:
        raise ValueError(f"schedule missing columns: {missing}")

    done = sched.dropna(subset=["home_score", "away_score"]).copy()
    done["home_score"] = done["home_score"].astype(float)
    done["away_score"] = done["away_score"].astype(float)

    home = pd.DataFrame(
        {
            "game_id": done["game_id"],
            "season": done["season"],
            "week": done["week"],
            "gameday": done["gameday"],
            "team": done["home_team"],
            "opponent": done["away_team"],
            "is_home": 1,
            "points_for": done["home_score"],
            "points_against": done["away_score"],
        }
    )
    away = pd.DataFrame(
        {
            "game_id": done["game_id"],
            "season": done["season"],
            "week": done["week"],
            "gameday": done["gameday"],
            "team": done["away_team"],
            "opponent": done["home_team"],
            "is_home": 0,
            "points_for": done["away_score"],
            "points_against": done["home_score"],
        }
    )
    panel = pd.concat([home, away], ignore_index=True)
    panel["won"] = (panel["points_for"] > panel["points_against"]).astype(int)
    panel["point_diff"] = panel["points_for"] - panel["points_against"]
    panel = panel.sort_values(["season", "week", "gameday", "game_id", "team"]).reset_index(drop=True)
    return panel
