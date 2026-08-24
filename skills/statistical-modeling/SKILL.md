---
name: statistical-modeling
description: >
  Statistical modeling for sports data science — GLMs for wins/scores/counts,
  hierarchical team/player effects, assumption checks, effect sizes, and
  complete reporting. Use when comparing groups, modeling margins/points/goals,
  building interpretable probability models, checking residuals, or writing up
  sports analysis results. Covers logistic/linear/Poisson models, mixed effects,
  regularization, and diagnostics with statsmodels/sklearn/pingouin patterns.
version: "0.3.0"
license: MIT
metadata:
  version: "0.3.0"
---

# Statistical Modeling for Sports

## Overview

Build defensible statistical models on sports data: the right family for the
outcome, verified assumptions, honest uncertainty, and a write-up that survives
review. Prefer interpretable structure before black-box ML.

This skill operates with the `sports_ds` package when available, and plain
scientific Python otherwise.

## When to Use This Skill

Use this skill when:

- Modeling win/loss, margins, points, goals, runs, or other sports outcomes
- Building logistic or linear baselines with covariates (home, rest, ratings)
- Fitting Poisson/NegBin count models for scoring
- Adding team/player hierarchical structure
- Checking residual diagnostics and calibration of probability models
- Reporting coefficients, effect sizes, and model fit honestly
- Choosing between classical stats models and jumping to ML

Do **not** use this skill as a substitute for:

- raw data loading → `nflreadpy` / `sportsdataverse-py` / `pybaseball` / `sports_ds.data`
- pure EDA → `eda-sports`
- walk-forward ML horse races → `predictive-modeling`
- leakage review of feature pipelines → `leakage-audit`

---

## Installation

```bash
# from repo root
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# recommended extras for richer classical stats
pip install "pingouin>=0.6" "seaborn>=0.13"
```

Core stack already pulled by `sports_ds`:

- `pandas`, `numpy`, `scipy`, `scikit-learn`, `statsmodels`, `matplotlib`

---

## Analysis Workflow

Every sound sports statistical analysis follows this arc. Do not skip.

1. **Frame the question before fitting.**
   - Outcome (win, margin, goals, player stat)
   - Predictors known at decision time T
   - Unit of analysis (game, team-game, player-game, possession)
   - Estimand: description, prediction, or causal claim (most sports work is predictive/descriptive)

2. **Inspect the data (`eda-sports`).**
   - n by season/group
   - missingness
   - score distributions, zero inflation, outliers
   - home/away balance

3. **Choose the model family** (see selection guide below).

4. **Enforce time safety for predictive work.**
   - Features must be knowable at T
   - Use walk-forward validation (`validation-design` / `sports_ds.validation`)

5. **Fit a minimal model first.**
   - home indicator + one strength feature beats a kitchen sink

6. **Check assumptions / diagnostics.**
   - residual plots, overdispersion, leverage, calibration for probabilities

7. **Compare to baselines.**
   - constant rate, home-only, simple rating differential

8. **Report completely.**
   - family, formula, n, metrics, coefficients with uncertainty, limits

---

## Model Selection Guide (Sports)

### Binary outcomes (win/loss, over/under hit)

| Situation | Model |
|---|---|
| Independent game outcomes, linear log-odds in features | Logistic regression (`statsmodels` GLM Binomial or sklearn) |
| Clustered games within season/team | Cluster-robust SE or mixed effects logistic |
| Severe separation / rare events | Firth/penalized logistic, or careful Bayesian prior |

### Continuous outcomes (margin, rating residual)

| Situation | Model |
|---|---|
| Roughly symmetric margins | OLS / Gaussian GLM |
| Heavy tails | Huber robust regression, Student-t likelihood (Bayesian) |
| Heteroscedasticity | HC3 robust SE, WLS |

### Counts (goals, runs, sacks, threes made)

| Situation | Model |
|---|---|
| Mean ≈ variance | Poisson GLM |
| Over-dispersed | Negative Binomial |
| Excess zeros | Hurdle / zero-inflated models |

### Ordered outcomes (win/draw/loss)

- Proportional odds / ordered logit
- Or two-stage: draw model + conditional direction

### Hierarchical structure

- Team strength as random intercepts
- Pitcher/batter, goalie, QB effects with partial pooling
- Prefer partial pooling over dummy-every-player with tiny n

---

## Worked Path with `sports_ds` (NFL team wins)

### 1. Load and EDA

```python
from sports_ds.data.nfl import load_team_game_panel
from sports_ds.eda.summary import summarize_team_game_panel, format_summary

panel = load_team_game_panel(list(range(2018, 2025)))
print(format_summary(summarize_team_game_panel(panel)))
```

### 2. Time-safe features

```python
from sports_ds.features.team_form import add_pregame_form_features

df = add_pregame_form_features(panel)
features = [
    "is_home",
    "feature_win_pct_diff",
    "feature_diff_diff",
    "feature_roll3_win_diff",
    "feature_roll5_diff_diff",
]
model_df = df.dropna(subset=features + ["won"])
model_df = model_df[model_df["pre_games_played"] >= 3]
```

### 3. Logistic model with statsmodels (inference-style)

```python
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Example on a single train window (for coefficients/diagnostics)
train = model_df[model_df["season"] < 2024].copy()
fit = smf.glm(
    formula="won ~ is_home + feature_win_pct_diff + feature_diff_diff",
    data=train,
    family=sm.families.Binomial(),
).fit(cov_type="HC3")
print(fit.summary())
```

### 4. Walk-forward evaluation (predictive honesty)

```python
from sports_ds.models.baselines import baseline_home_rate, fit_logistic_baseline
from sports_ds.validation.splits import season_walk_forward_masks

rows = []
for season, tr, te in season_walk_forward_masks(model_df, min_train_seasons=2):
    base = baseline_home_rate(model_df, tr, te)
    _, log_res, _ = fit_logistic_baseline(model_df, features, tr, te)
    rows.append((season, base.log_loss, log_res.log_loss, log_res.accuracy))

for season, bll, lll, acc in rows:
    print(f"{season}: constant_ll={bll:.4f} logistic_ll={lll:.4f} acc={acc:.3f}")
```

Or one command:

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024
```

---

## Assumption Checks & Diagnostics

Use bundled helpers:

```bash
# from repo root, with venv active
python skills/statistical-modeling/scripts/glm_diagnostics.py \
  --seasons 2018-2023 \
  --out data/glm_diagnostics.json
```

### What to check

**Logistic / classification**

- separation / extreme coefficients
- probability calibration (see `calibration-check`)
- influential games (high leverage matchups)
- stability across seasons

**Gaussian margin models**

- residual vs fitted curvature
- QQ plot of residuals
- residual variance by season or predicted mean

**Poisson scoring models**

- overdispersion: Pearson χ² / df >> 1 → NegBin
- excess zeros

**All predictive sports models**

- leakage: any feature using same-game outcomes?
- temporal drift: does 2019 model die in 2024?

### Script API

```python
import sys
from pathlib import Path
sys.path.append(str(Path("skills/statistical-modeling/scripts").resolve()))
from glm_diagnostics import logistic_diagnostics_report

report = logistic_diagnostics_report(train_df, formula="won ~ is_home + feature_win_pct_diff")
print(report["summary_text"])
print(report["odds_ratios"])
```

---

## Effect Sizes & Metrics (Sports Defaults)

p-values are usually the wrong headline for predictive sports work. Prefer:

| Goal | Primary metrics |
|---|---|
| Probability models | log-loss, Brier, calibration curves |
| Binary decisions | accuracy only as secondary; care about base rates |
| Margins | MAE, RMSE, residual SD |
| Counts | MAE, Poisson deviance |
| Ranking teams | Spearman/Kendall vs final standings (careful with leakage) |

For explanatory group comparisons off the main predictive track (e.g., before/after rule change):

- report effect sizes (Cohen's d, risk difference, odds ratios) with CIs
- do not p-hack season slices

Odds ratio from logistic coefficient:

```python
import numpy as np
or_home = np.exp(fit.params["is_home"])
ci = np.exp(fit.conf_int().loc["is_home"])
print(or_home, ci)
```

---

## Hierarchical / Partial Pooling Patterns

When player or team n is uneven, complete-pooling (ignore groups) and
no-pooling (dummy each group) both fail. Partial pooling is the default
serious approach.

Conceptual statsmodels/linearmodels style (team random intercept for margins):

```python
# Mixed LM example for continuous margin; requires sufficient group size
import statsmodels.formula.api as smf
md = smf.mixedlm("point_diff ~ is_home", data=train, groups=train["team"])
mdf = md.fit()
print(mdf.summary())
```

For full Bayesian hierarchical rating models, prefer a dedicated Bayesian workflow;
keep priors explicit and report posterior predictive checks.

---

## Reporting Template (Sports Statistical Model)

```text
Question: Pre-game P(team win) on NFL team-game panel, seasons S0–S1.
Unit: team-game. Decision time: scheduled kickoff.
Model: logistic GLM with HC3 SE.
Formula: won ~ is_home + feature_win_pct_diff + feature_diff_diff
Features: all shifted pre-game form differentials from sports_ds.features.team_form.
Validation: walk-forward by season; train on past seasons only.
Baselines: constant train win rate; home-only logistic optional.
Results: mean walk-forward log-loss = X.XXX vs constant Y.YYY; accuracy Z.ZZ.
Coefficients (train window): is_home OR=… (95% CI …); …
Diagnostics: …; calibration: …
Limits: no opponent-adjusted EPA; roster/injury not modeled; team renames handled by raw abbreviations.
```

---

## Integrity Rules

1. **Commit the model family before peeking at test folds.**
2. **Do not drop awkward seasons after seeing metrics.**
3. **Always beat a dumb baseline before claiming value.**
4. **Never use same-game score components as predictors for pre-game models.**
5. **Separate exploratory coefficient fishing from confirmatory walk-forward evaluation.**
6. **Report failures and non-improvements.**

---

## Bundled Resources

### references/

- `sports_glm_guide.md` — family choice, formulas, sports gotchas
- `diagnostics_checklist.md` — residual/calibration/leakage checks

### scripts/

- `glm_diagnostics.py` — fit logistic GLM on sports_ds features + export diagnostics JSON

### package code

- `src/sports_ds/models/baselines.py`
- `src/sports_ds/pipelines/nfl_win_model.py`
- `src/sports_ds/validation/splits.py`

---

## Handoffs

| Need | Go to |
|---|---|
| Deeper EDA first | `eda-sports` |
| Feature legality | `feature-rules` / `leakage-audit` |
| Nonlinear ML comparison | `predictive-modeling` |
| Ratings instead of covariates | `ratings-strength-models` |
| Probability reliability | `calibration-check` |
| Write-up | `results-reporting` / `model-card` |

---

## Quick Command Card

```bash
pip install -e .
sports-ds nfl-eda --seasons 2018-2024
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win_pipeline.json
python skills/statistical-modeling/scripts/glm_diagnostics.py --seasons 2018-2023
```
