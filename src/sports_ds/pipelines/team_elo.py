"""Generic as-of Elo baseline walk-forward for any team-game panel."""

from __future__ import annotations

from typing import Any, Callable

import numpy as np
import pandas as pd

from sports_ds.metrics.calibration import expected_calibration_error, verdict_from_ece
from sports_ds.metrics.classification import brier_score, log_loss_binary
from sports_ds.models.baselines import baseline_home_rate, fit_logistic_baseline
from sports_ds.ratings.elo import add_elo_asof
from sports_ds.validation.splits import season_walk_forward_masks

FEATURE_COLS = ["is_home", "elo_diff"]


def run_team_elo_baseline(
    panel: pd.DataFrame,
    *,
    sport: str,
    seasons: list[int],
    min_train_seasons: int = 1,
    k: float = 20.0,
    home_adv: float = 65.0,
    min_train_rows: int = 100,
    min_test_rows: int = 50,
) -> dict[str, Any]:
    featured = add_elo_asof(panel, k=k, home_adv=home_adv)
    model_df = featured.dropna(subset=FEATURE_COLS + ["won"]).copy()

    fold_rows: list[dict[str, Any]] = []
    ys: list[np.ndarray] = []
    ps: list[np.ndarray] = []
    for test_season, train_mask, test_mask in season_walk_forward_masks(
        model_df, min_train_seasons=min_train_seasons
    ):
        if int(train_mask.sum()) < min_train_rows or int(test_mask.sum()) < min_test_rows:
            continue
        const = baseline_home_rate(model_df, train_mask, test_mask)
        _, log_res, prob = fit_logistic_baseline(model_df, FEATURE_COLS, train_mask, test_mask)
        test = model_df.loc[test_mask].dropna(subset=FEATURE_COLS + ["won"])
        y = test["won"].astype(int).to_numpy()
        p = np.asarray(prob, dtype=float)
        ys.append(y)
        ps.append(p)
        fold_rows.append(
            {
                "test_season": int(test_season),
                "n_train": int(train_mask.sum()),
                "n_test": int(len(test)),
                "constant_log_loss": const.log_loss,
                "elo_logistic_log_loss": log_res.log_loss,
                "constant_accuracy": const.accuracy,
                "elo_logistic_accuracy": log_res.accuracy,
                "elo_logistic_brier": log_res.brier,
            }
        )

    summary: dict[str, Any] = {
        "sport": sport,
        "seasons_requested": seasons,
        "rows_raw_panel": int(len(panel)),
        "rows_modeled": int(len(model_df)),
        "feature_cols": FEATURE_COLS,
        "elo_params": {"k": k, "home_adv": home_adv},
        "folds": fold_rows,
    }
    folds = pd.DataFrame(fold_rows)
    if len(folds):
        summary["mean_metrics"] = {
            "constant_log_loss": float(folds["constant_log_loss"].mean()),
            "elo_logistic_log_loss": float(folds["elo_logistic_log_loss"].mean()),
            "constant_accuracy": float(folds["constant_accuracy"].mean()),
            "elo_logistic_accuracy": float(folds["elo_logistic_accuracy"].mean()),
        }
        summary["beats_constant"] = bool(
            summary["mean_metrics"]["elo_logistic_log_loss"]
            < summary["mean_metrics"]["constant_log_loss"]
        )
        y_all = np.concatenate(ys)
        p_all = np.concatenate(ps)
        ece = expected_calibration_error(y_all, p_all, n_bins=10)
        summary["calibration"] = {
            "n": int(len(y_all)),
            "brier": brier_score(y_all, p_all),
            "log_loss": log_loss_binary(y_all, p_all),
            "ece": ece,
            "verdict": verdict_from_ece(ece, int(len(y_all))),
        }
    else:
        summary["mean_metrics"] = {}
        summary["warning"] = "no walk-forward folds produced"
    return summary


def format_team_elo_report(result: dict[str, Any], title: str | None = None) -> str:
    sport = str(result.get("sport", "team")).upper()
    head = title or f"{sport} Elo as-of baseline pipeline"
    lines = [
        head,
        f"seasons: {result.get('seasons_requested')}",
        f"params: {result.get('elo_params')}",
        f"raw panel rows: {result.get('rows_raw_panel')}",
        f"modeled rows: {result.get('rows_modeled')}",
        "",
    ]
    means = result.get("mean_metrics") or {}
    if means:
        lines.append("Walk-forward mean metrics:")
        for k, v in means.items():
            lines.append(f"  {k}: {v:.4f}")
        lines.append(f"elo logistic beats constant: {result.get('beats_constant')}")
        cal = result.get("calibration") or {}
        if cal:
            lines.append(
                "calibration: ece={ece:.4f} brier={brier:.4f} verdict={verdict} n={n}".format(**cal)
            )
        lines.append("")
        lines.append("Per-season folds:")
        for row in result.get("folds", []):
            lines.append(
                "  season {test_season}: const_ll={constant_log_loss:.4f} "
                "elo_ll={elo_logistic_log_loss:.4f} n_test={n_test}".format(**row)
            )
    else:
        lines.append(result.get("warning", "no metrics"))
    return "\n".join(lines)


def run_loader_elo_baseline(
    load_panel: Callable[[list[int]], pd.DataFrame],
    seasons: list[int],
    *,
    sport: str,
    min_train_seasons: int = 1,
    k: float = 20.0,
    home_adv: float = 65.0,
) -> dict[str, Any]:
    panel = load_panel(seasons)
    return run_team_elo_baseline(
        panel,
        sport=sport,
        seasons=seasons,
        min_train_seasons=min_train_seasons,
        k=k,
        home_adv=home_adv,
    )
