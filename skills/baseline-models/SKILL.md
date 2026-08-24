---
name: baseline-models
description: >
  Build and evaluate strong simple sports baselines before complex models —
  constant rates, home effects, logistic form differentials, and comparison
  under walk-forward validation. Use at the start of every predictive project
  and whenever an ML model needs an honesty check.
version: "0.3.0"
license: MIT
metadata:
  version: "0.3.0"
---

# Baseline Models for Sports

## Overview

If a fancy model cannot beat simple baselines under time-safe validation, it is
not progress. This skill defines the baseline ladder and runs it through `sports_ds`.

## When to Use

- Starting a predictive sports project
- Auditing an ML result that looks shiny
- Building the first model you might actually keep

---

## Installation

```bash
pip install -e .
```

---

## Baseline Ladder

| Tier | Baseline | Implemented |
|---|---|---|
| A | Constant train win rate / mean target | yes (`baseline_home_rate` name is constant rate on panel) |
| B | Logistic on home + form differentials | yes (`fit_logistic_baseline`) |
| C | Simple rating differential only | pattern below / ratings skill |

---

## Run Baselines via Pipeline

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024
```

Reports constant vs logistic vs hist GBM on each walk-forward season.

## Python

```python
from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.models.baselines import baseline_home_rate, fit_logistic_baseline
from sports_ds.validation.splits import season_walk_forward_masks

df = add_pregame_form_features(load_team_game_panel(list(range(2018, 2025)))).dropna()
features = [
    "is_home",
    "feature_win_pct_diff",
    "feature_diff_diff",
    "feature_roll3_win_diff",
    "feature_roll5_diff_diff",
]

for season, tr, te in season_walk_forward_masks(df):
    c = baseline_home_rate(df, tr, te)
    _, loc, _ = fit_logistic_baseline(df, features, tr, te)
    print(season, c.log_loss, loc.log_loss, loc.accuracy)
```

Code:

- `src/sports_ds/models/baselines.py`
- `src/sports_ds/pipelines/nfl_win_model.py`

---

## What “Good” Looks Like

- Logistic log-loss < constant on most folds
- Coefficients point the right way (home > 0 in log-odds)
- Gains are not from one freak season only

If trees barely beat logistic, prefer logistic unless you have a strong reason.

---

## Home-only Baseline Pattern

```python
import statsmodels.formula.api as smf
import statsmodels.api as sm

fit = smf.glm("won ~ is_home", data=train, family=sm.families.Binomial()).fit()
print(fit.summary())
```

---

## Procedure

1. Define target + metric.
2. Implement Tier A constant baseline.
3. Implement Tier B simple model with legal features.
4. Walk-forward evaluate both.
5. Only then try ML (`predictive-modeling`).
6. Keep the simplest model that wins.

---

## Bundled Resources

### references/

- `baseline_ladder.md`

### scripts/

- `run_baselines.py` — print constant vs logistic fold metrics

---

## Handoffs

- Features → `feature-rules`
- ML comparison → `predictive-modeling`
- Inference writeup → `statistical-modeling`
- Validation design → `validation-design`

---

## Command Card

```bash
python skills/baseline-models/scripts/run_baselines.py --seasons 2018-2024
sports-ds nfl-win-pipeline --seasons 2018-2024
```
