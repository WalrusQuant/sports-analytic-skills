import pandas as pd

from sports_ds.features.team_form import RICH_WIN_FEATURE_COLS, add_pregame_form_features


def _toy_panel() -> pd.DataFrame:
    days = pd.to_datetime(["2020-09-01", "2020-09-08", "2020-09-15", "2020-09-22"])
    rows = []
    for i, day in enumerate(days):
        rows.append(
            {
                "game_id": f"g{i+1}",
                "season": 2020,
                "week": i + 1,
                "gameday": day,
                "team": "A",
                "opponent": "B",
                "is_home": 1 if i % 2 == 0 else 0,
                "points_for": 10 + i,
                "points_against": 7,
                "won": 1,
                "point_diff": 3 + i,
            }
        )
        rows.append(
            {
                "game_id": f"g{i+1}",
                "season": 2020,
                "week": i + 1,
                "gameday": day,
                "team": "B",
                "opponent": "A",
                "is_home": 0 if i % 2 == 0 else 1,
                "points_for": 7,
                "points_against": 10 + i,
                "won": 0,
                "point_diff": -(3 + i),
            }
        )
    return pd.DataFrame(rows)


def test_rich_features_exist_and_shifted():
    out = add_pregame_form_features(_toy_panel())
    a = out[out["team"] == "A"].sort_values("week")
    assert pd.isna(a.iloc[0]["pre_win_pct"])
    assert a.iloc[1]["pre_win_pct"] == 1.0
    assert "ewma5_win" in out.columns
    assert "rest_days" in out.columns
    assert "feature_ewma5_win_diff" in out.columns
    assert "feature_rest_diff" in out.columns
    # second game rest should be 7 days
    assert a.iloc[1]["rest_days"] == 7
    for c in RICH_WIN_FEATURE_COLS:
        assert c in out.columns or c == "season_week"
