"""Richer team-win walk-forward: expanded features + multi-model ladder + Elo ensemble."""

from __future__ import annotations

from typing import Any

import pandas as pd

from sports_ds.eda.summary import format_summary, summarize_team_game_panel
from sports_ds.features.team_form import RICH_WIN_FEATURE_COLS, add_pregame_form_features
from sports_ds.models.baselines import baseline_home_rate, fit_logistic_baseline
from sports_ds.models.ensemble import fit_form_elo_ensemble
from sports_ds.models.predict import fit_win_classifier
from sports_ds.ratings.elo import add_elo_asof
from sports_ds.validation.splits import season_walk_forward_masks


def run_team_win_rich_pipeline(
    panel: pd.DataFrame,
    *,
    sport: str,
    seasons: list[int],
    min_train_seasons: int = 2,
    min_pre_games: int = 3,
    min_train_rows: int = 100,
    min_test_rows: int = 50,
    elo_k: float = 20.0,
    elo_home_adv: float = 65.0,
    feature_cols: list[str] | None = None,
) -> dict[str, Any]:
    if feature_cols is None:
        feature_cols = list(RICH_WIN_FEATURE_COLS)

    eda = summarize_team_game_panel(panel)
    featured = add_pregame_form_features(panel)
    featured = add_elo_asof(featured, k=elo_k, home_adv=elo_home_adv)

    use_cols = [c for c in feature_cols if c in featured.columns]
    need = use_cols + ["won", "elo_diff"]
    model_df = featured.dropna(subset=[c for c in need if c in featured.columns]).copy()
    if "pre_games_played" in model_df.columns:
        model_df = model_df[
            (model_df["pre_games_played"] >= min_pre_games)
            & (model_df.get("opp_pre_games_played", min_pre_games) >= min_pre_games)
        ].copy()

    fold_rows: list[dict[str, Any]] = []
    for test_season, train_mask, test_mask in season_walk_forward_masks(
        model_df, min_train_seasons=min_train_seasons
    ):
        if int(train_mask.sum()) < min_train_rows or int(test_mask.sum()) < min_test_rows:
            continue
        const = baseline_home_rate(model_df, train_mask, test_mask)
        _, log_base, _ = fit_logistic_baseline(model_df, use_cols, train_mask, test_mask)
        _, gbm_res, _ = fit_win_classifier(
            model_df, use_cols, train_mask, test_mask, model_type="hist_gbm"
        )
        row: dict[str, Any] = {
            "test_season": int(test_season),
            "n_train": int(train_mask.sum()),
            "n_test": int(test_mask.sum()),
            "constant_log_loss": const.log_loss,
            "logistic_log_loss": log_base.log_loss,
            "hist_gbm_log_loss": gbm_res.log_loss,
            "constant_accuracy": const.accuracy,
            "logistic_accuracy": log_base.accuracy,
            "hist_gbm_accuracy": gbm_res.accuracy,
            "logistic_brier": log_base.brier,
            "hist_gbm_brier": gbm_res.brier,
        }
        if "elo_diff" in model_df.columns:
            try:
                _, ens_res, _ = fit_form_elo_ensemble(
                    model_df, use_cols, train_mask, test_mask, elo_col="elo_diff"
                )
                row["ensemble_log_loss"] = ens_res.log_loss
                row["ensemble_accuracy"] = ens_res.accuracy
                row["ensemble_brier"] = ens_res.brier
            except Exception as exc:  # noqa: BLE001 - fold-level soft fail
                row["ensemble_error"] = str(exc)
        fold_rows.append(row)

    folds = pd.DataFrame(fold_rows)
    summary: dict[str, Any] = {
        "sport": sport,
        "pipeline": "team_win_rich",
        "seasons_requested": seasons,
        "rows_raw_panel": int(len(panel)),
        "rows_modeled": int(len(model_df)),
        "feature_cols": use_cols,
        "eda_text": format_summary(eda),
        "folds": fold_rows,
    }
    if len(folds):
        mean_keys = [
            "constant_log_loss",
            "logistic_log_loss",
            "hist_gbm_log_loss",
            "ensemble_log_loss",
            "constant_accuracy",
            "logistic_accuracy",
            "hist_gbm_accuracy",
            "ensemble_accuracy",
        ]
        means = {}
        for k in mean_keys:
            if k in folds.columns:
                means[k] = float(folds[k].mean())
        summary["mean_metrics"] = means
        summary["beats_constant_logistic"] = bool(
            means.get("logistic_log_loss", 9) < means.get("constant_log_loss", 0)
        )
        summary["beats_constant_hist_gbm"] = bool(
            means.get("hist_gbm_log_loss", 9) < means.get("constant_log_loss", 0)
        )
        if "ensemble_log_loss" in means:
            summary["beats_constant_ensemble"] = bool(
                means["ensemble_log_loss"] < means.get("constant_log_loss", 0)
            )
            summary["best_model"] = min(
                (
                    ("logistic", means.get("logistic_log_loss", 9)),
                    ("hist_gbm", means.get("hist_gbm_log_loss", 9)),
                    ("ensemble", means.get("ensemble_log_loss", 9)),
                ),
                key=lambda x: x[1],
            )[0]
    else:
        summary["mean_metrics"] = {}
        summary["warning"] = "no walk-forward folds produced"
    return summary


def format_team_win_rich_report(result: dict[str, Any]) -> str:
    sport = str(result.get("sport", "team")).upper()
    lines = [
        f"{sport} rich team-win pipeline",
        f"seasons: {result.get('seasons_requested')}",
        f"features ({len(result.get('feature_cols') or [])}): {result.get('feature_cols')}",
        f"raw panel rows: {result.get('rows_raw_panel')}",
        f"modeled rows: {result.get('rows_modeled')}",
        "",
    ]
    means = result.get("mean_metrics") or {}
    if means:
        lines.append("Walk-forward mean metrics:")
        for k, v in means.items():
            lines.append(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
        lines.append(f"best_model: {result.get('best_model')}")
        lines.append(f"logistic beats constant: {result.get('beats_constant_logistic')}")
        lines.append(f"hist_gbm beats constant: {result.get('beats_constant_hist_gbm')}")
        if "beats_constant_ensemble" in result:
            lines.append(f"ensemble beats constant: {result.get('beats_constant_ensemble')}")
        lines.append("")
        lines.append("Per-season folds:")
        for row in result.get("folds", []):
            ens = row.get("ensemble_log_loss")
            ens_s = f" ens_ll={ens:.4f}" if isinstance(ens, float) else ""
            lines.append(
                "  season {test_season}: const_ll={constant_log_loss:.4f} "
                "log_ll={logistic_log_loss:.4f} gbm_ll={hist_gbm_log_loss:.4f}"
                f"{ens_s} n_test={{n_test}}".format(**row)
            )
    else:
        lines.append(result.get("warning", "no metrics"))
    return "\n".join(lines)
