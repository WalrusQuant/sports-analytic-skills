"""Optional live player-path integration tests."""

from __future__ import annotations

import os

import pytest

RUN = os.environ.get("SPORTS_DS_LIVE_TESTS", "").strip() in {"1", "true", "yes"}


@pytest.mark.skipif(not RUN, reason="set SPORTS_DS_LIVE_TESTS=1 for live pulls")
def test_live_nba_player_pipeline_smoke():
    from sports_ds.pipelines.nba_player_model import run_nba_player_pipeline

    result = run_nba_player_pipeline(
        [2023, 2024],
        min_train_seasons=1,
        min_pre_games=3,
        min_minutes=5.0,
        min_train_rows=200,
        min_test_rows=100,
    )
    assert result["rows_modeled"] > 500
    assert result.get("mean_metrics")
    assert result["mean_metrics"]["ridge_mae"] < result["mean_metrics"]["constant_mae"] * 1.2


@pytest.mark.skipif(not RUN, reason="set SPORTS_DS_LIVE_TESTS=1 for live pulls")
def test_live_mlb_player_pipeline_smoke_capped():
    from sports_ds.pipelines.mlb_player_model import run_mlb_player_pipeline

    # capped games keeps first-run API time reasonable; cache speeds repeats
    result = run_mlb_player_pipeline(
        [2024],
        min_train_seasons=1,
        min_pre_games=2,
        min_train_rows=50,
        min_test_rows=20,
        max_games=80,
    )
    # single-season may not walk-forward; at least panel path works
    assert result["rows_raw_panel"] > 50
