import pandas as pd

from sports_ds.audit.leakage import audit_pregame_form_features


def test_audit_clean_on_shifted_features():
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
    result = audit_pregame_form_features(df)
    assert result["status"] == "CLEAN"
    assert all(c["pass"] for c in result["checks"])
