import pandas as pd

from sports_ds.ratings.elo import build_elo_asof_table


def _tiny_panel() -> pd.DataFrame:
    # two teams, three games; home always wins by 3
    rows = []
    games = [
        ("g1", 2020, 1, "2020-09-01", "A", "B", 10, 7),
        ("g2", 2020, 2, "2020-09-08", "B", "A", 14, 10),
        ("g3", 2020, 3, "2020-09-15", "A", "B", 21, 17),
    ]
    for gid, season, week, day, home, away, hs, aws in games:
        rows.append(
            {
                "game_id": gid,
                "season": season,
                "week": week,
                "gameday": pd.Timestamp(day),
                "team": home,
                "opponent": away,
                "is_home": 1,
                "points_for": hs,
                "points_against": aws,
                "won": 1 if hs > aws else 0,
                "point_diff": hs - aws,
            }
        )
        rows.append(
            {
                "game_id": gid,
                "season": season,
                "week": week,
                "gameday": pd.Timestamp(day),
                "team": away,
                "opponent": home,
                "is_home": 0,
                "points_for": aws,
                "points_against": hs,
                "won": 1 if aws > hs else 0,
                "point_diff": aws - hs,
            }
        )
    return pd.DataFrame(rows)


def test_elo_pre_ignores_current_result():
    panel = _tiny_panel()
    elo = build_elo_asof_table(panel, k=20.0, home_adv=0.0, init=1500.0, use_margin=False)
    g1 = elo[elo["game_id"] == "g1"]
    # both teams start at init before any games
    assert (g1["elo_pre"] == 1500.0).all()
    g2_a = elo[(elo["game_id"] == "g2") & (elo["team"] == "A")].iloc[0]
    g2_b = elo[(elo["game_id"] == "g2") & (elo["team"] == "B")].iloc[0]
    # after A beat B in g1, A rating should be higher entering g2
    assert g2_a["elo_pre"] > 1500.0
    assert g2_b["elo_pre"] < 1500.0


def test_elo_row_count_matches_panel_teams():
    panel = _tiny_panel()
    elo = build_elo_asof_table(panel)
    assert len(elo) == len(panel)


def test_elo_tie_scores_half_not_away_win():
    rows = []
    games = [
        ("tie", 1, "2020-09-01", "A", "B", 1.0, 1.0),
        ("next", 2, "2020-09-08", "A", "C", 10.0, 7.0),
    ]
    for gid, week, day, home, away, hs, aws in games:
        rows.append(
            {
                "game_id": gid,
                "season": 2020,
                "week": week,
                "gameday": pd.Timestamp(day),
                "team": home,
                "opponent": away,
                "is_home": 1,
                "points_for": hs,
                "points_against": aws,
                "won": int(hs > aws),
                "point_diff": hs - aws,
            }
        )
        rows.append(
            {
                "game_id": gid,
                "season": 2020,
                "week": week,
                "gameday": pd.Timestamp(day),
                "team": away,
                "opponent": home,
                "is_home": 0,
                "points_for": aws,
                "points_against": hs,
                "won": int(aws > hs),
                "point_diff": aws - hs,
            }
        )
    panel = pd.DataFrame(rows)
    elo = build_elo_asof_table(panel, k=20.0, home_adv=0.0, init=1500.0, use_margin=False)
    tie = elo[elo["game_id"] == "tie"]
    assert set(tie["won"].tolist()) == {0}
    # A 0.5/0.5 tie with equal ratings must not move Elo; a wrong away-win
    # update would send B above 1500 entering the next game.
    next_a = elo[(elo["game_id"] == "next") & (elo["team"] == "A")].iloc[0]
    next_c = elo[(elo["game_id"] == "next") & (elo["team"] == "C")].iloc[0]
    assert next_a["elo_pre"] == 1500.0
    assert next_c["elo_pre"] == 1500.0
