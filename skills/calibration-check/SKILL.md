---
name: calibration-check
description: Evaluate whether sports-model probabilities match observed frequencies. Use for Brier score, log loss, reliability bins, ECE, segment checks, and recalibration decisions.
---

# Calibration Check

Analyze out-of-sample predictions already present in a user-owned table. Required inputs are a binary outcome column and a predicted-probability column; never assess calibration on in-sample fitted values unless explicitly diagnosing overfit.

## Procedure

1. Confirm outcomes are 0/1 and probabilities lie in `[0, 1]`.
2. Verify predictions were created without using the evaluated outcome and preferably came from chronological holdouts.
3. Report sample size, Brier score, log loss, ECE, and a reliability table.
4. Slice by season/fold, home/away, competition, and probability tails when columns exist.
5. Require enough observations per bin; merge sparse bins or show uncertainty rather than overinterpreting them.
6. Recalibrate only on training data inside the evaluation design, then retest on untouched future rows.

Read [references/calibration_metrics.md](references/calibration_metrics.md) for metric interpretation, [references/binning.md](references/binning.md) for binning choices, and [references/recalibration.md](references/recalibration.md) before applying Platt or isotonic calibration.

## Bundled helpers

The scripts accept CSV, Parquet, JSON, JSONL, or NDJSON records and require pandas. Replace `/path/to/calibration-check` with the installed skill path.

```bash
python /path/to/calibration-check/scripts/calibration_report.py \
  --input predictions.csv --target won --probability win_probability \
  --group-col season --bins 10 --out calibration.json

python /path/to/calibration-check/scripts/segment_calibration.py \
  --input predictions.csv --target won --probability win_probability \
  --segment-col is_home
```

`calibration_report.py` writes JSON only when `--out` is supplied. `segment_calibration.py` prints all-row, categorical-segment, and probability-tail metrics. Both expose `--help` without importing pandas.
The input must contain one row per evaluated decision. For symmetric team-game
artifacts, select one perspective with `--filter-col is_home --filter-value 1`
rather than double-counting each game.

## Hard constraints

- Never infer calibration from accuracy or ranking metrics.
- Never fit recalibration on the evaluated holdout.
- Never hide sparse or unstable bins.

## Output contract

Return evaluated row count and provenance, Brier score, log loss, ECE,
reliability bins with denominators, important segment results, and a decision to
retain, recalibrate, or gather more evidence.
