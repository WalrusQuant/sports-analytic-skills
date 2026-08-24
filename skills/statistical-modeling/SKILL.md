---
name: statistical-modeling
description: >
  Guided statistical modeling for sports data — test and model selection for
  wins/margins/scores/counts, assumption checking, effect sizes, hierarchical
  team/player effects, walk-forward-aware inference, and complete reporting.
  Use whenever analyzing sports outcomes, comparing groups (home/away, eras,
  positions), fitting logistic/linear/Poisson models, checking residuals, or
  writing up sports analysis results. Covers GLMs, mixed effects, regularization,
  calibration, and diagnostics with statsmodels/scipy/pingouin/sklearn patterns
  plus sports_ds loaders. For pure ML horse races see predictive-modeling; for
  leakage audits see leakage-audit.
version: "0.4.0"
license: MIT
metadata:
  version: "0.4.0"
---

# Statistical Modeling for Sports

## Overview

Conduct statistical analyses on sports data the way a careful analyst would:
right model family for the outcome, verified assumptions, honest effect sizes
and uncertainty, time-safe features when predicting, and a write-up that
survives review.

This is the sports-domain counterpart to a full scientific statistical-analysis
skill: complete workflows, runnable scripts, and deep references — specialized
for games, teams, players, and seasons.

Stack: `sports_ds` + `pandas` / `numpy` / `scipy` / `statsmodels` / `scikit-learn`
(+ optional `pingouin`, `seaborn`).

## When to Use This Skill

Use this skill when:

- Modeling win/loss, margins, points, goals, runs, or other sports outcomes
- Comparing groups (home vs away, pre/post rule change, position groups)
- Fitting logistic, linear, Poisson, or NegBin models on sports panels
- Adding hierarchical team/player effects (partial pooling)
- Checking residual diagnostics and probability calibration
- Reporting coefficients, odds ratios, effect sizes, and model fit
- Choosing between classical stats models and jumping to ML

Do **not** use this skill as a substitute for:

- raw data loading → `nflreadpy` / `sportsdataverse-py` / `pybaseball` / `sports_ds.data`
- pure EDA → `eda-sports`
- walk-forward ML horse races → `predictive-modeling`
- leakage review of feature pipelines → `leakage-audit`
- rating systems as the primary object → `ratings-strength-models`

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

**Compatibility notes:**

- Prefer `statsmodels>=0.14` with recent SciPy
- Pingouin 0.6+ column names: `p_val`, `cohen_d`, `CI95` (not hyphenated 0.5.x names)
- For Bayesian hierarchical work, optional: `pymc`, `arviz` (see references/bayesian_statistics.md)

---

## Analysis Workflow

Every sound sports statistical analysis follows this arc. Do not skip.

1. **Frame the question before fitting.**
   - Outcome (win, margin, goals, player stat)
   - Predictors known at decision time T (if predictive)
   - Unit of analysis (game, team-game, player-game, possession)
   - Estimand: description, prediction, or causal claim (most sports work is predictive/descriptive)

2. **Inspect the data (`eda-sports`).**
   - n by season/group
   - missingness
   - score distributions, zero inflation, outliers
   - home/away balance

3. **Choose the model family** using the selection guide below (and `references/test_selection_guide.md` + `references/sports_glm_guide.md`).

4. **Enforce time safety for predictive work.**
   - Features must be knowable at T
   - Use walk-forward validation (`validation-design` / `sports_ds.validation`)

5. **Fit a minimal model first.**
   - home indicator + one strength feature beats a kitchen sink

6. **Check assumptions / diagnostics.**
   - Use `scripts/assumption_checks.py` and `scripts/glm_diagnostics.py`
   - residual plots, overdispersion, leverage, calibration for probabilities

7. **Compare to baselines.**
   - constant rate, home-only, simple rating differential (`baseline-models`)

8. **Report completely.**
   - family, formula, n, metrics, coefficients with uncertainty, limits
   - templates in `references/reporting_standards.md` + sports templates below

If the user only needs one step (e.g. “is home advantage real in this sample?”), jump to that section — but still state design assumptions.

---

## Model Selection Guide (Sports)

### Binary outcomes (win/loss, threshold events)

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

### Group comparisons (not full predictive models)

| Design | Start here |
|---|---|
| Two independent groups, continuous | Welch t-test / Mann-Whitney |
| Paired (same team pre/post) | Paired t / Wilcoxon |
| 3+ groups | ANOVA / Kruskal-Wallis |
| Association of two continuous | Pearson / Spearman |
| See full tree | `references/test_selection_guide.md` |

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
import numpy as np

train = model_df[model_df["season"] < 2024].copy()
fit = smf.glm(
    formula="won ~ is_home + feature_win_pct_diff + feature_diff_diff",
    data=train,
    family=sm.families.Binomial(),
).fit(cov_type="HC3")
print(fit.summary())

# Odds ratios with 95% CI
ors = np.exp(fit.params)
ci = np.exp(fit.conf_int())
print(ors)
print(ci)
```

### 4. Margin model (Gaussian)

```python
# home-row margins avoid double-counting games
home = train[train["is_home"] == 1]
m_fit = smf.ols(
    "point_diff ~ feature_win_pct_diff + feature_diff_diff",
    data=home,
).fit(cov_type="HC3")
print(m_fit.summary())
```

### 5. Poisson scoring model (points/goals pattern)

```python
# example: points_for as count-ish outcome with exposure not required for full games
poi = smf.glm(
    "points_for ~ is_home + feature_win_pct_diff",
    data=train,
    family=sm.families.Poisson(),
).fit()
print(poi.summary())
# if Pearson chi2 / df >> 1, switch to NegativeBinomial
```

### 6. Walk-forward evaluation (predictive honesty)

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

**Always check assumptions before interpreting**, and report the checks.

### General assumption toolkit (bundled)

Use the full scientific assumption module (normality, variance homogeneity,
linearity, outliers, regression diagnostics):

```bash
# from repo root, with venv active — import path:
# skills/statistical-modeling/scripts
```

```python
import sys
from pathlib import Path
sys.path.append(str(Path("skills/statistical-modeling/scripts").resolve()))

from assumption_checks import (
    comprehensive_assumption_check,
    check_normality,
    check_homogeneity_of_variance,
    check_regression_diagnostics,
    detect_outliers,
)

# Example: margin distribution overall
home = model_df[model_df.is_home == 1]
print(check_normality(home["point_diff"], name="point_diff", plot=False))

# Grouped: point_diff by season (illustrative)
print(check_homogeneity_of_variance(home, "point_diff", "season", plot=False))
```

### Sports GLM diagnostics script

```bash
python skills/statistical-modeling/scripts/glm_diagnostics.py \
  --seasons 2018-2023 \
  --out data/glm_diagnostics.json
```

```python
from glm_diagnostics import logistic_diagnostics_report, build_model_frame
df = build_model_frame(list(range(2018, 2024)))
report = logistic_diagnostics_report(df)
print(report["odds_ratios"])
print(report["calibration_bins"])
```

### What to check by family

**Logistic / classification**

- separation / extreme coefficients
- probability calibration (`calibration-check`)
- influential games (high leverage matchups)
- stability across seasons

**Gaussian margin models**

- residual vs fitted curvature
- QQ plot of residuals
- residual variance by season or predicted mean
- use `check_regression_diagnostics` on OLS fits

**Poisson scoring models**

- overdispersion: Pearson χ² / df >> 1 → NegBin
- excess zeros

**All predictive sports models**

- leakage: any feature using same-game outcomes?
- temporal drift: does 2019 model die in 2024?

See `references/assumptions_and_diagnostics.md` and `references/diagnostics_checklist.md`.

---

## Effect Sizes & Metrics (Sports Defaults)

p-values are usually the wrong headline for predictive sports work. Prefer:

| Goal | Primary metrics |
|---|---|
| Probability models | log-loss, Brier, calibration curves |
| Binary decisions | accuracy only as secondary; care about base rates |
| Margins | MAE, RMSE, residual SD |
| Counts | MAE, Poisson deviance |
| Group differences (explanatory) | Cohen's d, risk difference, odds ratios + CIs |

Odds ratio from logistic coefficient:

```python
import numpy as np
or_home = np.exp(fit.params["is_home"])
ci = np.exp(fit.conf_int().loc["is_home"])
print(or_home, ci.tolist())
```

For classical effect size tables, power analysis, and CI methods, use
`references/effect_sizes_and_power.md` and pingouin:

```python
import pingouin as pg
# home vs away margins on home-row frame already encodes home perspective;
# example two-sample on a continuous player metric:
# pg.ttest(group_a, group_b, correction='auto')  # returns cohen_d, CI95, etc.
```

---

## Hierarchical / Partial Pooling Patterns

When player or team n is uneven, complete-pooling (ignore groups) and
no-pooling (dummy each group) both fail. Partial pooling is the default
serious approach.

```python
import statsmodels.formula.api as smf
# Mixed LM example for continuous margin; requires sufficient group size
md = smf.mixedlm("point_diff ~ is_home", data=train, groups=train["team"])
mdf = md.fit()
print(mdf.summary())
```

For full Bayesian hierarchical rating models, keep priors explicit and report
posterior predictive checks — see `references/bayesian_statistics.md`.

---

## Group Comparison Examples (Sports)

### Home advantage on margins (home rows)

```python
import pingouin as pg
home = panel[panel.is_home == 1]
# one-sample: is mean home margin > 0?
print(home["point_diff"].describe())
print(pg.ttest(home["point_diff"], 0))
```

### Correlation: pre-game form vs margin

```python
feat = add_pregame_form_features(panel).dropna(subset=["feature_diff_diff", "point_diff"])
print(pg.corr(feat["feature_diff_diff"], feat["point_diff"], method="pearson"))
print(pg.corr(feat["feature_diff_diff"], feat["point_diff"], method="spearman"))
```

Always state that observational sports associations are not automatically causal.

---

## Reporting Templates (Sports)

### Predictive logistic win model

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

### Explanatory home-advantage estimate

```text
Question: Mean home margin in NFL seasons …
Design: home rows only (one row per game).
Analysis: one-sample t on point_diff vs 0; effect size Cohen's d; 95% CI.
Assumptions: normality checked via Shapiro-Wilk + Q-Q; large n → CLT noted.
Result: M=…, SD=…, t(df)=…, p=…, d=…, 95% CI ….
Limits: era/rule confounds; not a causal estimate of venue alone.
```

APA-style general templates: `references/reporting_standards.md`.

---

## Integrity Rules

1. **Commit the model family before peeking at test folds.**
2. **Do not drop awkward seasons after seeing metrics.**
3. **Always beat a dumb baseline before claiming value.**
4. **Never use same-game score components as predictors for pre-game models.**
5. **Separate exploratory coefficient fishing from confirmatory walk-forward evaluation.**
6. **Report failures and non-improvements.**
7. **Distinguish confirmatory from exploratory analyses** (see statistical integrity notes in references).
8. **Make it reproducible** — seasons, formula, package versions, seeds.

---

## Bundled Resources

### references/

| File | Contents |
|---|---|
| `sports_glm_guide.md` | Sports outcome → GLM family map and formulas |
| `diagnostics_checklist.md` | Sports-specific diagnostic checklist |
| `test_selection_guide.md` | Full test selection tree (group comparisons, etc.) |
| `assumptions_and_diagnostics.md` | Deep assumption checking guidance |
| `effect_sizes_and_power.md` | Effect sizes, CIs, power analysis |
| `bayesian_statistics.md` | Priors, hierarchical Bayes, diagnostics |
| `reporting_standards.md` | Complete reporting standards and templates |

### scripts/

| File | Contents |
|---|---|
| `assumption_checks.py` | Full assumption toolkit: normality, Levene, linearity, outliers, OLS diagnostics |
| `glm_diagnostics.py` | Fit logistic GLM on sports_ds features; export OR, calibration JSON |

### package code

- `src/sports_ds/models/baselines.py`
- `src/sports_ds/pipelines/nfl_win_model.py`
- `src/sports_ds/validation/splits.py`
- `src/sports_ds/features/team_form.py`

---

## Related Skills

| Need | Go to |
|---|---|
| Deeper EDA first | `eda-sports` |
| Feature legality | `feature-rules` / `leakage-audit` |
| Nonlinear ML comparison | `predictive-modeling` |
| Ratings instead of covariates | `ratings-strength-models` |
| Probability reliability | `calibration-check` |
| Write-up | `results-reporting` / `model-card` |
| Baselines ladder | `baseline-models` |
| Validation design | `validation-design` |

---

## Quick Command Card

```bash
pip install -e .
sports-ds nfl-eda --seasons 2018-2024
sports-ds nfl-win-pipeline --seasons 2018-2024 --json-out data/nfl_win_pipeline.json
python skills/statistical-modeling/scripts/glm_diagnostics.py --seasons 2018-2023
python skills/calibration-check/scripts/calibration_report.py --seasons 2018-2024
```
