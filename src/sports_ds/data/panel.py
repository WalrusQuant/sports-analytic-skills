"""Shared team-game panel helpers."""

from __future__ import annotations

from typing import Any

import pandas as pd


REQUIRED_PANEL_COLS = [
    "game_id",
    "season",
    "week",
    "team",
    "opponent",
    "is_home",
    "points_for",
    "points_against",
    "won",
    "point_diff",
]


def to_pandas(obj: Any) -> pd.DataFrame:
    if obj is None:
        return pd.DataFrame()
    if hasattr(obj, "to_pandas"):
        return obj.to_pandas()
    if isinstance(obj, pd.DataFrame):
        return obj
    return pd.DataFrame(obj)


def as_season_list(seasons: int | list[int] | None, default: list[int]) -> list[int]:
    if seasons is None:
        return list(default)
    if isinstance(seasons, int):
        return [seasons]
    return [int(s) for s in seasons]


def normalize_schedule_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Best-effort map heterogeneous schedule schemas onto a common set."""
    candidates = {
        "game_id": ["game_id", "id", "gameId", "matchup_id", "event_id", "gamePk", "game_pk"],
        "season": ["season", "season_year", "year", "seasonYear"],
        "week": ["week", "week_number", "game_week"],
        "gameday": [
            "gameday",
            "game_date",
            "date",
            "start_date",
            "gameDate",
            "game_datetime",
            "startDate",
        ],
        "home_team": [
            "home_team",
            "home_team_abbrev",
            "homeAbbreviation",
            "home_abbrev",
            "home",
            "home_name",
            "homeTeam",
            "home_team_name",
        ],
        "away_team": [
            "away_team",
            "away_team_abbrev",
            "awayAbbreviation",
            "away_abbrev",
            "away",
            "away_name",
            "awayTeam",
            "away_team_name",
        ],
        "home_score": [
            "home_score",
            "home_points",
            "homeScore",
            "home_team_score",
            "home_goals",
            "homeGoals",
        ],
        "away_score": [
            "away_score",
            "away_points",
            "awayScore",
            "away_team_score",
            "away_goals",
            "awayGoals",
        ],
    }
    rename: dict[str, str] = {}
    lower = {str(c).lower(): c for c in df.columns}
    for dest, opts in candidates.items():
        if dest in df.columns:
            continue
        for opt in opts:
            if opt in df.columns:
                rename[opt] = dest
                break
            if opt.lower() in lower:
                rename[lower[opt.lower()]] = dest
                break
    out = df.rename(columns=rename).copy()
    if "gameday" in out.columns:
        out["gameday"] = pd.to_datetime(out["gameday"], errors="coerce", utc=False)
    if "season" in out.columns:
        out["season"] = pd.to_numeric(out["season"], errors="coerce").astype("Int64")
    return out


def assign_season_week(df: pd.DataFrame, *, date_col: str = "gameday") -> pd.DataFrame:
    """Set `week` to 1-based weeks since the earliest date in each season.

    ISO week numbers wrap at the calendar year (week 1 sorts before week 40),
    which inverts Oct–Jun NBA/NHL seasons. Use this instead of isocalendar.
    Does not overwrite an existing week column that already has values.
    """
    out = df.copy()
    if date_col not in out.columns or "season" not in out.columns:
        return out
    if "week" in out.columns and pd.to_numeric(out["week"], errors="coerce").notna().any():
        return out
    gd = pd.to_datetime(out[date_col], errors="coerce")
    start = gd.groupby(out["season"]).transform("min")
    days = (gd - start).dt.days
    week = ((days // 7) + 1).astype("Int64")
    out["week"] = week.where(gd.notna(), other=pd.NA)
    return out


def schedule_to_team_game_panel(sched: pd.DataFrame) -> pd.DataFrame:
    """Convert a normalized schedule frame into the shared team-game panel."""
    needed = ["game_id", "season", "home_team", "away_team", "home_score", "away_score"]
    missing = [c for c in needed if c not in sched.columns]
    if missing:
        raise ValueError(
            f"schedule missing required columns after normalize: {missing}; have={list(sched.columns)}"
        )

    done = sched.dropna(subset=["home_score", "away_score", "home_team", "away_team"]).copy()
    if not len(done):
        raise ValueError("schedule has no completed games with scores")

    done["home_score"] = pd.to_numeric(done["home_score"], errors="coerce")
    done["away_score"] = pd.to_numeric(done["away_score"], errors="coerce")
    done = done.dropna(subset=["home_score", "away_score"]).copy()
    done["season"] = pd.to_numeric(done["season"], errors="coerce").astype(int)
    done["game_id"] = done["game_id"].astype(str)
    done = done.drop_duplicates(subset=["game_id"], keep="first")

    if "gameday" in done.columns:
        gameday = pd.to_datetime(done["gameday"], errors="coerce")
        done["gameday"] = gameday
    else:
        gameday = pd.Series(pd.NaT, index=done.index)

    if "week" in done.columns and pd.to_numeric(done["week"], errors="coerce").notna().any():
        week = pd.to_numeric(done["week"], errors="coerce").fillna(0).astype(int)
    elif gameday.notna().any():
        assigned = assign_season_week(done)
        week = pd.to_numeric(assigned["week"], errors="coerce").fillna(0).astype(int)
    else:
        week = pd.Series(0, index=done.index, dtype=int)

    home = pd.DataFrame(
        {
            "game_id": done["game_id"].to_numpy(),
            "season": done["season"].to_numpy(),
            "week": week.to_numpy(),
            "gameday": gameday.to_numpy(),
            "team": done["home_team"].astype(str).to_numpy(),
            "opponent": done["away_team"].astype(str).to_numpy(),
            "is_home": 1,
            "points_for": done["home_score"].astype(float).to_numpy(),
            "points_against": done["away_score"].astype(float).to_numpy(),
        }
    )
    away = pd.DataFrame(
        {
            "game_id": done["game_id"].to_numpy(),
            "season": done["season"].to_numpy(),
            "week": week.to_numpy(),
            "gameday": gameday.to_numpy(),
            "team": done["away_team"].astype(str).to_numpy(),
            "opponent": done["home_team"].astype(str).to_numpy(),
            "is_home": 0,
            "points_for": done["away_score"].astype(float).to_numpy(),
            "points_against": done["home_score"].astype(float).to_numpy(),
        }
    )
    panel = pd.concat([home, away], ignore_index=True)
    panel["won"] = (panel["points_for"] > panel["points_against"]).astype(int)
    # ties (soccer/hockey OT handled upstream): count as not-win for binary target
    panel.loc[panel["points_for"] == panel["points_against"], "won"] = 0
    panel["point_diff"] = panel["points_for"] - panel["points_against"]
    sort_cols = [c for c in ["season", "gameday", "week", "game_id", "team"] if c in panel.columns]
    panel = panel.sort_values(sort_cols).reset_index(drop=True)
    validate_panel(panel)
    return panel


def validate_panel(panel: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_PANEL_COLS if c not in panel.columns]
    if missing:
        raise ValueError(f"panel missing columns: {missing}")
    if panel.duplicated(["game_id", "team"]).any():
        n_dup = int(panel.duplicated(["game_id", "team"]).sum())
        raise ValueError(f"panel has {n_dup} duplicate (game_id, team) rows")
    counts = panel.groupby("game_id").size()
    bad = counts[counts != 2]
    if len(bad):
        raise ValueError(
            f"{int(len(bad))} games do not have exactly 2 team rows "
            f"(examples: {list(bad.index[:5])})"
        )
