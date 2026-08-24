---
name: statistical-modeling
description: >
  Guided statistical modeling for user-provided sports data: selecting models
  for binary, continuous, and count outcomes; assumption checks; effect sizes;
  time-aware inference; GLM diagnostics; and complete reporting.
license: MIT
metadata:
  version: "0.5.0"
---

# Statistical Modeling for Sports

Choose the model family from the outcome and sampling process, not from habit.
Sports observations are often clustered by team/player and ordered in time, so
independence assumptions require explicit justification.

## Model choice

- Binary win/loss: binomial logistic model; report odds ratios and calibration.
- Continuous margin: linear or robust regression; inspect residual structure.
- Counts: Poisson first, then negative binomial when overdispersion is material.
- Repeated teams/players: clustered uncertainty or hierarchical effects.
- Prediction: use pre-event features and future-block validation.

Read the relevant files in `references/` for test selection, GLM choice,
diagnostics, effect sizes, Bayesian models, and reporting standards.

## Workflow

1. Define estimand, outcome, unit, timestamp, and population.
2. Validate grain, keys, missingness, and time availability of predictors.
3. Choose family/link and a simple comparison model.
4. Fit using an uncertainty method appropriate to clustering and time.
5. Check assumptions, influence, residuals, and probability calibration.
6. Evaluate predictions on later time blocks when prediction is the goal.
7. Report estimates, intervals, diagnostics, sample sizes, and limitations.

## Standalone assumption checks

Install `pandas`, `numpy`, and `scipy`; Parquet also needs `pyarrow` or
`fastparquet`. The helper accepts user-owned CSV, Parquet, JSON, JSONL, or
NDJSON and validates named columns.

```bash
python /absolute/path/to/assumption_checks.py \
  --input observations.csv --value-col margin \
  --group-col venue --out assumptions.json
```

It reports Shapiro-Wilk normality, IQR outliers, and optional median-centered
Levene variance testing. Formal tests supplement plots and domain judgment;
large samples can reject practically harmless departures.

## Standalone binomial GLM

Install `pandas`, `numpy`, and `scipy`.

```bash
python /absolute/path/to/glm_diagnostics.py \
  --input model_frame.csv \
  --formula "won ~ is_home + rating_diff + rest_diff" \
  --out glm_report.json
```

The input must contain binary `won` by default; use `--outcome-col` to rename
it. Formulas support additive numeric predictors joined by `+`. The report
includes robust HC3 inference, odds ratios, confidence intervals, AIC, and
in-sample calibration bins. Treat those bins as fit diagnostics, not held-out
predictive evidence.

## Reporting minimum

State data source and dates, grain, exclusions, formula, family/link,
uncertainty method, effect estimates with intervals, diagnostics, validation
design, baseline, sensitivity checks, and known threats to inference.
