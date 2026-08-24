import pandas as pd

from sports_ds.features.player_form import (
    DEFAULT_MLB_PLAYER_FEATURE_COLS,
    MLB_STAT_COLS,
    add_pregame_player_form_features,
)
from sports_ds.pipelines.player_model import run_player_pipeline


def _mlb_toy(n_players: int = 6, seasons=(2023, 2024), weeks: int = 25) -> pd.DataFrame:
    rows = []
    for season in seasons:
        for week in range(1, weeks + 1):
            day = pd.Timestamp(year=int(season), month=4, day=min(week, 28))
            for i in range(n_players):
                pid = f"b{i}"
                hits = float((week + i) % 4)
                rows.append(
                    {
                        "game_id": f"{season}_{week}_{i%3}",
                        "season": season,
                        "week": week,
                        "gameday": day,
                        "player_id": pid,
                        "player_name": pid,
                        "player_display_name": pid,
                        "position": ["C", "1B", "2B", "SS", "OF", "DH"][i % 6],
                        "team": f"T{i%2}",
                        "opponent": f"T{(i+1)%2}",
                        "is_home": i % 2,
                        "plate_appearances": 4.0,
                        "at_bats": 3.5,
                        "hits": hits,
                        "total_bases": hits + 1,
                        "home_runs": 0.0 if hits < 3 else 1.0,
                        "doubles": 1.0 if hits >= 2 else 0.0,
                        "triples": 0.0,
                        "walks": 0.5,
                        "strikeouts": 1.0,
                        "rbi": hits,
                        "runs": hits,
                        "stolen_bases": 0.0,
                        "fantasy_points": hits * 3 + 2,
                    }
                )
    return pd.DataFrame(rows)


def test_mlb_player_form_and_pipeline():
    panel = _mlb_toy()
    out = add_pregame_player_form_features(panel, stat_cols=list(MLB_STAT_COLS))
    assert "pre_hits" in out.columns
    assert "ewma5_fantasy_points" in out.columns
    for c in DEFAULT_MLB_PLAYER_FEATURE_COLS:
        assert c in out.columns

    result = run_player_pipeline(
        panel,
        sport="mlb",
        seasons=[2023, 2024],
        target_col="fantasy_points",
        feature_cols=list(DEFAULT_MLB_PLAYER_FEATURE_COLS),
        stat_cols=list(MLB_STAT_COLS),
        min_train_seasons=1,
        min_pre_games=3,
        min_train_rows=30,
        min_test_rows=15,
    )
    assert result.get("mean_metrics")
    assert result["mean_metrics"]["ridge_mae"] >= 0
