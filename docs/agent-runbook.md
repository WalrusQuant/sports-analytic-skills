# Agent runbook

Prompts for an installed pack.

## Data

```text
Use data-sources for NFL team-game counting stats. Seasons 2023 and 2024.
Record the manifest generated_at, the file URL, and the sha256. Then run
eda-sports on the team-game grain.
```

## EDA

```text
Use eda-sports on the team-game Parquet from data-sources. Report grain,
season coverage, duplicate keys, missing scores, and modeling red flags.
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
baseline delta, sample size, limitations, and the manifest snapshot used.
```

## If something fails

1. Confirm the skill and read its input contract.
2. Confirm the column exists on the manifest entry.
3. Do not invent a field or a dataset.
4. Do not download or overwrite files the user did not ask for.
