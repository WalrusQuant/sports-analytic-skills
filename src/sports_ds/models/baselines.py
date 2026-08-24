"""Strong simple baselines for sports prediction."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


@dataclass
class BaselineResult:
    name: str
    n: int
    log_loss: float
    brier: float
    accuracy: float


def _safe_log_loss(y_true, y_prob) -> float:
    p = np.clip(np.asarray(y_prob, dtype=float), 1e-6, 1 - 1e-6)
    return float(log_loss(y_true, p, labels=[0, 1]))


def baseline_home_rate(df: pd.DataFrame, train_mask: pd.Series, test_mask: pd.Series) -> BaselineResult:
    """Predict P(win) using training-set win rate among home rows when is_home else 1-home_rate on away.

    For team-game panel: use overall train win rate as constant probability.
    """
    y_train = df.loc[train_mask, "won"].astype(int)
    y_test = df.loc[test_mask, "won"].astype(int)
    p = float(y_train.mean()) if len(y_train) else 0.5
    prob = np.full(len(y_test), p, dtype=float)
    return BaselineResult(
        name="constant_train_win_rate",
        n=int(len(y_test)),
        log_loss=_safe_log_loss(y_test, prob),
        brier=float(brier_score_loss(y_test, prob)),
        accuracy=float(accuracy_score(y_test, (prob >= 0.5).astype(int))),
    )


def fit_logistic_baseline(
    df: pd.DataFrame,
    feature_cols: list[str],
    train_mask: pd.Series,
    test_mask: pd.Series,
) -> tuple[Pipeline, BaselineResult, np.ndarray]:
    """Fit a simple logistic baseline on provided features."""
    train = df.loc[train_mask].dropna(subset=feature_cols + ["won"]).copy()
    test = df.loc[test_mask].dropna(subset=feature_cols + ["won"]).copy()

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )
    model.fit(train[feature_cols], train["won"].astype(int))
    prob = model.predict_proba(test[feature_cols])[:, 1]
    y_test = test["won"].astype(int)
    result = BaselineResult(
        name="logistic_baseline",
        n=int(len(y_test)),
        log_loss=_safe_log_loss(y_test, prob),
        brier=float(brier_score_loss(y_test, prob)),
        accuracy=float(accuracy_score(y_test, (prob >= 0.5).astype(int))),
    )
    return model, result, prob
