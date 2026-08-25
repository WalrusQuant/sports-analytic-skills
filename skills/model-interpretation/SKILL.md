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

# Model Interpretation (Sports)

## Overview

Explain model behavior **after** evaluation — never instead of evaluation.

Interpretation answers:

- what the model relies on
- where it fails
- whether failures concentrate (season, home/away, probability tails)
- whether the story is stable enough to put in a model card

It does **not** turn a losing walk-forward into a win.

Work from held-out prediction tables, fold summaries, and model-specific coefficient or importance artifacts.

---

## When to Use This Skill

Use when:

- After win / margin / Elo pipelines finish
- Debugging bad folds
- Writing results or model cards
- User asks “why,” “largest misses,” “where does it break,” “what drives this”
- Comparing two models on the same walk-forward folds

Do **not** use when:

| Need | Go instead |
|---|---|
| No held-out predictions yet | `predictive-modeling` first |
| Leakage still open | `leakage-audit` |
| Pure presentation cleanup | `anti-slop-analytics` |
| Only global metrics writeup | `results-reporting` |
| Probability reliability deep-dive | `calibration-check` |

---

## Installation

The bundled helpers require pandas and NumPy:

```bash
python -m pip install pandas numpy
```

Parquet input also needs `pyarrow` or `fastparquet`. Inputs may be CSV,
Parquet, JSON, JSONL, or NDJSON.

---

## Required Inputs

Minimum:

- Walk-forward metrics (pipeline JSON or fold table)
- Predictions + actuals with stable reconciliation keys and a fold/season label;
  team, opponent, and home/away context when those slices are needed
- Baseline metrics on the same folds
- Leakage audit status

Optional:

- Feature matrix used at fit time
- Coefficients / importances
- Calibration table

---

## Analysis Workflow

Do not skip.

1. **Confirm evaluation is walk-forward** (not in-sample flex).
2. **Restate global metrics with baseline** before any story.
3. **Confirm leakage status is CLEAN** (or stop).
4. **Slice errors** by season, home/away, probability bins, margin buckets.
5. **List largest misses** with context (favorite blown out, early season, etc.).
6. **Read drivers carefully**
   - linear: coefficients with scale/standardization caveats
   - trees: slice stability over one importance bar chart
7. **Check calibration context** for probability models.
8. **Write limits** — what interpretation cannot claim.
9. **Hand off** to `results-reporting` / `model-card` / next experiment.

---

## Slice Menu (do at least two)

| Slice | Question |
|---|---|
| Season / fold | Does one year carry the mean? |
| Home vs away | Is edge only one side of the panel? |
| Probability tails | Are 10% and 90% calls reliable? |
| Early season (`pre_games_played` low) | Cold-start failure? |
| Large absolute `elo_diff` or form gap | Does it fail on “easy” games too? |
| Blowout residuals (margin) | Systematic scale miss? |

Guide: [slice_guide.md](references/slice_guide.md)
Methods: [interpretation_methods.md](references/interpretation_methods.md)
Use [miss_taxonomy.md](references/miss_taxonomy.md) when classifying large errors and deciding
which failures suggest data repair, a new feature, drift handling, or no action.

---

## Standalone Helpers

```bash
python /path/to/model-interpretation/scripts/slice_errors.py \
  --input held-out-predictions.csv --slice-cols fold --out slices.json

python /path/to/model-interpretation/scripts/largest_misses.py \
  --input held-out-predictions.csv \
  --columns fold,source_row --top 25
```

The defaults (`y_true`, `logistic_probability`, and the `fold` slice) match the
prediction artifact emitted by `predictive-modeling/scripts/run_fold_table.py`.
Use `--actual-col`, `--prob-col`, and `--slice-cols` for another candidate or
schema. Preserve context fields with the predictive helper's `--id-cols` if
you need team, opponent, or home/away slices. The scripts validate binary
outcomes and probability bounds. For symmetric team-game artifacts, add
`--filter-col is_home --filter-value 1` so each event is evaluated once.

These helpers cover probability-error tables only. Coefficient scaling,
permutation importance, causal interpretation, margin residuals, and model
stability require the external model artifacts and methods described below;
the bundled scripts do not compute them.

---

## Coefficient / Driver Rules

### Logistic / linear
- Report direction + magnitude with feature scale
- Standardized features: coefficient is per-SD effect
- Do not call it causal without design
- Check VIF / collinearity before story-time (form diffs often collinear)

### Trees / GBM
- Prefer permutation importance on held-out folds if used at all
- Require stability across seasons before believing a top feature
- A pretty importance chart is not lift

### Elo models
- `elo_diff` dominating is expected — say so
- Interpretation is mostly “rating gap + home,” not mysterious structure

---

## Largest Misses Protocol

For each miss report:

1. season, week/date, team, opponent, is_home
2. y vs p_hat (or margin residual)
3. model edge (favorite/underdog)
4. simple context features (form gap, elo gap, rest if present)
5. whether this miss type clusters

Never only show the funniest blowup.

---

## Hard Constraints

1. Never interpret a model that failed leakage.
2. Never treat coefficient sign as causal without design.
3. Never hide slices where the model loses.
4. Probability tails need calibration context.
5. One season hero story is not generalization.
6. Global metric + baseline must appear before narrative.
7. If slices conflict with the mean story, the mean story is incomplete.

---

## Anti-Patterns

- Feature importance theater without metric lift
- Explaining noise as narrative
- Only best-case slices
- Confusing form features with “true team quality”
- Post-hoc story after seeing test labels without labeling it post-hoc
- “The model understands matchups” without slice evidence

---

## Reporting Template

```text
Model:
Sport / target / T:
Walk-forward window:
Global metrics vs baseline:
Leakage status:
Slices:
  - season:
  - home/away:
  - tails:
Largest misses:
Stable drivers:
Unstable / discarded stories:
Limits:
Next test:
```

---

## Output Contract

Done means:

- [ ] Global metrics restated with baseline
- [ ] Leakage status stated
- [ ] At least two slices reported
- [ ] Largest misses listed with context
- [ ] Driver claims caveated
- [ ] Limits of interpretation stated
- [ ] Next test named if follow-up needed

---

## Worked Example

**NFL form logistic, 2018–2024 walk-forward**

1. Mean log-loss beats constant → proceed
2. Leakage CLEAN
3. Slice by season: check if 2020 or one year carries it
4. Slice home/away: both should beat constant if the model is real
5. Tails: run `calibration-check/scripts/calibration_report.py` and inspect bin counts
6. Largest misses: road dogs that won, or huge favorites that lost
7. Writeup: “beats constant on most folds; weak on early-season low-sample rows”

---

## Bundled Resources

### references/
- [interpretation_methods.md](references/interpretation_methods.md)
- [slice_guide.md](references/slice_guide.md)
- [miss_taxonomy.md](references/miss_taxonomy.md)

### scripts/
- `slice_errors.py`
- `largest_misses.py`

---

## Related Skills

- `results-reporting`
- `calibration-check`
- `model-card`
- `predictive-modeling`
- `statistical-modeling`
- `experiment-log`

---

## Quick Command Card

```bash
python /path/to/model-interpretation/scripts/slice_errors.py \
  --input held-out-predictions.csv --slice-cols fold --out slices.json

python /path/to/model-interpretation/scripts/largest_misses.py \
  --input held-out-predictions.csv \
  --columns fold,source_row --top 25
```

---
