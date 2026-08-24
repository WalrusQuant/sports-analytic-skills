"""End-to-end NFL team margin (point_diff) modeling pipeline."""

from __future__ import annotations

from typing import Any

import pandas as pd

from sports_ds.data.nfl import load_team_game_panel
from sports_ds.eda.summary import format_summary, summarize_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.models.regress import baseline_mean_margin, fit_margin_regressor
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


def run_nfl_margin_pipeline(
    seasons: list[int] | None = None,
    min_train_seasons: int = 2,
    min_pre_games: int = 3,
) -> dict[str, Any]:
    if seasons is None:
        seasons = list(range(2018, 2025))

    panel = load_team_game_panel(seasons)
    eda = summarize_team_game_panel(panel)
    featured = add_pregame_form_features(panel)
    model_df = featured.dropna(subset=FEATURE_COLS + ["point_diff"]).copy()
    model_df = model_df[
        (model_df["pre_games_played"] >= min_pre_games)
        & (model_df["opp_pre_games_played"] >= min_pre_games)
    ].copy()

    fold_rows: list[dict[str, Any]] = []
    for test_season, train_mask, test_mask in season_walk_forward_masks(
        model_df, min_train_seasons=min_train_seasons
    ):
        if train_mask.sum() < 200 or test_mask.sum() < 50:
            continue
        const = baseline_mean_margin(model_df, train_mask, test_mask)
        _, ridge, _ = fit_margin_regressor(
            model_df, FEATURE_COLS, train_mask, test_mask, model_type="ridge"
        )
        _, gbr, _ = fit_margin_regressor(
            model_df, FEATURE_COLS, train_mask, test_mask, model_type="hist_gbr"
        )
        fold_rows.append(
            {
                "test_season": test_season,
                "n_train": int(train_mask.sum()),
                "n_test": int(test_mask.sum()),
                "constant_mae": const.mae,
                "ridge_mae": ridge.mae,
                "hist_gbr_mae": gbr.mae,
                "constant_rmse": const.rmse,
                "ridge_rmse": ridge.rmse,
                "hist_gbr_rmse": gbr.rmse,
                "ridge_r2": ridge.r2,
                "hist_gbr_r2": gbr.r2,
            }
        )

    folds = pd.DataFrame(fold_rows)
    summary: dict[str, Any] = {
        "seasons_requested": seasons,
        "rows_raw_panel": int(len(panel)),
        "rows_modeled": int(len(model_df)),
        "feature_cols": FEATURE_COLS,
        "target": "point_diff",
        "eda_text": format_summary(eda),
        "folds": fold_rows,
    }
    if len(folds):
        summary["mean_metrics"] = {
            "constant_mae": float(folds["constant_mae"].mean()),
            "ridge_mae": float(folds["ridge_mae"].mean()),
            "hist_gbr_mae": float(folds["hist_gbr_mae"].mean()),
            "constant_rmse": float(folds["constant_rmse"].mean()),
            "ridge_rmse": float(folds["ridge_rmse"].mean()),
            "hist_gbr_rmse": float(folds["hist_gbr_rmse"].mean()),
        }
        summary["beats_constant_ridge"] = bool(
            summary["mean_metrics"]["ridge_mae"] < summary["mean_metrics"]["constant_mae"]
        )
        summary["beats_constant_hist_gbr"] = bool(
            summary["mean_metrics"]["hist_gbr_mae"] < summary["mean_metrics"]["constant_mae"]
        )
    else:
        summary["mean_metrics"] = {}
        summary["warning"] = "no walk-forward folds produced"
    return summary


def format_margin_report(result: dict[str, Any]) -> str:
    lines = [
        "NFL team-margin model pipeline",
        f"seasons: {result.get('seasons_requested')}",
        f"raw panel rows: {result.get('rows_raw_panel')}",
        f"modeled rows: {result.get('rows_modeled')}",
        f"target: {result.get('target')}",
        "",
        result.get("eda_text", ""),
        "",
    ]
    means = result.get("mean_metrics") or {}
    if means:
        lines.append("Walk-forward mean metrics:")
        for k, v in means.items():
            lines.append(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
        lines.append(f"ridge beats constant (MAE): {result.get('beats_constant_ridge')}")
        lines.append(f"hist_gbr beats constant (MAE): {result.get('beats_constant_hist_gbr')}")
        lines.append("")
        lines.append("Per-season folds:")
        for row in result.get("folds", []):
            lines.append(
                "  season {test_season}: const_mae={constant_mae:.3f} "
                "ridge_mae={ridge_mae:.3f} gbr_mae={hist_gbr_mae:.3f} "
                "n_test={n_test}".format(**row)
            )
    else:
        lines.append(result.get("warning", "no metrics"))
    return "\n".join(lines)
