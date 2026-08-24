---
name: predictive-modeling
description: >
  Predictive machine learning for sports outcomes using time-safe features,
  baselines-first workflow, and season walk-forward validation. Use when
  forecasting wins, margins, player stats, or rankings after EDA and simple
  baselines exist. Covers model ladder (logistic → trees), leakage-safe
  training, metric selection, and the sports_ds NFL win pipeline.
version: "0.3.0"
license: MIT
metadata:
  version: "0.3.0"
---

# Predictive Modeling for Sports

## Overview

Train and evaluate predictive models on sports data without leaking the future.
This skill is operational: it runs through the `sports_ds` toolkit and defines
the standard model ladder, metrics, and validation protocol.

Goal: a model that beats honest baselines under walk-forward evaluation.

## When to Use This Skill

Use when:

- Forecasting game winners, margins, totals-like targets derived from scores
- Building player/team prediction models from historical panels
- Comparing ML models against logistic/rating baselines
- Setting up season-based walk-forward training

Do not use when:

- You still need data loaded → package/data skills + `sports_ds.data`
- You have not inspected the panel → `eda-sports`
- You need explanatory inference only → `statistical-modeling`
- Features may be leaked → `feature-rules` / `leakage-audit` first

---

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pytest -q
```

---

## Standard Workflow

1. **Define target + decision time T**
2. **Load panel** (`sports_ds.data`)
3. **EDA** (`sports-ds nfl-eda` or `eda-sports`)
4. **Build time-safe features only**
5. **Create walk-forward folds by season**
6. **Fit baselines on each fold**
7. **Fit candidate ML on each fold**
8. **Aggregate metrics across folds**
9. **Interpret only if predictive value exists**
10. **Log the experiment**

Skipping baselines or using random K-fold on seasons is a failed analysis.

---

## Model Ladder

Climb only when the previous rung is beaten on walk-forward log-loss/MAE.

| Rung | Model | Role |
|---|---|---|
| 0 | Constant rate / mean | sanity floor |
| 1 | Home-only or simple rating differential logistic/linear | domain baseline |
| 2 | Logistic/linear on engineered form features | strong classical |
| 3 | HistGradientBoosting / GBM trees | nonlinear tabular ML |
| 4 | Deeper nets / special architectures | only with lots of data + clear gain |

Default implemented pipeline uses rungs 0, 2, and 3.

---

## Metrics

### Classification / probability

- **Primary:** log-loss
- **Secondary:** Brier, calibration
- **Tertiary:** accuracy (base-rate sensitive; never primary alone)

### Regression

- MAE, RMSE
- residual diagnostics by season

---

## End-to-End: NFL Team Win Model

### CLI (preferred)

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win_pipeline.json
```

What it does:

1. loads nflverse schedules via `nflreadpy`
2. expands to team-game panel
3. engineers shifted pre-game form features
4. walk-forward validates:
   - constant train win-rate
   - logistic baseline
   - hist gradient boosting
5. prints mean + per-season metrics

### Python API

```python
from sports_ds.pipelines.nfl_win_model import run_nfl_win_pipeline, format_pipeline_report

result = run_nfl_win_pipeline(seasons=list(range(2018, 2025)))
print(format_pipeline_report(result))
```

### Feature set used

From `sports_ds.features.team_form.add_pregame_form_features`:

- `is_home`
- `feature_win_pct_diff`
- `feature_diff_diff`
- `feature_roll3_win_diff`
- `feature_roll5_diff_diff`
- prior games played counts

All rolling/expanding stats use `shift(1)` (no current game).

### Validation

`sports_ds.validation.season_walk_forward_masks`:

- test season = S
- train seasons = all < S
- requires `min_train_seasons` (default 2)

---

## Custom Model Extension Pattern

```python
from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.validation.splits import season_walk_forward_masks
from sports_ds.models.predict import fit_win_classifier, evaluate_classifier
from sports_ds.models.baselines import baseline_home_rate

panel = load_team_game_panel(list(range(2018, 2025)))
df = add_pregame_form_features(panel).dropna()
features = ["is_home", "feature_win_pct_diff", "feature_diff_diff"]

for season, tr, te in season_walk_forward_masks(df):
    base = baseline_home_rate(df, tr, te)
    model, res, pred = fit_win_classifier(df, features, tr, te, model_type="hist_gbm")
    print(season, base.log_loss, res.log_loss, res.accuracy)
```

Add new targets by creating a new pipeline module under `src/sports_ds/pipelines/`.

---

## Leakage Rules (Non-Negotiable)

1. No points_for/points_against/won from the current game as features.
2. No final-season aggregates applied backward onto early weeks.
3. No opponent “season stats” that include the current matchup.
4. No tuning on the final test season repeatedly until it looks good.
5. If a feature needs same-game information, the task is no longer pre-game.

Use `python skills/predictive-modeling/scripts/leakage_smoke.py` for a quick check.

---

## Interpreting Results

**Good outcome**

- logistic/ML log-loss < constant on most folds
- stable home effect
- no single season carries the entire claim

**Bad outcome**

- beats baseline only in one season
- astronomical tree depth gains with tiny data
- train metrics great, walk-forward dead

When ML loses to logistic, keep logistic. Complexity is not a virtue.

---

## Bundled Resources

### references/

- `model_ladder.md` — when to climb complexity
- `metrics.md` — metric definitions and pitfalls

### scripts/

- `leakage_smoke.py` — asserts shifted features don’t equal current outcomes
- (pipeline itself lives in package)

### package code

- `src/sports_ds/pipelines/nfl_win_model.py`
- `src/sports_ds/models/`
- `src/sports_ds/features/team_form.py`
- `src/sports_ds/validation/splits.py`

---

## Handoffs

| Next need | Skill / command |
|---|---|
| EDA | `eda-sports`, `sports-ds nfl-eda` |
| Classical inference writeup | `statistical-modeling` |
| Calibration plots/metrics | `calibration-check` |
| Ratings features | `ratings-strength-models` |
| Report | `results-reporting` |

---

## Command Card

```bash
pip install -e .
sports-ds nfl-eda --seasons 2023-2024
sports-ds nfl-win-pipeline --seasons 2018-2024
python skills/predictive-modeling/scripts/leakage_smoke.py
```
