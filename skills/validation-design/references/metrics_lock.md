# Metric Lock Guide

Lock one primary metric before fitting candidates.

| Task | Primary | Secondary |
|---|---|---|
| Win probability | log-loss | Brier, ECE/calibration |
| Margin | MAE | RMSE, bias |
| Counts | MAE / deviance | rate calibration |
| Ranking | future-period Spearman | pairwise accuracy |

## Rules

- Accuracy is never the sole primary metric for probability models
- Do not switch primary metric after seeing leaderboards
- Report secondary metrics, but decisions follow the primary
