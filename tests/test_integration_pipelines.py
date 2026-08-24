"""Heavier integration tests for sports_ds pipelines.

These use synthetic multi-season panels so they run offline without network.
"""

from __future__ import annotations

import pandas as pd
import pytest

from sports_ds.audit.leakage import audit_pregame_form_features
from sports_ds.pipelines.team_elo import run_team_elo_baseline
from sports_ds.pipelines.team_margin import run_team_margin_pipeline
from sports_ds.pipelines.team_win import run_team_win_pipeline
from sports_ds.ratings.elo import add_elo_asof
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.validation.splits import season_walk_forward_masks


def _make_panel(seasons=(2022, 2023, 2024), weeks=12) -> pd.DataFrame:
    rows = []
    teams = ["A", "B", "C", "D"]
    gid = 0
    for season in seasons:
        for week in range(1, weeks + 1):
            # round-robin-ish pairs
            pairs = [("A", "B"), ("C", "D")] if week % 2 else [("A", "C"), ("B", "D")]
            for home, away in pairs:
                gid += 1
                # A/C slightly stronger home teams
                home_pts = 20 + (3 if home in {"A", "C"} else 0) + (week % 3)
                away_pts = 18 + (week % 2)
                rows.append(
                    {
                        "game_id": f"{season}-{gid}",
                        "season": season,
                        "week": week,
                        "gameday": pd.Timestamp(f"{season}-01-{min(week, 28):02d}"),
                        "team": home,
                        "opponent": away,
                        "is_home": 1,
                        "points_for": float(home_pts),
                        "points_against": float(away_pts),
                        "won": int(home_pts > away_pts),
                        "point_diff": float(home_pts - away_pts),
                    }
                )
                rows.append(
                    {
                        "game_id": f"{season}-{gid}",
                        "season": season,
                        "week": week,
                        "gameday": pd.Timestamp(f"{season}-01-{min(week, 28):02d}"),
                        "team": away,
                        "opponent": home,
                        "is_home": 0,
                        "points_for": float(away_pts),
                        "points_against": float(home_pts),
                        "won": int(away_pts > home_pts),
                        "point_diff": float(away_pts - home_pts),
                    }
                )
    return pd.DataFrame(rows)


def test_integration_win_pipeline_beats_or_matches_structure():
    panel = _make_panel()
    result = run_team_win_pipeline(
        panel,
        sport="toy",
        seasons=[2022, 2023, 2024],
        min_train_seasons=1,
        min_pre_games=1,
        min_train_rows=10,
        min_test_rows=10,
    )
    assert result["rows_raw_panel"] == len(panel)
    assert result["folds"], "expected at least one walk-forward fold"
    assert "mean_metrics" in result
    means = result["mean_metrics"]
    for key in (
        "constant_log_loss",
        "logistic_log_loss",
        "hist_gbm_log_loss",
        "constant_accuracy",
        "logistic_accuracy",
    ):
        assert key in means
        assert means[key] == means[key]  # not NaN
    # logistic should be finite and usually <= constant on this structured toy
    assert means["logistic_log_loss"] <= means["constant_log_loss"] + 0.05


def test_integration_margin_pipeline_structure():
    panel = _make_panel()
    result = run_team_margin_pipeline(
        panel,
        sport="toy",
        seasons=[2022, 2023, 2024],
        min_train_seasons=1,
        min_pre_games=1,
        min_train_rows=10,
        min_test_rows=10,
    )
    assert result["folds"]
    means = result["mean_metrics"]
    assert means["ridge_mae"] <= means["constant_mae"] + 1.0
    assert "beats_constant_ridge" in result


def test_integration_elo_pipeline_structure():
    panel = _make_panel()
    result = run_team_elo_baseline(
        panel,
        sport="toy",
        seasons=[2022, 2023, 2024],
        min_train_seasons=1,
        min_train_rows=10,
        min_test_rows=10,
        k=20.0,
        home_adv=30.0,
    )
    assert result["folds"]
    means = result["mean_metrics"]
    assert "elo_logistic_log_loss" in means
    assert "calibration" in result
    assert result["calibration"]["n"] > 0


def test_integration_leakage_audit_clean_on_toy():
    panel = _make_panel()
    audit = audit_pregame_form_features(panel)
    assert audit["status"] == "CLEAN"
    assert all(c["pass"] for c in audit["checks"])


def test_integration_walk_forward_masks_cover_later_seasons():
    panel = _make_panel()
    folds = list(season_walk_forward_masks(panel, min_train_seasons=1))
    seasons = [s for s, _, _ in folds]
    assert 2023 in seasons
    assert 2024 in seasons
    for _, tr, te in folds:
        assert tr.sum() > 0
        assert te.sum() > 0
        # no season overlap
        train_seasons = set(panel.loc[tr, "season"])
        test_seasons = set(panel.loc[te, "season"])
        assert train_seasons.isdisjoint(test_seasons)


def test_integration_form_and_elo_features_align_rowcount():
    panel = _make_panel()
    form = add_pregame_form_features(panel)
    elo = add_elo_asof(panel)
    assert len(form) == len(panel)
    assert len(elo) == len(panel)
    assert "feature_win_pct_diff" in form.columns
    assert "elo_diff" in elo.columns
