"""Binary classification metrics."""

from __future__ import annotations

import numpy as np


def safe_clip_prob(p, eps: float = 1e-15) -> np.ndarray:
    return np.clip(np.asarray(p, dtype=float), eps, 1.0 - eps)


def brier_score(y_true, y_prob) -> float:
    y = np.asarray(y_true, dtype=float)
    p = np.asarray(y_prob, dtype=float)
    return float(np.mean((p - y) ** 2))


def log_loss_binary(y_true, y_prob, eps: float = 1e-15) -> float:
    y = np.asarray(y_true, dtype=float)
    p = safe_clip_prob(y_prob, eps=eps)
    return float(-np.mean(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)))
