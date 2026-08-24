"""Simple ensembles for sports probability models."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from sports_ds.models.predict import EvalResult, evaluate_classifier, fit_win_classifier


@dataclass
class EnsembleSpec:
    name: str
    weights: dict[str, float]


def average_probs(prob_map: dict[str, np.ndarray], weights: dict[str, float] | None = None) -> np.ndarray:
    """Weighted average of probability arrays (same length)."""
    keys = list(prob_map.keys())
    if not keys:
        raise ValueError("prob_map empty")
    if weights is None:
        weights = {k: 1.0 for k in keys}
    num = None
    den = 0.0
    for k in keys:
        w = float(weights.get(k, 0.0))
        if w <= 0:
            continue
        arr = np.asarray(prob_map[k], dtype=float)
        num = arr * w if num is None else num + arr * w
        den += w
    if num is None or den <= 0:
        raise ValueError("no positive weights")
    return np.clip(num / den, 1e-6, 1 - 1e-6)


def fit_form_elo_ensemble(
    df: pd.DataFrame,
    form_cols: list[str],
    train_mask: pd.Series,
    test_mask: pd.Series,
    *,
    elo_col: str = "elo_diff",
    form_weight: float = 0.5,
    elo_weight: float = 0.5,
) -> tuple[dict, EvalResult, np.ndarray]:
    """
    Average form logistic probs with Elo-diff logistic probs.
    Both models fit only on train fold.
    """
    train = df.loc[train_mask].dropna(subset=form_cols + [elo_col, "won"]).copy()
    test = df.loc[test_mask].dropna(subset=form_cols + [elo_col, "won"]).copy()

    form_model = Pipeline(
        [("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=2000))]
    )
    form_model.fit(train[form_cols], train["won"].astype(int))
    p_form = form_model.predict_proba(test[form_cols])[:, 1]

    elo_model = Pipeline(
        [("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=2000))]
    )
    elo_model.fit(train[[elo_col, "is_home"] if "is_home" in train.columns else [elo_col]], train["won"].astype(int))
    elo_feats = [elo_col] + (["is_home"] if "is_home" in test.columns else [])
    p_elo = elo_model.predict_proba(test[elo_feats])[:, 1]

    p = average_probs({"form": p_form, "elo": p_elo}, {"form": form_weight, "elo": elo_weight})
    result = evaluate_classifier("form_elo_avg", test["won"].astype(int), p)
    models = {"form": form_model, "elo": elo_model}
    return models, result, p


def fit_model_ladder(
    df: pd.DataFrame,
    feature_cols: list[str],
    train_mask: pd.Series,
    test_mask: pd.Series,
    *,
    models: list[str] | None = None,
) -> dict[str, EvalResult]:
    """Fit several classifiers on one fold; return name->metrics."""
    if models is None:
        models = ["logistic", "hist_gbm"]
    out: dict[str, EvalResult] = {}
    for m in models:
        _, res, _ = fit_win_classifier(df, feature_cols, train_mask, test_mask, model_type=m)
        out[m] = res
    return out
