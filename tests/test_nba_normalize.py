import pandas as pd

from sports_ds.data.panel import normalize_schedule_columns


def test_normalize_maps_common_aliases():
    raw = pd.DataFrame(
        {
            "id": ["1", "2"],
            "season_year": [2024, 2024],
            "game_date": ["2024-01-01", "2024-01-02"],
            "homeAbbreviation": ["BOS", "NYK"],
            "awayAbbreviation": ["NYK", "BOS"],
            "homeScore": [110, 99],
            "awayScore": [100, 105],
        }
    )
    out = normalize_schedule_columns(raw)
    for c in ["game_id", "season", "gameday", "home_team", "away_team", "home_score", "away_score"]:
        assert c in out.columns
    assert list(out["home_team"]) == ["BOS", "NYK"]
