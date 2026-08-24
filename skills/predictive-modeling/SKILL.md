---
name: predictive-modeling
description: >
  Predictive ML for sports: model choice, training protocol, feature matrices,
  and evaluation against baselines under time-safe splits. Use for forecasting
  outcomes, stats, or ranks after baselines exist.
version: "0.1.0"
license: MIT
---

# Predictive Modeling (Sports)

Machine learning skill for sports prediction tasks.

## When to use

- Tabular prediction on games/players/possessions
- Nonlinear effects likely after linear baselines
- Need a disciplined train/validate protocol for ML models

## When not to use

- No baselines yet → `baseline-models` first
- Explanatory inference is the goal → `statistical-modeling`
- Sequence ratings only → `ratings-strength-models` / `time-series-sports`

## Model ladder (climb only as earned)

1. strong linear/logistic baseline
2. regularized linear / GLM
3. tree ensembles (HistGBM/XGBoost/LightGBM)
4. careful neural nets only if data and problem justify

## Procedure

1. Confirm question, target, T, metrics.
2. Build time-safe feature matrix (`feature-rules`).
3. Lock walk-forward design (`validation-design`).
4. Fit baselines first.
5. Fit candidate ML with tuning inside training folds only.
6. Evaluate on forward folds; compare to baselines.
7. Calibrate probabilities if needed (`calibration-check`).
8. Interpret drivers (`model-interpretation`).
9. Log experiment (`experiment-log`).

## Hard constraints

- No ML before baselines
- No random split default on chronological sports data
- No tuning on final holdout
- No leakage features
- Complexity must earn metric gains, not vibes

## Anti-patterns

- XGBoost as step 1
- Huge feature soup
- Early stopping on true test labels
- Reporting only accuracy for imbalanced outcomes

## Output contract

- [ ] Baseline metrics present
- [ ] Candidate metrics present on same folds
- [ ] Tuning scope stated
- [ ] Lift vs baseline quantified
- [ ] Keep / discard decision

## Handoffs

- `feature-rules`, `leakage-audit`
- `calibration-check`
- `model-interpretation`
- `sports-visualization`
- `results-reporting`

## Stack hints

- `scikit-learn`, `xgboost`/`lightgbm` optional
- `polars`/`pandas` matrices
- persist models + configs for reproducibility
