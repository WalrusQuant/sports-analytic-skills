"""Predictive classifiers for sports outcomes."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression


@dataclass
class EvalResult:
    name: str
    n: int
    log_loss: float
    brier: float
    accuracy: float


def _safe_log_loss(y_true, y_prob) -> float:
    p = np.clip(np.asarray(y_prob, dtype=float), 1e-6, 1 - 1e-6)
    return float(log_loss(y_true, p, labels=[0, 1]))


def evaluate_classifier(name: str, y_true, y_prob) -> EvalResult:
    y_true = np.asarray(y_true).astype(int)
    y_prob = np.asarray(y_prob, dtype=float)
    return EvalResult(
        name=name,
        n=int(len(y_true)),
        log_loss=_safe_log_loss(y_true, y_prob),
        brier=float(brier_score_loss(y_true, y_prob)),
        accuracy=float(accuracy_score(y_true, (y_prob >= 0.5).astype(int))),
    )


def fit_win_classifier(
    df: pd.DataFrame,
    feature_cols: list[str],
    train_mask: pd.Series,
    test_mask: pd.Series,
    model_type: str = "hist_gbm",
):
    train = df.loc[train_mask].dropna(subset=feature_cols + ["won"]).copy()
    test = df.loc[test_mask].dropna(subset=feature_cols + ["won"]).copy()

    if model_type == "logistic":
        model = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(max_iter=2000)),
            ]
        )
        model.fit(train[feature_cols], train["won"].astype(int))
        prob = model.predict_proba(test[feature_cols])[:, 1]
    elif model_type == "hist_gbm":
        model = HistGradientBoostingClassifier(max_depth=4, learning_rate=0.08, max_iter=150)
        model.fit(train[feature_cols], train["won"].astype(int))
        prob = model.predict_proba(test[feature_cols])[:, 1]
    else:
        raise ValueError(f"unknown model_type: {model_type}")

    result = evaluate_classifier(model_type, test["won"].astype(int), prob)
    return model, result, test.assign(pred_win_prob=prob)
