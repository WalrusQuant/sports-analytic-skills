# Model Ladder

Climb only with walk-forward evidence on the primary metric.

1. **Constant / mean** — floor.
2. **Single domain factor** — home, rest, or rating diff.
3. **Regularized linear / logistic on clean features** — often production winner on medium sports tabular problems.
4. **Tree ensembles (HistGBM, XGBoost, LightGBM)** — when nonlinear interactions are real and validated across folds.
5. **Specialized architectures** — tracking/sequence/graph models only with enough data and clear failure of rungs 3–4.

## Promotion rule

A higher rung must improve primary metric on multiple time folds, not one lucky season.

## Demotion rule

If a simpler rung matches the complex model within noise, keep the simpler model.
