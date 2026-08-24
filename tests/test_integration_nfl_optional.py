"""Optional live NFL integration tests (network/cache dependent)."""

from __future__ import annotations

import os

import pytest


RUN = os.environ.get("SPORTS_DS_LIVE_TESTS", "").strip() in {"1", "true", "yes"}
pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(not RUN, reason="set SPORTS_DS_LIVE_TESTS=1 for live pulls"),
]


def test_optional_nfl_win_margin_elo_pipelines():
    try:
        from sports_ds.data.nfl import load_team_game_panel
        from sports_ds.pipelines.nfl_win_model import run_nfl_win_pipeline
        from sports_ds.pipelines.nfl_margin_model import run_nfl_margin_pipeline
        from sports_ds.pipelines.nfl_elo_baseline import run_nfl_elo_baseline
        from sports_ds.audit.leakage import audit_pregame_form_features
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"imports failed: {exc}")

    try:
        panel = load_team_game_panel([2023, 2024])
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"nfl load unavailable: {exc}")

    assert len(panel) > 500
    assert abs(float(panel["won"].mean()) - 0.5) < 0.05
    audit = audit_pregame_form_features(panel)
    assert audit["status"] == "CLEAN"

    win = run_nfl_win_pipeline([2023, 2024], min_train_seasons=1, min_pre_games=3)
    assert win.get("folds")
    assert "mean_metrics" in win

    margin = run_nfl_margin_pipeline([2023, 2024], min_train_seasons=1, min_pre_games=3)
    assert margin.get("folds")

    elo = run_nfl_elo_baseline([2023, 2024], min_train_seasons=1)
    assert elo.get("folds")
    assert "calibration" in elo
