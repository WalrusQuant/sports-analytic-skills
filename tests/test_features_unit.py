import pandas as pd

from sports_ds.features.team_form import add_pregame_form_features


def test_pregame_features_are_shifted():
    df = pd.DataFrame(
        {
            "game_id": ["g1", "g2", "g3", "g1", "g2", "g3"],
            "season": [2020, 2020, 2020, 2020, 2020, 2020],
            "week": [1, 2, 3, 1, 2, 3],
            "gameday": pd.to_datetime(["2020-09-01", "2020-09-08", "2020-09-15"] * 2),
            "team": ["A", "A", "A", "B", "B", "B"],
            "opponent": ["B", "B", "B", "A", "A", "A"],
            "is_home": [1, 0, 1, 0, 1, 0],
            "points_for": [10, 20, 30, 7, 14, 21],
            "points_against": [7, 14, 21, 10, 20, 30],
            "won": [1, 1, 1, 0, 0, 0],
            "point_diff": [3, 6, 9, -3, -6, -9],
        }
    )
    out = add_pregame_form_features(df)
    a = out[out["team"] == "A"].sort_values("week")
    # first game has no history
    assert pd.isna(a.iloc[0]["pre_win_pct"])
    # second game sees only first result
    assert a.iloc[1]["pre_win_pct"] == 1.0
    assert a.iloc[1]["pre_games_played"] == 1
