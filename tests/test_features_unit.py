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


def test_pregame_features_follow_gameday_not_iso_week():
    """Oct–Jun seasons wrap ISO week; form must not treat January as earlier than October."""
    df = pd.DataFrame(
        {
            "game_id": ["oct", "jan", "oct", "jan"],
            "season": [2024, 2024, 2024, 2024],
            "week": [43, 2, 43, 2],
            "gameday": pd.to_datetime(["2023-10-15", "2024-01-10", "2023-10-15", "2024-01-10"]),
            "team": ["A", "A", "B", "B"],
            "opponent": ["B", "B", "A", "A"],
            "is_home": [1, 0, 0, 1],
            "points_for": [5.0, 1.0, 2.0, 4.0],
            "points_against": [2.0, 4.0, 5.0, 1.0],
            "won": [1, 0, 0, 1],
            "point_diff": [3.0, -3.0, -3.0, 3.0],
        }
    )
    out = add_pregame_form_features(df)
    oct_a = out[(out["team"] == "A") & (out["game_id"] == "oct")].iloc[0]
    jan_a = out[(out["team"] == "A") & (out["game_id"] == "jan")].iloc[0]
    assert pd.isna(oct_a["pre_win_pct"])
    assert jan_a["pre_win_pct"] == 1.0
    assert jan_a["pre_games_played"] == 1
