"""NFL player-level walk-forward regression (fantasy points / volume targets)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from sports_ds.data.nfl_players import load_player_game_panel
from sports_ds.features.player_form import (
    DEFAULT_PLAYER_FEATURE_COLS,
    PLAYER_TARGET_DEFAULT,
    add_pregame_player_form_features,
)
from sports_ds.models.regress import baseline_mean_margin, fit_margin_regressor
from sports_ds.validation.splits import season_walk_forward_masks


def run_nfl_player_pipeline(
    seasons: list[int],
    *,
    target_col: str = PLAYER_TARGET_DEFAULT,
    positions: set[str] | None = None,
    min_train_seasons: int = 1,
    min_pre_games: int = 3,
    min_train_rows: int = 200,
    min_test_rows: int = 100,
    feature_cols: list[str] | None = None,
) -> dict[str, Any]:
    panel = load_player_game_panel(seasons, positions=positions)
    featured = add_pregame_player_form_features(panel)
    use_cols = [c for c in (feature_cols or DEFAULT_PLAYER_FEATURE_COLS) if c in featured.columns]
    need = use_cols + [target_col]
    model_df = featured.dropna(subset=need).copy()
    model_df = model_df[model_df["pre_games_played"] >= min_pre_games].copy()

    fold_rows: list[dict[str, Any]] = []
    for test_season, train_mask, test_mask in season_walk_forward_masks(
        model_df, min_train_seasons=min_train_seasons
    ):
        if int(train_mask.sum()) < min_train_rows or int(test_mask.sum()) < min_test_rows:
            continue
        const = baseline_mean_margin(model_df, train_mask, test_mask, target_col=target_col)
        _, ridge, _ = fit_margin_regressor(
            model_df,
            use_cols,
            train_mask,
            test_mask,
            target_col=target_col,
            model_type="ridge",
        )
        _, gbr, _ = fit_margin_regressor(
            model_df,
            use_cols,
            train_mask,
            test_mask,
            target_col=target_col,
            model_type="hist_gbr",
        )
        fold_rows.append(
            {
                "test_season": int(test_season),
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
    out: dict[str, Any] = {
        "sport": "nfl",
        "pipeline": "nfl_player",
        "target": target_col,
        "seasons_requested": seasons,
        "rows_raw_panel": int(len(panel)),
        "rows_modeled": int(len(model_df)),
        "feature_cols": use_cols,
        "positions": sorted(positions) if positions else ["QB", "RB", "WR", "TE"],
        "folds": fold_rows,
    }
    if len(folds):
        out["mean_metrics"] = {
            "constant_mae": float(folds["constant_mae"].mean()),
            "ridge_mae": float(folds["ridge_mae"].mean()),
            "hist_gbr_mae": float(folds["hist_gbr_mae"].mean()),
            "constant_rmse": float(folds["constant_rmse"].mean()),
            "ridge_rmse": float(folds["ridge_rmse"].mean()),
            "hist_gbr_rmse": float(folds["hist_gbr_rmse"].mean()),
        }
        out["beats_constant_ridge"] = bool(
            out["mean_metrics"]["ridge_mae"] < out["mean_metrics"]["constant_mae"]
        )
        out["beats_constant_hist_gbr"] = bool(
            out["mean_metrics"]["hist_gbr_mae"] < out["mean_metrics"]["constant_mae"]
        )
        out["best_model"] = min(
            (
                ("ridge", out["mean_metrics"]["ridge_mae"]),
                ("hist_gbr", out["mean_metrics"]["hist_gbr_mae"]),
            ),
            key=lambda x: x[1],
        )[0]
    else:
        out["mean_metrics"] = {}
        out["warning"] = "no walk-forward folds produced"
    return out


def format_nfl_player_report(result: dict[str, Any]) -> str:
    lines = [
        "NFL player pipeline",
        f"target: {result.get('target')}",
        f"positions: {result.get('positions')}",
        f"seasons: {result.get('seasons_requested')}",
        f"raw rows: {result.get('rows_raw_panel')}",
        f"modeled rows: {result.get('rows_modeled')}",
        f"features: {result.get('feature_cols')}",
        "",
    ]
    means = result.get("mean_metrics") or {}
    if means:
        lines.append("Walk-forward mean metrics:")
        for k, v in means.items():
            lines.append(f"  {k}: {v:.4f}")
        lines.append(f"best_model: {result.get('best_model')}")
        lines.append(f"ridge beats constant: {result.get('beats_constant_ridge')}")
        lines.append(f"hist_gbr beats constant: {result.get('beats_constant_hist_gbr')}")
        lines.append("")
        lines.append("Per-season folds:")
        for row in result.get("folds", []):
            lines.append(
                "  season {test_season}: const_mae={constant_mae:.3f} "
                "ridge_mae={ridge_mae:.3f} gbr_mae={hist_gbr_mae:.3f} n_test={n_test}".format(**row)
            )
    else:
        lines.append(result.get("warning", "no metrics"))
    return "\n".join(lines)
