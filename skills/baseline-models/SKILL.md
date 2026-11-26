---
name: baseline-models
description: Design and evaluate simple sports prediction baselines before accepting more complex models. Use for constant-rate, home-advantage, logistic, Elo-style, or market-reference comparisons.
license: MIT
metadata:
  version: "1.0.0"
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

Fit baselines in the user's environment. A binary comparison needs pandas, NumPy, and scikit-learn:

```bash
python -m pip install pandas numpy scikit-learn pyarrow
```

Read Parquet with pandas or DuckDB. This repository does not ship the fitting code.

---

## Baseline Ladder

| Tier | Baseline | Implemented here |
|---|---|---|
| A | Constant training-fold win rate / mean target | required |
| B | Home-only rate or mean home margin | descriptive, then fold-local if used as a forecast |
| C | Logistic/linear on home + legal form differentials | fit inside each training fold |
| D | Rating differential logistic/linear | `ratings-strength-models` or a supplied as-of rating column |

Climb to ML only after Tier A–C (or A–D) exist under walk-forward evaluation.

Fit Tier A and Tier C on the same rows. A home-only rate is a pooled description until it is scored on the same chronological folds. Elo, a user-supplied market probability, and other ladder entries need their own matched prediction column.

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

Work from a user-owned table, usually a sportsleader-data Parquet file chosen with `data-sources`, and use identical rows, folds, target, and scoring rules for every candidate.

Score a training-rate constant and a regularized logistic baseline on expanding chronological folds. Record the modeling contract, validation design, model names, per-fold metrics, means, and complete-case row accounting. Do not impute inside the baseline comparison: rows missing the target, split, or any named feature are excluded from both candidates and counted.

**Minimum training groups default to 2.** With seasons `[2022, 2023, 2024]`, only 2024 is tested (train on 2022+2023). Use one training group when 2023 should also be a test fold. Print the planned test folds before scoring.

The prediction table should keep identifiers, split/fold, `y_true`, `constant_probability`, `logistic_probability`, and `p_pred` (the logistic probability, for `calibration-check`).

A home-only summary can report group rates and a continuity-corrected odds ratio with a Wald interval. Treat that as pooled descriptive inference unless the same home indicator is scored inside the chronological folds. It does not by itself establish predictive generalization.

`panel` is the team-game panel from `data-sources`. Score each fold with log loss and Brier score, and keep the prediction rows `calibration-check` reads.

```python
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss

df = panel.dropna(subset=["won", "season", "is_home"]).copy()
df["is_home"] = df["is_home"].astype(int)
df["won"] = df["won"].astype(int)
fold_rows, pred_rows = [], []
for season in sorted(df["season"].unique())[2:]:
    train = df[df["season"] < season]
    test = df[df["season"] == season]
    constant = float(train["won"].mean())
    model = LogisticRegression(max_iter=500)
    model.fit(train[["is_home"]], train["won"])
    y = test["won"].to_numpy()
    p_const = [constant] * len(test)
    p_model = model.predict_proba(test[["is_home"]])[:, 1]
    fold_rows.append({
        "season": int(season),
        "n": len(test),
        "log_loss_constant": log_loss(y, p_const),
        "log_loss_home": log_loss(y, p_model),
        "brier_constant": brier_score_loss(y, p_const),
        "brier_home": brier_score_loss(y, p_model),
    })
    part = test[["game_id", "team", "season"]].copy()
    part["y_true"] = y
    part["constant_probability"] = p_const
    part["logistic_probability"] = p_model
    part["p_pred"] = p_model
    pred_rows.append(part)
print(pd.DataFrame(fold_rows))
predictions = pd.concat(pred_rows, ignore_index=True)
```

---

## Tier Details

### Tier A — Constant rate
The constant baseline predicts the training-fold mean of the target for every test row.
On balanced team-game panels this is near 0.5 and log-loss near ~0.693.

### Tier B — Home only

Report the home-row win rate or the mean home margin. When that rate is used as a forecast, score a home indicator on the same walk-forward folds as Tier A. A pooled rate is a description, not a held-out result.

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

## References

### references/
| File | Contents |
|---|---|
| [baseline_ladder.md](references/baseline_ladder.md) | ladder and promotion rules |
| [interpretation.md](references/interpretation.md) | how to read baseline comparisons |

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
