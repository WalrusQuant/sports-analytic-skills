---
name: baseline-models
description: >
  Build and evaluate strong simple sports baselines before complex models —
  constant rates, home effects, logistic/linear form differentials, rating
  differentials, and walk-forward comparison tables. Use at the start of every
  predictive project and whenever an ML result needs an honesty check. Includes
  sports_ds baseline APIs and runnable fold scripts.
version: "0.4.0"
license: MIT
metadata:
  version: "0.4.0"
---

# Baseline Models for Sports

## Overview

If a fancy model cannot beat simple baselines under time-safe validation, it is
not progress.

This skill defines the **baseline ladder**, implements constant and logistic
baselines via `sports_ds`, and standardizes walk-forward comparison before ML.

---

## When to Use This Skill

Use when:

- Starting a predictive sports project
- Auditing an ML result that looks shiny
- Building the first model you might actually keep
- User says “what’s the baseline?” or “does this beat home field?”

Do **not** skip this skill and jump to trees.

Related:

- validation folds → `validation-design`
- features → `feature-rules`
- ML candidates → `predictive-modeling`
- GLM inference writeup → `statistical-modeling`
- ratings baseline → `ratings-strength-models`

---

## Installation

```bash
pip install -e .
```

---

## Baseline Ladder

| Tier | Baseline | Implemented here |
|---|---|---|
| A | Constant train win rate / mean target | yes — `baseline_home_rate` (constant rate on panel) |
| B | Home-only logistic / mean home margin | pattern below |
| C | Logistic/linear on home + form differentials | yes — `fit_logistic_baseline` |
| D | Rating differential logistic/linear | via `ratings-strength-models` Elo table |

Climb to ML only after Tier A–C (or A–D) exist under walk-forward evaluation.

See `references/baseline_ladder.md`.

---

## Workflow

1. Define target + primary metric.
2. Build legal features (`feature-rules`).
3. Create walk-forward folds (`validation-design`).
4. Fit Tier A constant baseline each fold.
5. Fit Tier C logistic/linear baseline each fold.
6. Optional: rating-diff baseline.
7. Compare per-fold and mean metrics.
8. Only then try ML (`predictive-modeling`).
9. Keep the simplest model that wins.
10. Log the experiment.

---

## Run Baselines

### CLI / pipeline (includes ML for comparison)

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024
```

### Baseline-only fold table

```bash
python skills/baseline-models/scripts/run_baselines.py --seasons 2018-2024
python skills/baseline-models/scripts/home_only_baseline.py --seasons 2018-2024
```

### Python API

```python
from sports_ds.data.nfl import load_team_game_panel
from sports_ds.features.team_form import add_pregame_form_features
from sports_ds.models.baselines import baseline_home_rate, fit_logistic_baseline
from sports_ds.pipelines.nfl_win_model import FEATURE_COLS
from sports_ds.validation.splits import season_walk_forward_masks

df = add_pregame_form_features(load_team_game_panel(list(range(2018, 2025))))
df = df.dropna(subset=FEATURE_COLS + ["won"])
df = df[(df.pre_games_played >= 3) & (df.opp_pre_games_played >= 3)]

for season, tr, te in season_walk_forward_masks(df):
    c = baseline_home_rate(df, tr, te)
    _, loc, prob = fit_logistic_baseline(df, FEATURE_COLS, tr, te)
    print(season, c.log_loss, loc.log_loss, loc.accuracy)
```

Code:

- `src/sports_ds/models/baselines.py`
- `src/sports_ds/pipelines/nfl_win_model.py`

---

## Tier Details

### Tier A — Constant rate

`baseline_home_rate` predicts the training-set mean of `won` for every test row.

On balanced team-game panels this is near 0.5 and log-loss near ~0.693.

### Tier B — Home only

```python
import statsmodels.api as sm
import statsmodels.formula.api as smf

fit = smf.glm("won ~ is_home", data=train, family=sm.families.Binomial()).fit()
print(fit.summary())
# odds ratio for home:
import numpy as np
print(float(np.exp(fit.params["is_home"])))
```

Or:

```bash
python skills/baseline-models/scripts/home_only_baseline.py --seasons 2018-2023
```

### Tier C — Form logistic

Uses `FEATURE_COLS` from the win pipeline (home + shifted form differentials).

### Tier D — Rating differential

```bash
python skills/ratings-strength-models/scripts/elo_asof.py --seasons 2018-2024 --out data/elo_asof.csv
# then logistic on is_home + elo_diff under walk-forward (see ratings skill)
```

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

## Reporting Template

```text
Baseline report
Target: …
T: …
Features: …
Validation: season walk-forward
Tier A mean metric:
Tier C mean metric:
Per-season table:
Decision: promote to ML | keep logistic | debug features
```

---

## Integrity Rules

1. No predictive project without Tier A.
2. Walk-forward only for claims of generalization.
3. Do not hide folds where baseline wins.
4. Simplest winning model is the default ship candidate.

---

## Bundled Resources

### references/

| File | Contents |
|---|---|
| `baseline_ladder.md` | ladder and promotion rules |
| `interpretation.md` | how to read baseline comparisons |

### scripts/

| File | Contents |
|---|---|
| `run_baselines.py` | const vs logistic walk-forward table |
| `home_only_baseline.py` | home-only logistic on pooled train window + note |

### package code

- `src/sports_ds/models/baselines.py`

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
python skills/baseline-models/scripts/run_baselines.py --seasons 2018-2024
python skills/baseline-models/scripts/home_only_baseline.py --seasons 2018-2023
sports-ds nfl-win-pipeline --seasons 2018-2024
```
