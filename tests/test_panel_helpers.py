import pandas as pd

from sports_ds.data.panel import normalize_schedule_columns, schedule_to_team_game_panel


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
