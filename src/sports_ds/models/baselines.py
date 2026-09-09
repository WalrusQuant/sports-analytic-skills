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


def _baseline_from_probs(name: str, y_test, prob) -> BaselineResult:
    y_test = np.asarray(y_test, dtype=int)
    prob = np.asarray(prob, dtype=float)
    return BaselineResult(
        name=name,
        n=int(len(y_test)),
        log_loss=_safe_log_loss(y_test, prob),
        brier=float(brier_score_loss(y_test, prob)),
        accuracy=float(accuracy_score(y_test, (prob >= 0.5).astype(int))),
    )


def baseline_constant_rate(
    df: pd.DataFrame, train_mask: pd.Series, test_mask: pd.Series
) -> BaselineResult:
    """Predict P(win) with the training-set overall win rate (null baseline)."""
    y_train = df.loc[train_mask, "won"].astype(int)
    y_test = df.loc[test_mask, "won"].astype(int)
    p = float(y_train.mean()) if len(y_train) else 0.5
    prob = np.full(len(y_test), p, dtype=float)
    return _baseline_from_probs("constant_train_win_rate", y_test, prob)


def baseline_home_rate(df: pd.DataFrame, train_mask: pd.Series, test_mask: pd.Series) -> BaselineResult:
    """Predict P(win) with the training home win rate, and 1-p on away rows."""
    train = df.loc[train_mask]
    test = df.loc[test_mask]
    y_test = test["won"].astype(int)
    if "is_home" not in train.columns or "is_home" not in test.columns:
        return baseline_constant_rate(df, train_mask, test_mask)
    home = train.loc[train["is_home"].astype(int) == 1, "won"]
    p_home = float(home.mean()) if len(home) else 0.5
    is_home = test["is_home"].astype(int).to_numpy()
    prob = np.where(is_home == 1, p_home, 1.0 - p_home)
    return _baseline_from_probs("home_train_win_rate", y_test, prob)


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
