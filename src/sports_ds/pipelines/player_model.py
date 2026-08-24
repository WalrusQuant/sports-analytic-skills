"""Generic player-level walk-forward regression pipeline."""

from __future__ import annotations

from typing import Any, Callable

import pandas as pd

from sports_ds.features.player_form import add_pregame_player_form_features
from sports_ds.models.regress import baseline_mean_margin, fit_margin_regressor
from sports_ds.validation.splits import season_walk_forward_masks


def run_player_pipeline(
    panel: pd.DataFrame,
    *,
    sport: str,
    seasons: list[int],
    target_col: str,
    feature_cols: list[str],
    stat_cols: list[str] | None = None,
    position_values: tuple[str, ...] | list[str] | None = None,
    min_train_seasons: int = 1,
    min_pre_games: int = 3,
    min_train_rows: int = 200,
    min_test_rows: int = 100,
    extra_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    featured = add_pregame_player_form_features(
        panel, stat_cols=stat_cols, position_values=position_values
    )
    use_cols = [c for c in feature_cols if c in featured.columns]
    need = use_cols + [target_col]
    model_df = featured.dropna(subset=need).copy()
    if "pre_games_played" in model_df.columns:
        model_df = model_df[model_df["pre_games_played"] >= min_pre_games].copy()

    fold_rows: list[dict[str, Any]] = []
    for test_season, train_mask, test_mask in season_walk_forward_masks(
        model_df, min_train_seasons=min_train_seasons
    ):
        if int(train_mask.sum()) < min_train_rows or int(test_mask.sum()) < min_test_rows:
            continue
        const = baseline_mean_margin(model_df, train_mask, test_mask, target_col=target_col)
        _, ridge, _ = fit_margin_regressor(
            model_df, use_cols, train_mask, test_mask, target_col=target_col, model_type="ridge"
        )
        _, gbr, _ = fit_margin_regressor(
            model_df, use_cols, train_mask, test_mask, target_col=target_col, model_type="hist_gbr"
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
        "sport": sport,
        "pipeline": f"{sport}_player",
        "target": target_col,
        "seasons_requested": seasons,
        "rows_raw_panel": int(len(panel)),
        "rows_modeled": int(len(model_df)),
        "feature_cols": use_cols,
        "folds": fold_rows,
    }
    if extra_meta:
        out.update(extra_meta)
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


def format_player_report(result: dict[str, Any], title: str | None = None) -> str:
    sport = str(result.get("sport", "player")).upper()
    lines = [
        title or f"{sport} player pipeline",
        f"target: {result.get('target')}",
        f"positions: {result.get('positions')}",
        f"seasons: {result.get('seasons_requested')}",
        f"raw rows: {result.get('rows_raw_panel')}",
        f"modeled rows: {result.get('rows_modeled')}",
        f"features ({len(result.get('feature_cols') or [])}): {result.get('feature_cols')}",
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


def run_loader_player_pipeline(
    load_panel: Callable[..., pd.DataFrame],
    seasons: list[int],
    *,
    sport: str,
    target_col: str,
    feature_cols: list[str],
    load_kwargs: dict[str, Any] | None = None,
    **pipeline_kwargs: Any,
) -> dict[str, Any]:
    panel = load_panel(seasons, **(load_kwargs or {}))
    return run_player_pipeline(
        panel,
        sport=sport,
        seasons=seasons,
        target_col=target_col,
        feature_cols=feature_cols,
        **pipeline_kwargs,
    )
