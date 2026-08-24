---
name: predictive-modeling
description: Build and evaluate predictive sports models from user-provided modeling data. Use for binary outcome models, feature/model selection, chronological backtests, probability scoring, and comparison to baselines.
---

# Predictive Modeling

Work from a user-owned modeling table. If data is missing, identify the required grain and fields and treat data acquisition as a separate optional task rather than a dependency of this workflow.

## Modeling contract

Before fitting, define:

- target and row grain;
- prediction decision time;
- eligible population and exclusions;
- chronological split unit;
- primary metric and practical success threshold;
- baseline ladder;
- probability or point-prediction output needs.

For win probabilities, prefer log loss or Brier score as the primary metric and accuracy only as a secondary diagnostic. For continuous targets, select MAE/RMSE according to error costs. Never tune on the final future holdout.

## Workflow

1. Audit feature legality and dataset grain.
2. Freeze chronological walk-forward folds.
3. Establish constant and domain baselines.
4. Fit a regularized linear/logistic model before nonlinear models.
5. Put imputation, encoding, scaling, and selection inside the fold-local estimator pipeline.
6. Tune only within past training data.
7. Report every fold, sample sizes, aggregate metrics, calibration, and comparison with baselines.
8. Prefer the simplest model whose improvement is stable and practically meaningful.

Read [references/leakage_rules.md](references/leakage_rules.md) before feature use, [references/metrics.md](references/metrics.md) when choosing the score, [references/model_ladder.md](references/model_ladder.md) for model progression, and [references/walk_forward.md](references/walk_forward.md) for validation design.

## Bundled helpers

The scripts accept CSV, Parquet, JSON, JSONL, or NDJSON records. They require pandas; the fold comparison additionally needs NumPy and scikit-learn. Optional libraries are imported only after argument parsing, so `--help` remains available.

```bash
python /path/to/predictive-modeling/scripts/leakage_smoke.py \
  --input modeling_table.csv --target won \
  --features is_home,rating_diff,rest_diff

python /path/to/predictive-modeling/scripts/run_fold_table.py \
  --input modeling_table.csv --target won --split-col season \
  --features is_home,rating_diff,rest_diff --min-train-groups 2 \
  --id-cols game_id,team --out model-folds.json \
  --predictions-out held-out-predictions.csv
```

The smoke check is intentionally fast and incomplete. The fold helper compares
a training-rate constant, regularized logistic regression, and histogram
gradient boosting on identical expanding folds. Its JSON artifact can go
directly to sports visualization; its row-level held-out prediction table can
go to calibration or interpretation. Replace `/path/to/predictive-modeling`
with the installed skill path.

## Hard constraints

- Never use random shuffled folds by default for ordered sports predictions.
- Never fit preprocessing, selection, or tuning on future folds.
- Never report a candidate without the same-row baseline comparison.

## Output contract

`run_fold_table.py --out` writes a JSON object containing the modeling contract,
validation design, candidate ladder, per-fold metrics, and mean metrics.
`--predictions-out` writes identifiers, split/fold, `y_true`, and held-out
`constant_probability`, `logistic_probability`, and `hist_gbm_probability`.
Use those artifacts to add baseline deltas, calibration evidence, limitations,
and a reproducible decision.
