import pandas as pd

from sports_ds.features.player_form import MLB_STAT_COLS, add_pregame_player_form_features
from sports_ds.pipelines.mlb_player_model import MLB_LEAN_FEATURE_COLS, run_mlb_player_pipeline


def _mlb_toy(n_players: int = 12, seasons=(2023, 2024), weeks: int = 40) -> pd.DataFrame:
    rows = []
    for season in seasons:
        for week in range(1, weeks + 1):
            day = pd.Timestamp(year=int(season), month=4, day=min(((week - 1) % 28) + 1, 28))
            for i in range(n_players):
                pid = f"b{i}"
                skill = 2.0 + 0.7 * i
                hits = float((week + i) % 4)
                ab = 4.0
                bb = 0.5
                hr = 1.0 if hits >= 3 else 0.0
                doubles = 1.0 if hits >= 2 else 0.0
                tb = hits + doubles + 2 * hr
                pa = ab + bb
                fp = skill + hits * 3 + 2 + 10 * hr
                rows.append(
                    {
                        "game_id": f"{season}_{week}_{i % 3}",
                        "season": season,
                        "week": week,
                        "gameday": day,
                        "player_id": pid,
                        "player_name": pid,
                        "player_display_name": pid,
                        "position": [
                            "C",
                            "1B",
                            "2B",
                            "SS",
                            "OF",
                            "DH",
                            "LF",
                            "RF",
                            "CF",
                            "3B",
                            "1B",
                            "SS",
                        ][i % 12],
                        "team": f"T{i % 2}",
                        "opponent": f"T{(i + 1) % 2}",
                        "is_home": i % 2,
                        "batting_order": (i % 9 + 1) * 100,
                        "plate_appearances": pa,
                        "at_bats": ab,
                        "hits": hits,
                        "singles": max(hits - doubles - hr, 0),
                        "total_bases": tb,
                        "home_runs": hr,
                        "doubles": doubles,
                        "triples": 0.0,
                        "walks": bb,
                        "strikeouts": 1.0,
                        "rbi": hits,
                        "runs": hits,
                        "stolen_bases": 0.0,
                        "avg": hits / ab,
                        "obp": (hits + bb) / pa,
                        "slg": tb / ab,
                        "ops": (hits + bb) / pa + tb / ab,
                        "iso": tb / ab - hits / ab,
                        "k_rate": 1.0 / pa,
                        "bb_rate": bb / pa,
                        "opp_k9": 8.0 + (i % 3),
                        "fantasy_points": fp,
                    }
                )
    return pd.DataFrame(rows)


def test_mlb_lean_features_and_form():
    panel = _mlb_toy()
    out = add_pregame_player_form_features(panel, stat_cols=list(MLB_STAT_COLS), windows=[3, 5, 10])
    assert "ewma5_fantasy_points" in out.columns
    assert "batting_order_slot" in out.columns
    assert "pre_ops" in out.columns
    for c in MLB_LEAN_FEATURE_COLS:
        assert c in out.columns, c


def test_mlb_player_pipeline_beats_constant_on_toy(monkeypatch):
    toy = _mlb_toy()

    def _fake_load(*args, **kwargs):
        return toy.copy()

    monkeypatch.setattr(
        "sports_ds.pipelines.mlb_player_model.load_mlb_player_game_panel",
        _fake_load,
    )
    result = run_mlb_player_pipeline(
        [2023, 2024],
        min_train_seasons=1,
        min_pre_games=3,
        min_train_rows=30,
        min_test_rows=15,
        max_games=100,
    )
    assert result.get("mean_metrics")
    assert result.get("beats_constant") is True
