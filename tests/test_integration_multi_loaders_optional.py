"""Optional live multi-sport loader tests.

Skip cleanly when sportsdataverse is not installed or network/data fails.
"""

from __future__ import annotations

import os

import pytest


RUN = os.environ.get("SPORTS_DS_LIVE_TESTS", "").strip() in {"1", "true", "yes"}
pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(not RUN, reason="set SPORTS_DS_LIVE_TESTS=1 for live pulls"),
]


def test_optional_nba_panel_and_win_pipeline():
    pytest.importorskip("sportsdataverse")
    from sports_ds.data.nba import load_nba_team_game_panel
    from sports_ds.pipelines.nba_win_model import run_nba_win_pipeline
    from sports_ds.audit.leakage import audit_pregame_form_features

    try:
        panel = load_nba_team_game_panel([2023, 2024])
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"nba load unavailable: {exc}")
    assert len(panel) > 1000
    assert abs(float(panel["won"].mean()) - 0.5) < 0.05
    home = panel[panel["is_home"] == 1]
    assert 0.5 < float(home["won"].mean()) < 0.7
    audit = audit_pregame_form_features(panel)
    assert audit["status"] == "CLEAN"
    result = run_nba_win_pipeline([2023, 2024], min_train_seasons=1, min_pre_games=3)
    assert result.get("folds")
    assert "mean_metrics" in result


def test_optional_mlb_panel_and_margin_pipeline():
    pytest.importorskip("sportsdataverse")
    from sports_ds.data.mlb import load_mlb_team_game_panel
    from sports_ds.pipelines.mlb_margin_model import run_mlb_margin_pipeline
    from sports_ds.pipelines.mlb_elo_baseline import run_mlb_elo_baseline

    try:
        panel = load_mlb_team_game_panel([2023, 2024])
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"mlb load unavailable: {exc}")
    assert len(panel) > 1000
    assert abs(float(panel["won"].mean()) - 0.5) < 0.05
    margin = run_mlb_margin_pipeline([2023, 2024], min_train_seasons=1, min_pre_games=5)
    assert margin.get("folds")
    elo = run_mlb_elo_baseline([2023, 2024], min_train_seasons=1)
    assert elo.get("folds")
    assert "calibration" in elo
