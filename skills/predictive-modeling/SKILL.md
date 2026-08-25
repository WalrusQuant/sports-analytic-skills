---
name: predictive-modeling
description: Build and evaluate predictive sports models from user-provided modeling data. Use for binary outcome models, feature/model selection, chronological backtests, probability scoring, and comparison to baselines.
metadata:
  version: "0.12.0"
---

# Predictive Modeling for Sports

## Overview

Train and evaluate predictive models on sports data **without leaking the future**.

Goal: a model that beats honest baselines under **walk-forward** evaluation, with
metrics locked before peeking at test folds, and a write-up that states limits.

This skill defines:

- the model ladder (when complexity is allowed)
- metrics by task
- season walk-forward protocol
- leakage rules
- how to extend to new targets
- how to report results

---

## When to Use This Skill

Use this skill when:

- Forecasting game winners, margins, or score-derived targets
- Building player/team prediction models from historical panels
- Comparing ML models against logistic/rating baselines
- Setting up season-based walk-forward training
- User says “build a model,” “predict winners,” or “does ML help here?”

Do **not** use this skill as a substitute for:

| Need | Go to instead |
|---|---|
| Data not loaded yet | use the appropriate loader skill, then return with a user-owned modeling table |
| No EDA yet | `eda-sports` |
| Explanatory inference / GLM writeup | `statistical-modeling` |
| Feature legality unsure | `feature-rules` then `leakage-audit` |
| Only ratings as the model | `ratings-strength-models` |
| Probability reliability deep-dive | `calibration-check` |

---

## Installation

The bundled fold helper requires pandas, NumPy, and scikit-learn:

```bash
python -m pip install pandas numpy scikit-learn
```

Parquet input also needs `pyarrow` or `fastparquet`. The scripts accept CSV,
Parquet, JSON, JSONL, and NDJSON. Optional libraries are imported only after
argument parsing, so `--help` remains available.

---

## Analysis Workflow

Every sound sports predictive analysis follows this arc. Do not skip.

1. **Frame the question before fitting.**
   - Target (win, margin, player stat)
   - Grain (game, team-game, player-game)
   - Decision time T (e.g. scheduled kickoff)
   - Primary metric (lock it now)

2. **Load data** with the right loader skill into a user-owned table.

3. **EDA** (`eda-sports`).
   - n, coverage, missingness, base rates, leakage scouts

4. **Build time-safe features only** (`feature-rules`, `time-series-sports`, `ratings-strength-models`).
   - Every feature must be knowable at T
   - Prefer shifted form / as-of ratings

5. **Create walk-forward folds** (`validation-design`).
   - Default: train on seasons `< S`, test on season `S`

6. **Fit baselines on each fold** (`baseline-models`).
   - Constant rate / mean
   - Home-only or rating-diff logistic/linear
   - Logistic/linear on form features

7. **Fit candidate ML on each fold** only if baselines exist.
   - Default tree model: `HistGradientBoostingClassifier` / regressor

8. **Aggregate metrics across folds.**
   - Mean + per-season table
   - Count how many folds beat the baseline

9. **Calibration check** for probability models (`calibration-check`).

10. **Interpret and report** only if predictive value exists
    (`model-interpretation`, `results-reporting`, `experiment-log`).

Skipping baselines or using random K-fold on seasons is a failed analysis.

Read [model_ladder.md](references/model_ladder.md) before adding model complexity,
[metrics.md](references/metrics.md) before locking the primary score,
[walk_forward.md](references/walk_forward.md) when defining folds, and
[leakage_rules.md](references/leakage_rules.md) before approving the feature set.

---

## Model Ladder

Climb only when the previous rung is beaten on the **primary walk-forward metric**
on multiple folds — not one lucky season.

| Rung | Model | Role |
|---:|---|---|
| 0 | Constant rate / mean target | sanity floor |
| 1 | Home-only or simple rating differential | domain baseline |
| 2 | Logistic / linear on engineered form features | strong classical |
| 3 | HistGradientBoosting / other tabular trees | nonlinear ML |
| 4 | Deeper nets / specialized architectures | only with lots of data + clear gain |

The bundled binary helper implements rungs 0, 2, and 3 for any compatible
user-owned table. It is not an NFL-specific pipeline and does not implement the
regression, ranking, neural-network, encoding, or tuning workflows described
elsewhere in this methodology.

Promotion rule:

- mean primary metric improves vs previous best **and**
- improvement appears on a majority of folds **and**
- no unresolved leakage flags

If trees lose to logistic, **keep logistic**. Complexity is not a virtue.

---

## Metrics

Lock the primary metric **before** fitting candidates.

### Probability / classification (wins, binary events)

| Priority | Metric | Notes |
|---|---|---|
| Primary | **log-loss** | proper scoring rule; default |
| Secondary | Brier score | interpretable MSE of probs |
| Secondary | calibration (ECE / curve) | required before quoting percents |
| Tertiary | accuracy | base-rate sensitive; never alone |

### Regression (margins, counts-as-continuous)

| Priority | Metric | Notes |
|---|---|---|
| Primary | **MAE** | robust headline |
| Secondary | RMSE | penalizes blowups |
| Secondary | bias | systematic over/under by season |

### Ranking tasks

- Spearman / pairwise accuracy on a true holdout period
- Still prefer a proper scoring rule if probabilities exist

See `references/metrics.md`.

---

## Validation Protocol (default)

Use season walk-forward:

```text
train 2018–2019 → test 2020
train 2018–2020 → test 2021
...
```

Represent folds explicitly in the modeling artifact:

```text
fold 1: train groups < 2021 → test 2021
fold 2: train groups < 2022 → test 2022
fold 3: train groups < 2023 → test 2023
```

The split group may be season, date block, event sequence, or another
predeclared chronological unit. The essential property is that every training
row precedes its test rows.

Rules:

- train max season `<` test season
- tune hyperparameters **inside training data only** (nested or fixed a priori)
- never fit scalers/encoders on train+test together
- never early-stop on the true test fold
- report per-fold and mean metrics

Details: `validation-design`, `references/walk_forward.md`.

---

## Standalone Binary Model Comparison

Before fitting, define the target, row grain, decision time, eligible population,
chronological split unit, primary metric, practical success threshold, baseline
ladder, and required prediction artifact.

```bash
python /path/to/predictive-modeling/scripts/run_fold_table.py \
  --input modeling_table.csv --target won --split-col season \
  --features is_home,rating_diff,rest_diff --min-train-groups 2 \
  --id-cols game_id,team --out model-folds.json \
  --predictions-out held-out-predictions.csv
```

The helper compares three candidates on identical expanding folds:

1. training-fold event-rate constant;
2. regularized logistic regression;
3. histogram gradient boosting.

Its JSON output contains the modeling contract, validation design, candidate
ladder, per-fold metrics, and means. The row-level prediction output contains
identifiers, split/fold, `y_true`, and each candidate probability. Pass that
artifact to calibration and interpretation work.

### Modeling-table contract

| Field class | Requirement |
|---|---|
| target | binary 0/1, one value per evaluated decision |
| split column | chronologically sortable and stable |
| features | numeric and legally available at decision time |
| identifiers | enough to reconcile predictions to source events |
| duplicated perspectives | explicitly retained or filtered; never accidental |

The helper keeps rows with missing feature values and places median imputation
inside each fitted candidate. It drops only rows missing the target or split
value, rejects nonnumeric/infinite feature values, and records both counts plus
the number of imputed rows in `row_accounting`. If a feature is entirely
missing in a training fold, the command stops instead of inventing a value.
Any added encoding, scaling, selection, or tuning must also live inside the
fold-local pipeline.

### Custom model loop

For each frozen fold:

```python
train = frame[frame["season"] < test_season]
test = frame[frame["season"] == test_season]

# Fit preprocessing and every candidate only on train.
constant_probability = train["won"].mean()
# Fit a regularized linear/logistic baseline next.
# Fit a nonlinear candidate only after the baseline exists.
# Score all candidates on exactly the same test rows.
```

For continuous outcomes, use a training-mean dummy baseline, then ridge/linear
regression, then a nonlinear regressor only if justified. Prefer MAE when
typical absolute error drives the decision; add RMSE when large errors deserve
extra weight.

### Expected result shape

A credible analysis includes:

- fold-level sample sizes and every candidate metric;
- mean and dispersion across folds;
- candidate-minus-baseline deltas on matched rows;
- held-out predictions for calibration and error analysis;
- an explicit keep/reject decision tied to the predeclared threshold.

If the regularized model does not beat the constant, stop and examine grain,
feature timing, target quality, drift, and data coverage before adding
complexity.

## Hyperparameter Discipline

1. **Default first.** Use package defaults / modest trees before search.
2. **Tune inside training only.** Nested walk-forward or a fixed inner validation season.
3. **Small search spaces.** Depth, learning rate, max_iter — not kitchen-sink grids.
4. **One locked config for final fold metrics.** Do not refit after seeing the answer.
5. **Report the config** in the experiment log.

Anti-pattern: repeatedly tweaking until the last season looks good.

---

## Leakage Rules (Non-Negotiable)

1. No `points_for` / `points_against` / `won` / current-game EPA as pre-game features.
2. No final-season aggregates applied backward onto early weeks.
3. No opponent “season stats” that include the current matchup.
4. No target encoding fit on the full shuffled dataset.
5. No scaler/imputer fit on train+test together.
6. If a feature needs same-game information, the task is no longer pre-game — redefine T.

Checks:

```bash
python /path/to/predictive-modeling/scripts/leakage_smoke.py \
  --input modeling_table.csv --target won \
  --features is_home,rating_diff,rest_diff
```

See `references/leakage_rules.md`.

---

## Interpreting Results

### Good outcome

- logistic and/or ML primary metric beats constant on **most** folds
- home / strength effects point the right way
- no single season carries the entire claim
- calibration not catastrophic (`calibration-check`)

### Bad outcome

- beats baseline only in one season
- huge tree gains on tiny data
- train metrics great, walk-forward dead
- perfect accuracy / absurd log-loss → assume leakage until proven otherwise

### Decision table

| Result | Action |
|---|---|
| ML < logistic < constant (lower log-loss better) | ship simplest winner; log experiment |
| logistic ≈ ML, both beat constant | prefer logistic unless trees win clearly on multiple folds |
| neither beats constant | debug features/EDA/leakage; do not add complexity |
| only one season wins | do not claim generalization |

---

## Reporting Template

```text
Predictive model report
Question: …
Sport/league: …
Grain: …
Decision time T: …
Target: …
Features: … (all knowable at T: yes/no)
Baselines: constant; logistic form; (optional rating)
Candidate models: …
Validation: season walk-forward, min_train_seasons=…
Primary metric: …
Mean walk-forward metrics: …
Per-season table: …
Calibration: …
Leakage audit: CLEAN / NOT CLEAN
Decision: keep logistic | keep ML | discard | follow-up
Limits: …
Reproduce:
  python /path/to/predictive-modeling/scripts/run_fold_table.py --input …
```

Also use `results-reporting` and `experiment-log`.

---

## Bundled Resources

### references/

| File | Contents |
|---|---|
| [model_ladder.md](references/model_ladder.md) | when to climb complexity |
| [metrics.md](references/metrics.md) | metric definitions and pitfalls |
| [walk_forward.md](references/walk_forward.md) | fold design details |
| [leakage_rules.md](references/leakage_rules.md) | predictive leakage checklist |

### scripts/

| File | Contents |
|---|---|
| `leakage_smoke.py` | fast column, target, and suspicious-name checks on a supplied feature set |
| `run_fold_table.py` | compare constant/logistic/GBM on expanding folds and optionally save predictions |


---

## Integrity Rules

1. Lock target, T, and primary metric before candidate fitting.
2. Always run baselines.
3. Walk-forward over random season shuffles.
4. Do not drop ugly seasons after seeing scores.
5. Do not tune on the final test season.
6. Report failures and non-improvements.
7. Log the experiment (`experiment-log`).

---

## Related Skills

| Need | Skill |
|---|---|
| Doctrine / charter | `sports-modeling-doctrine` |
| EDA | `eda-sports` |
| Features | `feature-rules`, `time-series-sports` |
| Ratings features | `ratings-strength-models` |
| Baselines only | `baseline-models` |
| GLM inference | `statistical-modeling` |
| Validation design | `validation-design` |
| Leakage | `leakage-audit` |
| Calibration | `calibration-check` |
| Interpretation | `model-interpretation` |
| Writeup | `results-reporting`, `model-card` |

---

## Quick Command Card

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

---
