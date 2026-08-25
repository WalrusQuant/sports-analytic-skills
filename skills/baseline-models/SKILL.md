---
name: baseline-models
description: Design and evaluate simple sports prediction baselines before accepting more complex models. Use for constant-rate, home-advantage, logistic, Elo-style, or market-reference comparisons.
metadata:
  version: "0.12.0"
---

# Baseline Models for Sports

## Overview

If a fancy model cannot beat simple baselines under time-safe validation, it is
not progress.

This skill defines the **baseline ladder** and standardizes matched, chronological comparison before ML.

Baselines are not disposable. Often they are the ship candidate.

---

## When to Use This Skill

Use when:

- Starting a predictive sports project
- Auditing an ML result that looks shiny
- Building the first model you might actually keep
- User says “what’s the baseline?” or “does this beat home field?”
- Comparing form vs Elo vs constant on NFL/NBA/MLB

Do **not** skip this skill and jump to trees.

| Need | Go instead |
|---|---|
| Validation folds | `validation-design` |
| Features | `feature-rules` |
| ML candidates after baselines | `predictive-modeling` |
| GLM inference writeup | `statistical-modeling` |
| Ratings baseline detail | `ratings-strength-models` |

---

## Installation

`run_baselines.py` requires pandas, NumPy, and scikit-learn;
`home_only_baseline.py` requires pandas:

```bash
python -m pip install pandas numpy scikit-learn
```

Parquet input also needs `pyarrow` or `fastparquet`. Both scripts expose
`--help` before optional libraries are imported.

---

## Baseline Ladder

| Tier | Baseline | Implemented here |
|---|---|---|
| A | Constant training-fold win rate / mean target | required |
| B | Home-only logistic / mean home margin | pattern + script |
| C | Logistic/linear on home + legal form differentials | bundled fold helper |
| D | Rating differential logistic/linear | ratings skill or supplied rating column |

Climb to ML only after Tier A–C (or A–D) exist under walk-forward evaluation.

The bundled fold helper implements binary Tier A and a numeric-feature Tier C
logistic model. Tier B descriptive summaries have a separate helper; Elo,
market, regression, and other ladder entries are methodology that require
their own matched prediction artifacts.

Read [references/baseline_ladder.md](references/baseline_ladder.md) when selecting the minimum credible ladder
and promotion rule. Read [references/interpretation.md](references/interpretation.md) when deciding whether a
candidate's delta is stable and practically meaningful.

---

## Workflow

1. Define target + primary metric.
2. Build legal features (`feature-rules`).
3. Create walk-forward folds (`validation-design`).
4. Fit Tier A constant baseline each fold.
5. Fit Tier C logistic/linear baseline each fold.
6. Optional: rating-difference or market-reference baseline.
7. Compare per-fold and mean metrics.
8. Only then try ML (`predictive-modeling`).
9. Keep the simplest model that wins.
10. Log the experiment.

---

## Run Baselines

Work from a user-owned table and use identical rows, folds, target, and scoring
rules for every candidate.

```bash
python /path/to/baseline-models/scripts/run_baselines.py \
  --input games.csv --target won --split-col season \
  --features is_home,rating_diff,rest_diff \
  --id-cols game_id,team --out baseline-folds.json \
  --predictions-out baseline-predictions.csv

python /path/to/baseline-models/scripts/home_only_baseline.py \
  --input games.csv --target won --home-col is_home
```

`run_baselines.py` evaluates a training-rate constant and regularized logistic
baseline on expanding chronological folds. Its JSON artifact records the
modeling contract, validation design, model names, per-fold metrics, means, and
complete-case row accounting. It performs no imputation: rows missing target,
split, or any named feature are excluded from both candidates and counted.

**`--min-train-groups` default is 2.** With seasons `[2022, 2023, 2024]`, only
2024 is tested (train on 2022+2023). Use `--min-train-groups 1` to also test
2023. The helper prints the planned test folds on stderr before scoring.

The prediction table writes identifiers, split/fold, `y_true`,
`constant_probability`, `logistic_probability`, and portable `p_pred`
(alias of the logistic probability for handoff).

Direct handoff to calibration:

```bash
python /path/to/calibration-check/scripts/calibration_report.py \
  --input baseline-predictions.csv --target y_true --probability p_pred \
  --group-col season --out calibration.json
```

The home-only helper reports group rates and a continuity-corrected odds ratio
with a Wald interval. Treat it as pooled descriptive inference unless it is
embedded in a chronological evaluation; it does not by itself establish
predictive generalization.

---

## Tier Details

### Tier A — Constant rate
The constant baseline predicts the training-fold mean of the target for every test row.
On balanced team-game panels this is near 0.5 and log-loss near ~0.693.

### Tier B — Home only
```bash
python /path/to/baseline-models/scripts/home_only_baseline.py \
  --input games.csv --target won --home-col is_home
```

### Tier C — Form logistic
Uses a small declared set of legal pre-event form differentials.

### Tier D — Rating differential
Use a pre-event rating-difference column supplied in the modeling table and
evaluate it on the same rows and folds as the other baselines.

---

## What “Good” Looks Like

- Logistic log-loss < constant on **most** folds
- Coefficients point the right way (home effect positive in log-odds)
- Gains are not from one freak season only
- If trees barely beat logistic, **prefer logistic**

### Decision table

| Result | Action |
|---|---|
| C beats A on most folds | strong baseline; ML must beat C |
| C fails to beat A | debug features/leakage before ML |
| D beats C | consider ratings as primary features |
| ML ≈ C | ship C |

---

## Hard Constraints

1. No predictive project without Tier A.
2. Walk-forward only for claims of generalization.
3. Do not hide folds where baseline wins.
4. Simplest winning model is the default ship candidate.
5. Cross-sport claims require sport-specific evaluation; do not assume transportability.

---

## Anti-Patterns

- Jumping to GBM with no constant baseline
- Reporting accuracy without log-loss/MAE
- One-season hero baselines
- Calling home-rate on the full doubled panel “home advantage”
- Hiding folds where ML loses to logistic

---

## Reporting Template

```text
Baseline report
Sport/target/T:
Features:
Validation: season walk-forward
Tier A mean metric:
Tier C mean metric:
Tier D mean metric (if any):
Per-season table:
Decision: promote to ML | keep logistic | debug features
Reproduce:
```

---

## Output Contract

Done means:

- [ ] Tier A present
- [ ] At least one stronger baseline (B/C/D) present
- [ ] Walk-forward comparison table present
- [ ] Decision stated
- [ ] Repro commands present

---

## Bundled Resources

### references/
| File | Contents |
|---|---|
| [baseline_ladder.md](references/baseline_ladder.md) | ladder and promotion rules |
| [interpretation.md](references/interpretation.md) | how to read baseline comparisons |

### scripts/
| File | Contents |
|---|---|
| `run_baselines.py` | const vs logistic walk-forward table |
| `home_only_baseline.py` | pooled home/away rates and a continuity-corrected descriptive odds ratio; not a fitted walk-forward predictor |


---

## Related Skills

| Need | Skill |
|---|---|
| Features | `feature-rules` |
| Validation | `validation-design` |
| ML | `predictive-modeling` |
| GLM writeup | `statistical-modeling` |
| Ratings | `ratings-strength-models` |
| Calibration | `calibration-check` |

---

## Quick Command Card

```bash
python /path/to/baseline-models/scripts/run_baselines.py \
  --input games.csv --target won --split-col season \
  --features is_home,rating_diff,rest_diff \
  --id-cols game_id,team --out baseline-folds.json \
  --predictions-out baseline-predictions.csv

python /path/to/baseline-models/scripts/home_only_baseline.py \
  --input games.csv --target won --home-col is_home
```

---
