"""Optional live integration for rich NFL pipelines (network + nflreadpy)."""

from __future__ import annotations

import os

import pytest

RUN = os.environ.get("SPORTS_DS_LIVE_TESTS", "").strip() in {"1", "true", "yes"}
pytestmark = pytest.mark.live


@pytest.mark.skipif(not RUN, reason="set SPORTS_DS_LIVE_TESTS=1 for live nflverse pulls")
def test_live_nfl_win_rich_smoke():
    from sports_ds.data.nfl import load_team_game_panel
    from sports_ds.pipelines.team_win_rich import run_team_win_rich_pipeline

    seasons = [2022, 2023, 2024]
    panel = load_team_game_panel(seasons)
    result = run_team_win_rich_pipeline(
        panel, sport="nfl", seasons=seasons, min_train_seasons=1, min_pre_games=3
    )
    assert result["rows_modeled"] > 100
    assert result.get("mean_metrics")
    assert "logistic_log_loss" in result["mean_metrics"]


@pytest.mark.skipif(not RUN, reason="set SPORTS_DS_LIVE_TESTS=1 for live nflverse pulls")
def test_live_nfl_player_pipeline_smoke():
    from sports_ds.pipelines.nfl_player_model import run_nfl_player_pipeline

    result = run_nfl_player_pipeline(
        [2023, 2024],
        target_col="fantasy_points_ppr",
        min_train_seasons=1,
        min_pre_games=2,
        min_train_rows=100,
        min_test_rows=50,
    )
    assert result["rows_modeled"] > 100
    assert result.get("mean_metrics")
    assert result["mean_metrics"]["ridge_mae"] < result["mean_metrics"]["constant_mae"] * 1.5
