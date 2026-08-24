# Agent runbook

Prompts for a skill-only installation.

## EDA

```text
Use eda-sports on data/team_games.parquet. Report grain, date and season
coverage, duplicates, missingness, target distribution, and modeling red flags.
```

## Feature legality

```text
Use feature-rules and leakage-audit on data/features.parquet. Decision time is
kickoff. Produce a pass/fail inventory with the earliest time each feature is
knowable.
```

## Baselines and predictive modeling

```text
Use baseline-models, predictive-modeling, and validation-design on this feature
table. Compare a constant baseline and logistic regression under season
walk-forward validation. Report per-fold and aggregate metrics.
```

## Calibration

```text
Use calibration-check on data/predictions.csv. The true-outcome column is
y_true and the probability column is p_pred. Report Brier score, log loss,
reliability bins, ECE, and important segments.
```

## Interpretation and reporting

```text
Use model-interpretation and results-reporting on data/predictions.csv and
data/fold_metrics.json. Identify the largest misses, meaningful error slices,
baseline delta, sample size, limitations, and reproduction inputs.
```

## Public data

```text
Use data-sources to choose a public source for NFL team-game schedules and
scores. Prefer a direct public loader skill and export a portable Parquet file.
```

## Optional sports_ds route

```text
Use sports-ds-bridge because I explicitly want the sports_ds toolkit. Load the
requested public data, export a portable artifact, validate it, and hand it to
eda-sports. Do not require the EDA skill to import sports_ds.
```

## Failure checklist

1. Confirm the selected skill and read its input contract.
2. Resolve helper paths relative to the installed `SKILL.md`.
3. Validate required columns and grain before computation.
4. Install only disclosed public dependencies for that helper.
5. Do not assume `sports_ds` exists unless using `sports-ds-bridge`.
6. Do not download data, install packages, or overwrite artifacts without the
   user's authorization.
