---
name: predictive-modeling
description: >
  Predictive machine learning for sports outcomes with time-safe features,
  baselines-first workflow, season walk-forward validation, metric selection,
  hyperparameter discipline, and complete reporting. Use whenever forecasting
  wins, margins, player stats, or rankings after EDA and simple baselines exist
  — even if the user only says "build a model" or "will this beat the baseline."
  Covers the model ladder (constant → logistic/linear → trees), leakage-safe
  training, the sports_ds NFL win pipeline, custom target extension patterns,
  and calibration handoff. For classical inference/GLMs see statistical-modeling;
  for feature legality see feature-rules and leakage-audit.
version: "0.4.0"
license: MIT
metadata:
  version: "0.4.0"
---

# Predictive Modeling for Sports

## Overview

Train and evaluate predictive models on sports data **without leaking the future**.

Goal: a model that beats honest baselines under **walk-forward** evaluation, with
metrics locked before peeking at test folds, and a write-up that states limits.

This skill is operational. It drives the `sports_ds` toolkit and defines:

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
| Data not loaded yet | `nflreadpy` / `sportsdataverse-py` / `pybaseball` / `sports_ds.data` |
| No EDA yet | `eda-sports` |
| Explanatory inference / GLM writeup | `statistical-modeling` |
| Feature legality unsure | `feature-rules` then `leakage-audit` |
| Only ratings as the model | `ratings-strength-models` |
| Probability reliability deep-dive | `calibration-check` |

---

## Installation

```bash
# from repo root
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pytest -q
```

Core stack (via `sports_ds`):

- `pandas`, `numpy`, `scikit-learn`, `scipy`, `statsmodels`, `matplotlib`
- `nflreadpy` for NFL loads

Optional:

```bash
pip install -e ".[multi]"          # SportsDataverse, pybaseball
pip install "pingouin>=0.6" seaborn
```

**Notes:**

- First nflverse download needs network; later runs use cache
- Prefer running commands from repo root with venv active
- Python 3.10+

---

## Analysis Workflow

Every sound sports predictive analysis follows this arc. Do not skip.

1. **Frame the question before fitting.**
   - Target (win, margin, player stat)
   - Grain (game, team-game, player-game)
   - Decision time T (e.g. scheduled kickoff)
   - Primary metric (lock it now)

2. **Load data** with the right loader skill / `sports_ds.data`.

3. **EDA** (`eda-sports` / `sports-ds nfl-eda`).
   - n, coverage, missingness, base rates, leakage scouts

4. **Build time-safe features only** (`feature-rules`, `time-series-sports`, `ratings-strength-models`).
   - Every feature must be knowable at T
   - Prefer shifted form / as-of ratings

5. **Create walk-forward folds** (`validation-design` / `sports_ds.validation`).
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

**Default implemented NFL pipeline uses rungs 0, 2, and 3.**

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

Implemented by:

```python
from sports_ds.validation.splits import season_walk_forward_masks

for test_season, train_mask, test_mask in season_walk_forward_masks(df, min_train_seasons=2):
    ...
```

Rules:

- train max season `<` test season
- tune hyperparameters **inside training data only** (nested or fixed a priori)
- never fit scalers/encoders on train+test together
- never early-stop on the true test fold
- report per-fold and mean metrics

Details: `validation-design`, `references/walk_forward.md`.

---

## End-to-End: NFL Team Win Model

### CLI (preferred)

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win_pipeline.json
```

### What the pipeline does

1. loads nflverse schedules via `nflreadpy` (`sports_ds.data.nfl`)
2. expands to **team-game** panel
3. engineers shifted pre-game form features
4. drops rows with insufficient prior games (default ≥ 3 each side)
5. walk-forward evaluates:
   - constant train win-rate
   - logistic baseline on form features
   - hist gradient boosting
6. prints mean + per-season metrics

### Python API

```python
from sports_ds.pipelines.nfl_win_model import run_nfl_win_pipeline, format_pipeline_report

result = run_nfl_win_pipeline(seasons=list(range(2018, 2025)))
print(format_pipeline_report(result))

# keys of interest:
# result["mean_metrics"]
# result["folds"]
# result["beats_constant_logistic"]
# result["beats_constant_hist_gbm"]
# result["feature_cols"]
```

### Feature set used

From `sports_ds.features.team_form.add_pregame_form_features`:

| Feature | Meaning |
|---|---|
| `is_home` | 1 if home team row |
| `feature_win_pct_diff` | pre-game win% − opponent pre-game win% |
| `feature_diff_diff` | pre-game avg point diff − opponent |
| `feature_roll3_win_diff` | roll3 win% differential |
| `feature_roll5_diff_diff` | roll5 point-diff differential |
| `pre_games_played` | prior games for team |
| `opp_pre_games_played` | prior games for opponent |

All rolling/expanding stats use **`shift(1)`** (current game excluded).

Code: `src/sports_ds/features/team_form.py`  
Feature list constant: `sports_ds.pipelines.nfl_win_model.FEATURE_COLS`

### Typical result shape (illustrative)

Walk-forward means will vary by season window. A healthy run looks like:

- constant log-loss near ~0.69 for balanced win labels on team-game panels
- logistic log-loss **below** constant on most seasons
- hist GBM competitive with logistic; sometimes slightly better/worse
- accuracy only as a secondary note

If logistic does not beat constant, **stop and debug features/leakage/EDA** before adding trees.

---

## Custom Model Loop (any feature set)

```python
from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.validation.splits import season_walk_forward_masks
from sports_ds.models.predict import fit_win_classifier
from sports_ds.models.baselines import baseline_home_rate, fit_logistic_baseline

panel = load_team_game_panel(list(range(2018, 2025)))
df = add_pregame_form_features(panel)
features = [
    "is_home",
    "feature_win_pct_diff",
    "feature_diff_diff",
    "feature_roll3_win_diff",
    "feature_roll5_diff_diff",
]
df = df.dropna(subset=features + ["won"])
df = df[(df.pre_games_played >= 3) & (df.opp_pre_games_played >= 3)]

rows = []
for season, tr, te in season_walk_forward_masks(df, min_train_seasons=2):
    const = baseline_home_rate(df, tr, te)
    _, log_res, log_prob = fit_logistic_baseline(df, features, tr, te)
    _, gbm_res, gbm_df = fit_win_classifier(df, features, tr, te, model_type="hist_gbm")
    rows.append(
        {
            "season": season,
            "n_test": int(te.sum()),
            "const_ll": const.log_loss,
            "log_ll": log_res.log_loss,
            "gbm_ll": gbm_res.log_loss,
            "log_acc": log_res.accuracy,
            "gbm_acc": gbm_res.accuracy,
        }
    )

import pandas as pd
print(pd.DataFrame(rows).to_string(index=False))
```

### Margin regression pattern

```python
# Conceptual pattern — implement a pipeline module when promoting to package code.
# Target: point_diff on home rows only (one row per game)
# Models: DummyRegressor(mean) → Ridge/LinearRegression → HistGradientBoostingRegressor
# Metric: MAE primary
home = df[df.is_home == 1].copy()
# ... season_walk_forward_masks(home) ...
# fit on feature_cols, evaluate MAE/RMSE on test fold
```

Add production targets as new modules under `src/sports_ds/pipelines/`.

---

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
python skills/predictive-modeling/scripts/leakage_smoke.py
python skills/leakage-audit/scripts/audit_pregame_features.py --seasons 2023-2024
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
  sports-ds nfl-win-pipeline --seasons …
```

Also use `results-reporting` and `experiment-log`.

---

## Bundled Resources

### references/

| File | Contents |
|---|---|
| `model_ladder.md` | when to climb complexity |
| `metrics.md` | metric definitions and pitfalls |
| `walk_forward.md` | fold design details |
| `leakage_rules.md` | predictive leakage checklist |

### scripts/

| File | Contents |
|---|---|
| `leakage_smoke.py` | smoke checks that pre-game features are shifted |
| `run_fold_table.py` | print walk-forward const/logistic/GBM table |

### package code

- `src/sports_ds/pipelines/nfl_win_model.py`
- `src/sports_ds/models/baselines.py`
- `src/sports_ds/models/predict.py`
- `src/sports_ds/features/team_form.py`
- `src/sports_ds/validation/splits.py`

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
pip install -e .
sports-ds nfl-eda --seasons 2023-2024
sports-ds nfl-win-pipeline --seasons 2018-2024
python skills/predictive-modeling/scripts/leakage_smoke.py
python skills/predictive-modeling/scripts/run_fold_table.py --seasons 2018-2024
python skills/calibration-check/scripts/calibration_report.py --seasons 2018-2024
```
