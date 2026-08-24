"""End-to-end NFL team-win modeling pipeline."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

import pandas as pd

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.eda.summary import format_summary, summarize_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.models.baselines import baseline_home_rate, fit_logistic_baseline
from sports_ds.models.predict import evaluate_classifier, fit_win_classifier
from sports_ds.validation.splits import season_walk_forward_masks


FEATURE_COLS = [
    "is_home",
    "feature_win_pct_diff",
    "feature_diff_diff",
    "feature_roll3_win_diff",
    "feature_roll5_diff_diff",
    "pre_games_played",
    "opp_pre_games_played",
]


def run_nfl_win_pipeline(
    seasons: list[int] | None = None,
    min_train_seasons: int = 2,
    min_pre_games: int = 3,
) -> dict[str, Any]:
    """
    Load NFL team-game data, engineer pre-game form features, and walk-forward
    evaluate baselines + models for P(team wins).
    """
    if seasons is None:
        # solid default public window
        seasons = list(range(2018, 2025))

    panel = load_team_game_panel(seasons)
    eda = summarize_team_game_panel(panel)
    featured = add_pregame_form_features(panel)

    # require enough prior games for both sides so features are meaningful
    model_df = featured.dropna(subset=FEATURE_COLS + ["won"]).copy()
    model_df = model_df[
        (model_df["pre_games_played"] >= min_pre_games)
        & (model_df["opp_pre_games_played"] >= min_pre_games)
    ].copy()

    fold_rows: list[dict[str, Any]] = []
    for test_season, train_mask, test_mask in season_walk_forward_masks(
        model_df, min_train_seasons=min_train_seasons
    ):
        # reindex masks on model_df
        tr = train_mask
        te = test_mask
        if tr.sum() < 200 or te.sum() < 50:
            continue

        const_base = baseline_home_rate(model_df, tr, te)
        _, log_base, _ = fit_logistic_baseline(model_df, FEATURE_COLS, tr, te)
        _, gbm_res, _ = fit_win_classifier(
            model_df, FEATURE_COLS, tr, te, model_type="hist_gbm"
        )

        fold_rows.append(
            {
                "test_season": test_season,
                "n_train": int(tr.sum()),
                "n_test": int(te.sum()),
                "constant_log_loss": const_base.log_loss,
                "logistic_log_loss": log_base.log_loss,
                "hist_gbm_log_loss": gbm_res.log_loss,
                "constant_accuracy": const_base.accuracy,
                "logistic_accuracy": log_base.accuracy,
                "hist_gbm_accuracy": gbm_res.accuracy,
                "logistic_brier": log_base.brier,
                "hist_gbm_brier": gbm_res.brier,
            }
        )

    folds = pd.DataFrame(fold_rows)
    summary: dict[str, Any] = {
        "seasons_requested": seasons,
        "rows_raw_panel": int(len(panel)),
        "rows_modeled": int(len(model_df)),
        "feature_cols": FEATURE_COLS,
        "eda_text": format_summary(eda),
        "eda": eda,
        "folds": fold_rows,
    }
    if len(folds):
        summary["mean_metrics"] = {
            "constant_log_loss": float(folds["constant_log_loss"].mean()),
            "logistic_log_loss": float(folds["logistic_log_loss"].mean()),
            "hist_gbm_log_loss": float(folds["hist_gbm_log_loss"].mean()),
            "constant_accuracy": float(folds["constant_accuracy"].mean()),
            "logistic_accuracy": float(folds["logistic_accuracy"].mean()),
            "hist_gbm_accuracy": float(folds["hist_gbm_accuracy"].mean()),
        }
        # did models beat constant baseline on log loss?
        summary["beats_constant_logistic"] = bool(
            summary["mean_metrics"]["logistic_log_loss"]
            < summary["mean_metrics"]["constant_log_loss"]
        )
        summary["beats_constant_hist_gbm"] = bool(
            summary["mean_metrics"]["hist_gbm_log_loss"]
            < summary["mean_metrics"]["constant_log_loss"]
        )
    else:
        summary["mean_metrics"] = {}
        summary["warning"] = "no walk-forward folds produced; check seasons/min_train_seasons"

    return summary


def format_pipeline_report(result: dict[str, Any]) -> str:
    lines = []
    lines.append("NFL team-win model pipeline")
    lines.append(f"seasons: {result.get('seasons_requested')}")
    lines.append(f"raw panel rows: {result.get('rows_raw_panel')}")
    lines.append(f"modeled rows: {result.get('rows_modeled')}")
    lines.append("")
    lines.append(result.get("eda_text", ""))
    lines.append("")
    means = result.get("mean_metrics") or {}
    if means:
        lines.append("Walk-forward mean metrics:")
        for k, v in means.items():
            lines.append(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
        lines.append(f"logistic beats constant: {result.get('beats_constant_logistic')}")
        lines.append(f"hist_gbm beats constant: {result.get('beats_constant_hist_gbm')}")
        lines.append("")
        lines.append("Per-season folds:")
        for row in result.get("folds", []):
            lines.append(
                "  season {test_season}: const_ll={constant_log_loss:.4f} "
                "log_ll={logistic_log_loss:.4f} gbm_ll={hist_gbm_log_loss:.4f} "
                "n_test={n_test}".format(**row)
            )
    else:
        lines.append(result.get("warning", "no metrics"))
    return "\n".join(lines)
