import pandas as pd

from sports_ds.features.player_form import (
    DEFAULT_PLAYER_FEATURE_COLS,
    add_pregame_player_form_features,
)


def test_player_form_shifted():
    df = pd.DataFrame(
        {
            "game_id": ["g1", "g2", "g3"],
            "season": [2020, 2020, 2020],
            "week": [1, 2, 3],
            "gameday": pd.to_datetime(["2020-09-01", "2020-09-08", "2020-09-15"]),
            "player_id": ["p1", "p1", "p1"],
            "player_name": ["X", "X", "X"],
            "player_display_name": ["X", "X", "X"],
            "position": ["WR", "WR", "WR"],
            "team": ["A", "A", "A"],
            "opponent": ["B", "B", "B"],
            "is_home": [1, 0, 1],
            "fantasy_points_ppr": [10.0, 20.0, 30.0],
            "fantasy_points": [8.0, 16.0, 24.0],
            "targets": [5, 8, 10],
            "receptions": [3, 5, 7],
            "receiving_yards": [40, 80, 100],
            "carries": [0, 0, 0],
            "rushing_yards": [0, 0, 0],
            "attempts": [0, 0, 0],
            "passing_yards": [0, 0, 0],
            "target_share": [0.2, 0.25, 0.3],
        }
    )
    out = add_pregame_player_form_features(df)
    assert pd.isna(out.iloc[0]["pre_fantasy_points_ppr"])
    assert out.iloc[1]["pre_fantasy_points_ppr"] == 10.0
    assert out.iloc[2]["pre_fantasy_points_ppr"] == 15.0
    assert out.iloc[2]["roll3_fantasy_points_ppr"] == 15.0
    assert out.iloc[0]["pos_WR"] == 1
    for c in DEFAULT_PLAYER_FEATURE_COLS:
        assert c in out.columns
