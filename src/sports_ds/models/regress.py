"""Regression models for sports margins/scores."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


@dataclass
class RegressResult:
    name: str
    n: int
    mae: float
    rmse: float
    r2: float


def evaluate_regressor(name: str, y_true, y_pred) -> RegressResult:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return RegressResult(
        name=name,
        n=int(len(y_true)),
        mae=float(mean_absolute_error(y_true, y_pred)),
        rmse=float(np.sqrt(mean_squared_error(y_true, y_pred))),
        r2=float(r2_score(y_true, y_pred)) if len(y_true) > 1 else float("nan"),
    )


def fit_margin_regressor(
    df: pd.DataFrame,
    feature_cols: list[str],
    train_mask: pd.Series,
    test_mask: pd.Series,
    target_col: str = "point_diff",
    model_type: str = "ridge",
):
    train = df.loc[train_mask].dropna(subset=feature_cols + [target_col]).copy()
    test = df.loc[test_mask].dropna(subset=feature_cols + [target_col]).copy()

    if model_type == "ridge":
        model = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("reg", Ridge(alpha=1.0)),
            ]
        )
    elif model_type == "hist_gbr":
        model = HistGradientBoostingRegressor(max_depth=4, learning_rate=0.08, max_iter=150)
    else:
        raise ValueError(f"unknown model_type: {model_type}")

    model.fit(train[feature_cols], train[target_col].astype(float))
    pred = model.predict(test[feature_cols])
    result = evaluate_regressor(model_type, test[target_col].astype(float), pred)
    out = test.assign(pred_margin=pred)
    return model, result, out


def baseline_mean_margin(
    df: pd.DataFrame,
    train_mask: pd.Series,
    test_mask: pd.Series,
    target_col: str = "point_diff",
) -> RegressResult:
    y_train = df.loc[train_mask, target_col].astype(float)
    y_test = df.loc[test_mask, target_col].astype(float)
    mu = float(y_train.mean()) if len(y_train) else 0.0
    pred = np.full(len(y_test), mu, dtype=float)
    return evaluate_regressor("constant_train_mean", y_test, pred)
