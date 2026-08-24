---
name: baseline-models
description: Design and evaluate simple sports prediction baselines before accepting more complex models. Use for constant-rate, home-advantage, logistic, Elo-style, or market-reference comparisons.
---

# Baseline Models

Establish the weakest credible alternatives before evaluating a complex model. Work directly from data the user supplies; do not make obtaining data a prerequisite for the analysis.

## Baseline ladder

For binary outcomes, compare at least:

1. Training-fold event rate, carried forward unchanged.
2. A domain prior such as home advantage, seed, or rating difference.
3. A regularized logistic model on the same legal features as the candidate.
4. A strong domain reference, such as Elo or consensus market probability, when it is available in the user's table.

Use exactly the same chronological folds, eligible rows, target, and scoring rules for every candidate. Fit rates, encoders, scalers, and model parameters on training rows only. Report fold-level sample sizes and metrics, then summarize mean and dispersion. Read [references/baseline_ladder.md](references/baseline_ladder.md) when selecting domain baselines and [references/interpretation.md](references/interpretation.md) when explaining results.

## Bundled helpers

The helpers accept user-owned CSV, Parquet, JSON, JSONL, or NDJSON records. Parquet needs a pandas-compatible Parquet engine. They validate named columns before fitting. Replace `/path/to/baseline-models` below with the installed skill's path.

```bash
python /path/to/baseline-models/scripts/run_baselines.py \
  --input games.csv --target won --split-col season \
  --features is_home,rating_diff,rest_diff \
  --id-cols game_id,team --out baseline-folds.json \
  --predictions-out baseline-predictions.csv

python /path/to/baseline-models/scripts/home_only_baseline.py \
  --input games.csv --target won --home-col is_home
```

`run_baselines.py` requires pandas, NumPy, and scikit-learn. Its JSON fold
artifact is directly consumable by the visualization skill, while its held-out
prediction table can be passed to calibration and interpretation skills.
`home_only_baseline.py` requires pandas and reports group rates plus a
continuity-corrected odds ratio and Wald interval. Both expose `--help` before
optional libraries are imported.

Treat the home-only fit as pooled inference, not predictive validation. Do not promote a model merely for beating the constant baseline; require improvement over the strongest relevant simple baseline and inspect stability across folds.

## Hard constraints

- Never estimate a baseline on test rows.
- Never compare candidates on different folds or eligible populations.
- Never omit a credible domain baseline merely because it is harder to beat.

## Output contract

`run_baselines.py --out` writes a JSON object with the modeling contract,
validation design, model names, fold metrics, and mean metrics.
`--predictions-out` writes one row per held-out observation with identifiers,
split/fold, `y_true`, `constant_probability`, and `logistic_probability`.
Report candidate deltas and a keep/reject conclusion tied to the predeclared
success rule alongside these machine-readable artifacts.
