import pandas as pd

import pytest

from sports_ds.data.panel import (
    assign_season_week,
    normalize_schedule_columns,
    schedule_to_team_game_panel,
    validate_panel,
)


def test_schedule_to_panel_basic():
    sched = pd.DataFrame(
        {
            "game_id": ["1", "2"],
            "season": [2024, 2024],
            "gameday": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "home_team": ["A", "B"],
            "away_team": ["B", "A"],
            "home_score": [10, 8],
            "away_score": [7, 12],
        }
    )
    panel = schedule_to_team_game_panel(sched)
    assert len(panel) == 4
    assert set(panel.columns) >= {
        "game_id",
        "season",
        "team",
        "opponent",
        "is_home",
        "won",
        "point_diff",
    }
    home = panel[(panel.game_id == "1") & (panel.is_home == 1)].iloc[0]
    assert home.team == "A"
    assert home.won == 1
    assert home.point_diff == 3


def test_normalize_aliases():
    raw = pd.DataFrame(
        {
            "id": ["9"],
            "season_year": [2024],
            "game_date": ["2024-02-01"],
            "homeAbbreviation": ["BOS"],
            "awayAbbreviation": ["NYK"],
            "homeScore": [100],
            "awayScore": [99],
        }
    )
    out = normalize_schedule_columns(raw)
    for c in ["game_id", "season", "gameday", "home_team", "away_team", "home_score", "away_score"]:
        assert c in out.columns


def test_assign_season_week_is_chronological_across_year_wrap():
    df = pd.DataFrame(
        {
            "season": [2024, 2024],
            "gameday": pd.to_datetime(["2023-10-15", "2024-01-10"]),
        }
    )
    out = assign_season_week(df)
    assert int(out.loc[0, "week"]) == 1
    assert int(out.loc[1, "week"]) > int(out.loc[0, "week"])


def test_validate_panel_rejects_one_row_games():
    panel = pd.DataFrame(
        {
            "game_id": ["g1"],
            "season": [2024],
            "week": [1],
            "team": ["A"],
            "opponent": ["B"],
            "is_home": [1],
            "points_for": [10.0],
            "points_against": [7.0],
            "won": [1],
            "point_diff": [3.0],
        }
    )
    with pytest.raises(ValueError, match="exactly 2 team rows"):
        validate_panel(panel)
