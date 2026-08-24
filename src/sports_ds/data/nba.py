"""NBA data loading helpers.

Primary path uses sportsdataverse when installed (`pip install -e ".[multi]"`).
Raises a clear error if the optional dependency is missing.
"""

from __future__ import annotations

import importlib
from typing import Iterable

import pandas as pd


class NbaDataError(RuntimeError):
    """Raised when NBA data cannot be loaded."""


def _require_sdv() -> None:
    try:
        import sportsdataverse  # noqa: F401
    except ImportError as e:
        raise NbaDataError(
            'sportsdataverse is required for NBA loads. Install with: pip install -e ".[multi]"'
        ) from e


def _to_pandas(obj) -> pd.DataFrame:
    if obj is None:
        return pd.DataFrame()
    if hasattr(obj, "to_pandas"):
        return obj.to_pandas()
    if isinstance(obj, pd.DataFrame):
        return obj
    return pd.DataFrame(obj)


def _as_season_list(seasons: int | Iterable[int] | None) -> list[int]:
    if seasons is None:
        return [2023, 2024]
    if isinstance(seasons, int):
        return [seasons]
    return [int(s) for s in seasons]


def load_nba_schedules(seasons: int | Iterable[int] | None = None) -> pd.DataFrame:
    """Load NBA schedules/results for seasons via sportsdataverse ESPN loaders."""
    _require_sdv()
    season_list = _as_season_list(seasons)

    frames: list[pd.DataFrame] = []
    last_err: Exception | None = None
    for season in season_list:
        loaded = False
        for mod_name, fn_name in (
            ("sportsdataverse.nba", "load_nba_schedule"),
            ("sportsdataverse.nba", "espn_nba_schedule"),
            ("sportsdataverse.nba.espn_nba_schedule", "espn_nba_schedule"),
        ):
            try:
                mod = importlib.import_module(mod_name)
                fn = getattr(mod, fn_name)
                try:
                    raw = fn(seasons=season)
                except TypeError:
                    try:
                        raw = fn(season)
                    except TypeError:
                        raw = fn()
                df = _to_pandas(raw)
                if len(df):
                    df = df.copy()
                    if "season" not in df.columns:
                        df["season"] = season
                    frames.append(df)
                    loaded = True
                    break
            except Exception as e:  # noqa: BLE001 - try next loader
                last_err = e
                continue
        if not loaded:
            continue

    if not frames:
        raise NbaDataError(
            f"could not load NBA schedules for seasons={season_list}. last_error={last_err}"
        )

    out = pd.concat(frames, ignore_index=True)
    return _normalize_nba_schedule(out)


def _normalize_nba_schedule(df: pd.DataFrame) -> pd.DataFrame:
    """Best-effort normalize heterogeneous SDV/ESPN schedule schemas."""
    colmap_candidates = {
        "game_id": ["game_id", "id", "gameId", "matchup_id"],
        "season": ["season", "season_year", "year"],
        "gameday": ["gameday", "game_date", "date", "start_date", "gameDate"],
        "home_team": ["home_team", "home_team_abbrev", "homeAbbreviation", "home_abbrev", "home"],
        "away_team": ["away_team", "away_team_abbrev", "awayAbbreviation", "away_abbrev", "away"],
        "home_score": ["home_score", "home_points", "homeScore", "home_team_score"],
        "away_score": ["away_score", "away_points", "awayScore", "away_team_score"],
    }
    rename: dict[str, str] = {}
    lower = {c.lower(): c for c in df.columns}
    for dest, opts in colmap_candidates.items():
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
        out["gameday"] = pd.to_datetime(out["gameday"], errors="coerce")
    if "season" in out.columns:
        out["season"] = pd.to_numeric(out["season"], errors="coerce").astype("Int64")
    return out


def load_nba_team_game_panel(seasons: int | Iterable[int] | None = None) -> pd.DataFrame:
    """Build an NBA team-game panel analogous to the NFL panel contract."""
    sched = load_nba_schedules(seasons)
    needed = ["game_id", "season", "home_team", "away_team", "home_score", "away_score"]
    missing = [c for c in needed if c not in sched.columns]
    if missing:
        raise NbaDataError(
            f"NBA schedule missing required columns after normalize: {missing}. "
            f"have={list(sched.columns)}"
        )

    done = sched.dropna(subset=["home_score", "away_score", "home_team", "away_team"]).copy()
    if not len(done):
        raise NbaDataError("NBA schedule has no completed games with scores")

    done["home_score"] = pd.to_numeric(done["home_score"], errors="coerce")
    done["away_score"] = pd.to_numeric(done["away_score"], errors="coerce")
    done = done.dropna(subset=["home_score", "away_score"]).copy()

    gameday = done["gameday"] if "gameday" in done.columns else pd.NaT
    if "gameday" in done.columns:
        week = pd.to_datetime(done["gameday"], errors="coerce").dt.isocalendar().week.astype(int)
    else:
        week = 0

    home = pd.DataFrame(
        {
            "game_id": done["game_id"].astype(str),
            "season": done["season"].astype(int),
            "week": week,
            "gameday": gameday,
            "team": done["home_team"].astype(str),
            "opponent": done["away_team"].astype(str),
            "is_home": 1,
            "points_for": done["home_score"].astype(float),
            "points_against": done["away_score"].astype(float),
        }
    )
    away = pd.DataFrame(
        {
            "game_id": done["game_id"].astype(str),
            "season": done["season"].astype(int),
            "week": week,
            "gameday": gameday,
            "team": done["away_team"].astype(str),
            "opponent": done["home_team"].astype(str),
            "is_home": 0,
            "points_for": done["away_score"].astype(float),
            "points_against": done["home_score"].astype(float),
        }
    )
    panel = pd.concat([home, away], ignore_index=True)
    panel["won"] = (panel["points_for"] > panel["points_against"]).astype(int)
    panel["point_diff"] = panel["points_for"] - panel["points_against"]
    panel = panel.sort_values(["season", "week", "gameday", "game_id", "team"]).reset_index(drop=True)
    return panel
