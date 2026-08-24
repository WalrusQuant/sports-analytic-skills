import pandas as pd

from sports_ds.features.player_form import (
    DEFAULT_NBA_PLAYER_FEATURE_COLS,
    NBA_STAT_COLS,
    add_pregame_player_form_features,
)
from sports_ds.pipelines.player_model import run_player_pipeline


def _nba_toy(n_players: int = 4, seasons=(2023, 2024), weeks: int = 20) -> pd.DataFrame:
    rows = []
    for season in seasons:
        for week in range(1, weeks + 1):
            day = pd.Timestamp(year=int(season), month=10, day=min(week, 28))
            for i in range(n_players):
                pid = f"p{i}"
                pts = 10 + i + (week % 5)
                rows.append(
                    {
                        "game_id": f"{season}_{week}_{i%2}",
                        "season": season,
                        "week": week,
                        "gameday": day,
                        "player_id": pid,
                        "player_name": pid,
                        "player_display_name": pid,
                        "position": ["PG", "SG", "SF", "PF"][i % 4],
                        "team": f"T{i%2}",
                        "opponent": f"T{(i+1)%2}",
                        "is_home": i % 2,
                        "minutes": 28.0,
                        "points": float(pts),
                        "rebounds": 5.0,
                        "assists": 4.0,
                        "steals": 1.0,
                        "blocks": 0.5,
                        "turnovers": 2.0,
                        "fga": 12.0,
                        "fg3a": 4.0,
                        "fta": 3.0,
                        "plus_minus": 1.0,
                        "fantasy_points": float(pts + 10),
                    }
                )
    return pd.DataFrame(rows)


def test_nba_player_form_and_pipeline():
    panel = _nba_toy()
    out = add_pregame_player_form_features(panel, stat_cols=list(NBA_STAT_COLS))
    assert pd.isna(out.sort_values(["player_id", "week"]).iloc[0]["pre_points"])
    assert "roll3_fantasy_points" in out.columns
    for c in DEFAULT_NBA_PLAYER_FEATURE_COLS:
        assert c in out.columns

    result = run_player_pipeline(
        panel,
        sport="nba",
        seasons=[2023, 2024],
        target_col="fantasy_points",
        feature_cols=list(DEFAULT_NBA_PLAYER_FEATURE_COLS),
        stat_cols=list(NBA_STAT_COLS),
        min_train_seasons=1,
        min_pre_games=2,
        min_train_rows=20,
        min_test_rows=10,
    )
    assert result["rows_modeled"] > 0
    assert result.get("mean_metrics")
    assert "ridge_mae" in result["mean_metrics"]
