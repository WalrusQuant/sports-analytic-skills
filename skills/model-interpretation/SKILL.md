---
name: model-interpretation
description: >
  Interpret sports models using held-out predictions, coefficients, error
  slices, largest misses, calibration context, and stability checks. Use after
  time-aware evaluation when explaining what drives a model and where it fails.
license: MIT
metadata:
  version: "0.12.0"
---

# Model Interpretation for Sports

Interpretation explains evaluated behavior; it does not rescue weak evaluation.
Use only out-of-sample predictions for error analysis.

## Required inputs

Provide a user-owned CSV, Parquet, JSON, JSONL, or NDJSON prediction table with:

- a binary actual-outcome column (default `actual`)
- a predicted-probability column in `[0, 1]` (default `probability`)
- identifiers such as season, date, game, team, and opponent
- useful slice columns such as home/away, season, competition, or market

Keep fold assignment and prediction timestamp when available. Never mix
in-sample fitted values with held-out predictions without labeling them.

## Workflow

1. Confirm predictions are held out and aligned one-to-one with outcomes.
2. Compare the model with the same baseline on the same rows.
3. Inspect log loss, Brier score, accuracy, and base rate by meaningful slices.
4. Rank largest probability errors and investigate data, context, and regime.
5. Read coefficients/importances as associations conditional on the model.
6. Check sign and magnitude stability across time folds.
7. Report where the explanation is reliable and where sample size is weak.

See `references/interpretation_methods.md`, `references/slice_guide.md`, and
`references/miss_taxonomy.md` for deeper guidance.

## Standalone helpers

Install `pandas` and `numpy`. Parquet also needs `pyarrow` or `fastparquet`.

```bash
python /absolute/path/to/slice_errors.py \
  --input predictions.csv --slice-cols season,is_home --out slices.json

python /absolute/path/to/largest_misses.py \
  --input predictions.csv --columns season,game_id,team,opponent --top 25
```

Use `--actual-col` and `--prob-col` for alternate schemas. The scripts validate
required columns, binary outcomes, and probability bounds.
Prediction artifacts should contain one row per evaluated decision. When a
symmetric team-game table contains both perspectives, add
`--filter-col is_home --filter-value 1`.

## Honest interpretation

Do not claim causality from predictive coefficients. Mention correlation among
features, transformations, regularization, sample size, uncertainty, and drift.
Aggregate slices can hide failures, while tiny slices can manufacture them.
