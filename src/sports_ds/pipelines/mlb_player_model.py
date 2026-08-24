"""MLB player-level walk-forward pipeline (batters via boxscores)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from sports_ds.data.mlb_players import load_mlb_player_game_panel
from sports_ds.features.player_form import (
    MLB_POSITIONS,
    MLB_STAT_COLS,
    add_pregame_player_form_features,
)
from sports_ds.pipelines.player_model import format_player_report
from sports_ds.validation.splits import season_walk_forward_masks

# Lean feature set proven to beat constant on dense 2023->2024 walk-forward.
MLB_LEAN_FEATURE_COLS = [
    "is_home",
    "batting_order_slot",
    "rest_days",
    "ewma5_fantasy_points",
    "roll5_fantasy_points",
    "pre_fantasy_points",
    "roll5_ops",
    "pre_ops",
    "roll5_plate_appearances",
    "opp_k9",
]


def _safe_mae(y, p) -> float:
    return float(mean_absolute_error(y, p))


def _safe_rmse(y, p) -> float:
    return float(np.sqrt(mean_squared_error(y, p)))


def _shrunk_player_baseline(
    train: pd.DataFrame,
    test: pd.DataFrame,
    target_col: str,
    *,
    k: float = 20.0,
) -> np.ndarray:
    """Empirical-Bayes shrink player train means toward global mean."""
    ytr = train[target_col].astype(float)
    g = float(ytr.mean()) if len(ytr) else 0.0
    mu = train.groupby("player_id")[target_col].mean()
    cnt = train.groupby("player_id")[target_col].count()
    shrink = (cnt / (cnt + k)) * mu + (k / (cnt + k)) * g
    return test["player_id"].map(shrink).astype(float).fillna(g).to_numpy(dtype=float)


def run_mlb_player_pipeline(
    seasons: list[int],
    *,
    target_col: str = "fantasy_points",
    positions: set[str] | None = None,
    min_train_seasons: int = 1,
    min_pre_games: int = 15,
    min_pa: float = 2.0,
    min_train_rows: int = 1000,
    min_test_rows: int = 500,
    max_games: int | None = None,
    workers: int = 8,
    feature_cols: list[str] | None = None,
    lineup_only: bool = True,
) -> dict[str, Any]:
    # default: hitters only (exclude pure P unless asked)
    if positions is None:
        positions = {p for p in MLB_POSITIONS if p != "P"}
    panel = load_mlb_player_game_panel(
        seasons,
        positions=positions,
        min_pa=min_pa,
        max_games=max_games,
        workers=workers,
        lineup_only=lineup_only,
    )
    # For sparse/capped samples, relax history thresholds so folds can form.
    if max_games is not None and int(max_games) < 1500:
        min_pre_games = min(min_pre_games, 5)
        min_train_rows = min(min_train_rows, 300)
        min_test_rows = min(min_test_rows, 150)

    featured = add_pregame_player_form_features(
        panel,
        stat_cols=list(MLB_STAT_COLS),
        position_values=tuple(sorted(positions)),
        windows=[3, 5, 10],
    )

    # Target-aware lean defaults
    if feature_cols is None:
        if target_col == "total_bases":
            use_cols = [
                c
                for c in [
                    "is_home",
                    "batting_order_slot",
                    "rest_days",
                    "ewma5_total_bases",
                    "roll5_total_bases",
                    "pre_total_bases",
                    "roll5_ops",
                    "pre_ops",
                    "roll5_plate_appearances",
                    "opp_k9",
                ]
                if c in featured.columns
            ]
        elif target_col == "hits":
            use_cols = [
                c
                for c in [
                    "is_home",
                    "batting_order_slot",
                    "rest_days",
                    "ewma5_hits",
                    "roll5_hits",
                    "pre_hits",
                    "roll5_ops",
                    "pre_ops",
                    "roll5_plate_appearances",
                    "opp_k9",
                ]
                if c in featured.columns
            ]
        elif target_col == "plate_appearances":
            use_cols = [
                c
                for c in [
                    "is_home",
                    "batting_order_slot",
                    "rest_days",
                    "ewma5_plate_appearances",
                    "roll5_plate_appearances",
                    "pre_plate_appearances",
                    "season_week",
                ]
                if c in featured.columns
            ]
        else:
            use_cols = [c for c in MLB_LEAN_FEATURE_COLS if c in featured.columns]
    else:
        use_cols = [c for c in feature_cols if c in featured.columns]

    # Starting lineup only when order is known.
    if "batting_order_slot" in featured.columns:
        featured = featured[
            featured["batting_order_slot"].isna()
            | ((featured["batting_order_slot"] >= 1) & (featured["batting_order_slot"] <= 9))
        ].copy()

    if "opp_k9" in featured.columns:
        featured["opp_k9"] = pd.to_numeric(featured["opp_k9"], errors="coerce")
    if "rest_days" in featured.columns:
        featured["rest_days"] = pd.to_numeric(featured["rest_days"], errors="coerce").fillna(1.0)

    need = [c for c in use_cols if c != "opp_k9"] + [target_col, "player_id"]
    model_df = featured.dropna(subset=need).copy()
    if "pre_games_played" in model_df.columns:
        model_df = model_df[model_df["pre_games_played"] >= min_pre_games].copy()
    if "plate_appearances" in model_df.columns:
        model_df = model_df[model_df["plate_appearances"] >= float(min_pa)].copy()

    fold_rows: list[dict[str, Any]] = []
    for test_season, train_mask, test_mask in season_walk_forward_masks(
        model_df, min_train_seasons=min_train_seasons
    ):
        if int(train_mask.sum()) < min_train_rows or int(test_mask.sum()) < min_test_rows:
            continue
        train = model_df.loc[train_mask].copy()
        test = model_df.loc[test_mask].copy()

        cols = list(use_cols)
        if "opp_k9" in cols:
            med = float(train["opp_k9"].median()) if train["opp_k9"].notna().any() else 8.0
            train["opp_k9"] = train["opp_k9"].fillna(med)
            test["opp_k9"] = test["opp_k9"].fillna(med)

        y_tr = train[target_col].astype(float).to_numpy()
        y_te = test[target_col].astype(float).to_numpy()
        global_mu = float(y_tr.mean()) if len(y_tr) else 0.0
        const_pred = np.full(len(y_te), global_mu, dtype=float)
        player_pred = _shrunk_player_baseline(train, test, target_col)

        ridge = Pipeline([("scaler", StandardScaler()), ("reg", Ridge(alpha=10.0))])
        ridge.fit(train[cols], y_tr)
        ridge_pred = np.clip(ridge.predict(test[cols]), 0.0, None)

        gbr = HistGradientBoostingRegressor(
            max_depth=3,
            learning_rate=0.05,
            max_iter=250,
            min_samples_leaf=80,
            l2_regularization=2.0,
        )
        gbr.fit(train[cols], y_tr)
        gbr_pred = np.clip(gbr.predict(test[cols]), 0.0, None)

        blend = np.clip(0.4 * player_pred + 0.6 * gbr_pred, 0.0, None)

        fold_rows.append(
            {
                "test_season": int(test_season),
                "n_train": int(len(train)),
                "n_test": int(len(test)),
                "constant_mae": _safe_mae(y_te, const_pred),
                "player_hist_mae": _safe_mae(y_te, player_pred),
                "ridge_mae": _safe_mae(y_te, ridge_pred),
                "hist_gbr_mae": _safe_mae(y_te, gbr_pred),
                "blend_mae": _safe_mae(y_te, blend),
                "constant_rmse": _safe_rmse(y_te, const_pred),
                "player_hist_rmse": _safe_rmse(y_te, player_pred),
                "ridge_rmse": _safe_rmse(y_te, ridge_pred),
                "hist_gbr_rmse": _safe_rmse(y_te, gbr_pred),
                "blend_rmse": _safe_rmse(y_te, blend),
            }
        )

    folds = pd.DataFrame(fold_rows)
    out: dict[str, Any] = {
        "sport": "mlb",
        "pipeline": "mlb_player",
        "target": target_col,
        "seasons_requested": seasons,
        "rows_raw_panel": int(len(panel)),
        "rows_modeled": int(len(model_df)),
        "feature_cols": use_cols,
        "positions": sorted(positions),
        "min_pa": min_pa,
        "min_pre_games": min_pre_games,
        "max_games": max_games,
        "lineup_only": lineup_only,
        "folds": fold_rows,
    }
    if len(folds):
        mean_keys = [
            "constant_mae",
            "player_hist_mae",
            "ridge_mae",
            "hist_gbr_mae",
            "blend_mae",
            "constant_rmse",
            "player_hist_rmse",
            "ridge_rmse",
            "hist_gbr_rmse",
            "blend_rmse",
        ]
        means = {k: float(folds[k].mean()) for k in mean_keys}
        out["mean_metrics"] = means
        out["beats_constant_ridge"] = bool(means["ridge_mae"] < means["constant_mae"])
        out["beats_constant_hist_gbr"] = bool(means["hist_gbr_mae"] < means["constant_mae"])
        out["beats_constant_player_hist"] = bool(means["player_hist_mae"] < means["constant_mae"])
        out["beats_constant_blend"] = bool(means["blend_mae"] < means["constant_mae"])
        cand = [
            ("player_hist", means["player_hist_mae"]),
            ("ridge", means["ridge_mae"]),
            ("hist_gbr", means["hist_gbr_mae"]),
            ("blend", means["blend_mae"]),
        ]
        out["best_model"] = min(cand, key=lambda x: x[1])[0]
        out["beats_constant"] = bool(min(v for _, v in cand) < means["constant_mae"])
    else:
        out["mean_metrics"] = {}
        out["warning"] = "no walk-forward folds produced"
    return out


def format_mlb_player_report(result: dict[str, Any]) -> str:
    base = format_player_report(result, title="MLB player pipeline (batters)")
    means = result.get("mean_metrics") or {}
    if not means:
        return base
    extra = [
        "",
        "MLB baselines/models:",
        f"  player_hist_mae: {means.get('player_hist_mae', float('nan')):.4f}",
        f"  blend_mae: {means.get('blend_mae', float('nan')):.4f}",
        f"  beats_constant_player_hist: {result.get('beats_constant_player_hist')}",
        f"  beats_constant_blend: {result.get('beats_constant_blend')}",
        f"  beats_constant_any: {result.get('beats_constant')}",
    ]
    return base + "\n" + "\n".join(extra)
