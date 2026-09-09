import pandas as pd

from sports_ds.data.mlb_players import _extract_opp_starter_k9, _starter_pitching_lines


def _box_rows() -> pd.DataFrame:
    # Pitcher P throws 9 K in 9 IP in game 1, then 0 K in 9 IP in game 2.
    return pd.DataFrame(
        {
            "game_id": ["g1", "g2"],
            "person_id": ["P", "P"],
            "team_side": ["home", "home"],
            "gameday": pd.to_datetime(["2024-04-01", "2024-04-08"]),
            "season": [2024, 2024],
            "stats_pitching_games_started": [1, 1],
            "stats_pitching_innings_pitched": [9.0, 9.0],
            "stats_pitching_strike_outs": [9.0, 0.0],
        }
    )


def test_starter_lines_keep_identity_and_this_game_k():
    lines = _starter_pitching_lines(_box_rows())
    assert list(lines["pitcher_id"]) == ["P", "P"]
    assert list(lines["strikeouts"]) == [9.0, 0.0]


def test_opp_k9_is_prior_start_not_current_boxscore():
    prior = _extract_opp_starter_k9(_box_rows())
    g1 = prior[prior["game_id"] == "g1"].iloc[0]
    g2 = prior[prior["game_id"] == "g2"].iloc[0]
    assert pd.isna(g1["opp_k9"])
    assert g2["opp_k9"] == 9.0
