---
name: calibration-check
description: Evaluate whether sports-model probabilities match observed frequencies. Use for Brier score, log loss, reliability bins, ECE, segment checks, and recalibration decisions.
metadata:
  version: "0.12.0"
---

# Calibration Check (Sports)

## Overview

A model can rank teams well and still be miscalibrated. If the model says 30%,
about 30% of those cases should hit.

This skill measures probability reliability for sports models and supports a
human-reviewed verdict grounded in evaluation provenance, uncertainty, and
segment stability.

Discrimination metrics (AUC, accuracy) do **not** replace calibration.

---

## When to Use This Skill

Use when:

- Model outputs win/event probabilities
- User asks how confident / how reliable the probs are
- After walk-forward evaluation of a probability model
- Before writing results that quote probability levels
- Comparing raw vs recalibrated probabilities
- sport- and competition-specific probability artifacts

Do **not** use when:

| Need | Go instead |
|---|---|
| Pure ranking tasks with no probabilistic interpretation | ranking/eval skills |
| Hard labels only with no probability outputs | classification metrics only |
| Designing splits from scratch | `validation-design` |
| Feature legality review | `leakage-audit` |
| Margin-only models without probs | MAE/RMSE reporting |

---

## Installation

The bundled scripts require pandas:

```bash
python -m pip install pandas
```

Parquet input also needs `pyarrow` or `fastparquet`. Both scripts accept CSV,
Parquet, JSON, JSONL, and NDJSON and expose `--help` without importing pandas.

---

## What to Measure

1. **Reliability / calibration curve** — bin predicted prob vs observed rate
2. **Expected Calibration Error (ECE)**
3. **Brier score** (+ reliability/resolution decomposition when useful)
4. **Log-loss** — discrimination + calibration together; not a substitute for ECE
5. **Segment calibration** — by season, home/away, probability tail
6. **Sharpness** — are probs informative, not all ~0.5?

Read [calibration_metrics.md](references/calibration_metrics.md) when interpreting ECE, Brier score,
log loss, or sharpness. Read [binning.md](references/binning.md) before choosing bin edges
or minimum counts. Read [recalibration.md](references/recalibration.md) before fitting Platt,
isotonic, or another probability correction.

---

## Workflow

1. Confirm predictions come from time-safe / walk-forward folds.
2. Validate probabilities in `[0, 1]`; account for every excluded row.
3. Pre-declare binning (fixed-width or quantile).
4. Compute curve, ECE, Brier, log-loss.
5. Slice by season and by probability tails.
6. Issue a verdict (table below).
7. If recalibrating, only with nested/train-proper methods — never fit isotonic on the final test fold and call it validated.
8. Write the calibration report into experiment log / results writeup.

---

## Verdict Scale

| Verdict | Meaning |
|---|---|
| `well-calibrated` | Reliability acceptable for quoting probabilities |
| `usable-with-caveats` | Some miscalibration; disclose and/or recalibrate properly |
| `poorly-calibrated` | Probability numbers not trustworthy as probabilities |
| `invalid-eval` | Leakage/split issues block judgment |

These verdicts belong to the full methodology, not to a single ECE threshold.
Before issuing one, verify that predictions are genuinely held out and
walk-forward, inspect uncertainty and populated-bin counts, compare seasons or
folds, check decision-relevant segments, and document the prediction source.
No universal ECE cutoff establishes that probabilities are trustworthy.

---

## Run on Held-Out Prediction Artifacts

The input must contain one row per evaluated decision, a binary outcome, and a
probability in `[0, 1]`.

Preferred portable names from this pack's baseline helper:

- outcome: `y_true`
- probability: `p_pred` (also emitted as `logistic_probability`)

```bash
# After baseline-models/scripts/run_baselines.py --predictions-out ...
python /path/to/calibration-check/scripts/calibration_report.py \
  --input baseline-predictions.csv --target y_true --probability p_pred \
  --group-col season --bins 10 --out calibration.json

python /path/to/calibration-check/scripts/calibration_report.py \
  --input predictions.csv --target won --probability win_probability \
  --group-col season --bins 10 --out calibration.json

python /path/to/calibration-check/scripts/segment_calibration.py \
  --input predictions.csv --target won --probability win_probability \
  --segment-col is_home
```

Use `--filter-col is_home --filter-value 1` for a symmetric team-game artifact
when one home perspective per game is the actual evaluation unit. Do not
double-count both sides of one event.

`calibration_report.py` returns Brier score, log loss, ECE, reliability-bin
counts, row accounting, optional group metrics, and a conservative
`manual-review-required` helper verdict. The script cannot prove held-out
provenance or turn a favorable pooled ECE into `well-calibrated`; the analyst
must apply the verdict scale above. `segment_calibration.py` prints all-row,
categorical-segment, probability-tail metrics, and sparse-bin counts.

---

## Binning Guidance

| Strategy | Use when |
|---|---|
| Equal-width (10 bins 0–1) | default sports win probs |
| Quantile bins | probs clump in a narrow range |
| Tail focus (0–0.2, 0.8–1.0) | decisions live in extremes |

Always report **bin counts**. Empty bins are not evidence.

---

## Recalibration Rules

**Allowed**
- Platt scaling / isotonic fit **inside training folds only**, applied to test fold
- Nested walk-forward recalibration

**Not allowed**
- Fit isotonic on final test labels and call it validated
- Hand-edit probabilities after seeing outcomes

After recalibration, re-report ECE/Brier on true forward folds.

---

## Hard Constraints

1. Never evaluate calibration on training rows used to fit the same model without nested disclosure.
2. Never present raw scores as probabilities without checking calibration.
3. Never hide segment failures behind a pooled “looks fine.”
4. If sample per bin is tiny, say so — widen bins or reduce claim strength.
5. Accuracy is not calibration.
6. Leakage-invalid evaluations cannot be “well-calibrated.”

---

## Anti-Patterns

- “56% correct, so calibrated”
- One reliability plot with no sample sizes
- Holdout isotonic theater
- Average prob ≈ base rate therefore calibrated (necessary, not sufficient)
- Ignoring 0.05 and 0.95 tails
- Quoting NBA/MLB percents without sport-specific calibration

---

## Reporting Template

```text
Calibration report
Sport/model:
Eval: walk-forward seasons …
n:
Brier:
ECE (bins=…):
Log-loss:
Notes by season:
Tail behavior:
Verdict: well-calibrated | usable-with-caveats | poorly-calibrated | invalid-eval
Actions:
Reproduce:
```

---

## Output Contract

Done means:

- [ ] Walk-forward probs used
- [ ] ECE/Brier/log-loss reported
- [ ] Bin counts or segment notes present
- [ ] Verdict issued
- [ ] Actions stated

---

## Worked Example

```bash
python /path/to/calibration-check/scripts/calibration_report.py \
  --input held-out-predictions.csv --target y_true \
  --probability logistic_probability --group-col season \
  --bins 10 --out calibration.json

python /path/to/calibration-check/scripts/segment_calibration.py \
  --input held-out-predictions.csv --target y_true \
  --probability logistic_probability --segment-col is_home
```

Example finding: predictions near 0.70 occur in sparse bins and realize near
0.60. Label the tail unstable or overconfident according to its uncertainty;
do not infer a durable defect from a handful of rows.

---

## Bundled Resources

### references/
| File | Contents |
|---|---|
| [calibration_metrics.md](references/calibration_metrics.md) | ECE/Brier/log-loss definitions |
| [binning.md](references/binning.md) | bin strategy notes |
| [recalibration.md](references/recalibration.md) | allowed recalibration patterns |

### scripts/
| File | Contents |
|---|---|
| `calibration_report.py` | descriptive calibration JSON for supplied prediction rows; provenance must be verified externally |
| `segment_calibration.py` | home/away and tail slices |


---

## Related Skills

| Need | Skill |
|---|---|
| Validation design | `validation-design` |
| Predictive models | `predictive-modeling` |
| Statistical models | `statistical-modeling` |
| Results writeup | `results-reporting` |
| Model card | `model-card` |

---

## Quick Command Card

```bash
python /path/to/calibration-check/scripts/calibration_report.py \
  --input predictions.csv --target won --probability win_probability \
  --group-col season --bins 10 --out calibration.json

python /path/to/calibration-check/scripts/segment_calibration.py \
  --input predictions.csv --target won --probability win_probability \
  --segment-col is_home
```

---
