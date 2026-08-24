import numpy as np

from sports_ds.metrics.calibration import expected_calibration_error, verdict_from_ece
from sports_ds.metrics.classification import brier_score, log_loss_binary


def test_perfect_probs_metrics():
    y = np.array([0, 1, 1, 0])
    p = np.array([0.0, 1.0, 1.0, 0.0])
    assert brier_score(y, p) == 0.0
    assert log_loss_binary(y, p) < 1e-6
    assert expected_calibration_error(y, p, n_bins=4) == 0.0


def test_verdict_thresholds():
    assert verdict_from_ece(0.01, 500) == "well-calibrated"
    assert verdict_from_ece(0.05, 500) == "usable-with-caveats"
    assert verdict_from_ece(0.2, 500) == "poorly-calibrated"
    assert verdict_from_ece(0.01, 50) == "usable-with-caveats"
