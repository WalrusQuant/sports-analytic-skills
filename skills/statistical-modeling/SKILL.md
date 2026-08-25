---
name: statistical-modeling
description: >
  Guided statistical modeling for user-provided sports data: selecting models
  for binary, continuous, and count outcomes; assumption checks; effect sizes;
  time-aware inference; GLM diagnostics; and complete reporting.
license: MIT
metadata:
  version: "0.12.0"
---

# Statistical Modeling for Sports

## Overview

Conduct statistical analyses on sports data the way a careful analyst would:
right model family for the outcome, verified assumptions, honest effect sizes
and uncertainty, time-safe features when predicting, and a write-up that
survives review.

This is a sports-domain statistical-analysis methodology with deep references,
specialized for games, teams, players, and seasons. Its bundled scripts are
deliberately narrower: univariate assumption summaries and an additive numeric
binomial GLM. The linear, count, mixed, Bayesian, causal, and power-analysis
workflows below require the named external libraries and analyst-written code.

Typical stack: `pandas`, `numpy`, `scipy`, `statsmodels`, and `scikit-learn`
(+ optional `pingouin`, `seaborn`, `pymc`, and `arviz`).

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

- raw data loading → use the appropriate loader skill, then return with a user-owned analysis table
- pure EDA → `eda-sports`
- walk-forward ML horse races → `predictive-modeling`
- leakage review of feature pipelines → `leakage-audit`
- rating systems as the primary object → `ratings-strength-models`

---

## Installation

Install only the libraries required by the chosen analysis:

```bash
python -m pip install pandas numpy scipy statsmodels scikit-learn
# Optional richer classical statistics and plots:
python -m pip install "pingouin>=0.6" "seaborn>=0.13"
# Optional Bayesian hierarchical work:
python -m pip install pymc arviz
```

Parquet input to the bundled helpers also needs `pyarrow` or `fastparquet`.

Compatibility notes:

- Prefer `statsmodels>=0.14` with a recent SciPy.
- Pingouin 0.6+ uses `p_val`, `cohen_d`, and `CI95`.
- Read [bayesian_statistics.md](references/bayesian_statistics.md) before selecting Bayesian priors or diagnostics.

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
   - Use walk-forward validation (`validation-design`)

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

Reference routing:

- Read [test_selection_guide.md](references/test_selection_guide.md) when choosing a comparison or test.
- Read [sports_glm_guide.md](references/sports_glm_guide.md) when mapping an outcome to a family and link.
- Read [assumptions_and_diagnostics.md](references/assumptions_and_diagnostics.md) and
  [diagnostics_checklist.md](references/diagnostics_checklist.md) when validating a fitted model.
- Read [effect_sizes_and_power.md](references/effect_sizes_and_power.md) for effect-size, interval, and
  power choices.
- Read [bayesian_statistics.md](references/bayesian_statistics.md) for prior, partial-pooling, and
  posterior-diagnostic decisions.
- Read [reporting_standards.md](references/reporting_standards.md) when producing the final analysis.

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

## Worked Path on a User-Provided Team-Game Table

Start with one row per evaluated decision and document whether that means one
row per game or one row per team-game. A useful binary-outcome frame contains:

| Field | Role |
|---|---|
| `season`, `event_time`, stable IDs | chronology and alignment |
| `won` | binary outcome |
| `is_home` | pre-event context |
| `rating_diff`, `rest_diff` | legal pre-event predictors |
| fold or test-season label | evaluation provenance |

For symmetric team-game data, either model both perspectives with dependence-aware
uncertainty or select one perspective per game. Never treat doubled rows as
independent evidence.

### Logistic model with robust inference

```python
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

train = model_df[model_df["season"] < 2024].copy()
fit = smf.glm(
    "won ~ is_home + rating_diff + rest_diff",
    data=train,
    family=sm.families.Binomial(),
).fit(cov_type="HC3")

odds_ratios = np.exp(fit.params)
odds_ratio_ci = np.exp(fit.conf_int())
print(fit.summary())
print(odds_ratios)
print(odds_ratio_ci)
```

HC3 is useful for heteroskedasticity but does not solve team, player, or temporal
dependence. Use cluster-robust uncertainty or a hierarchical model when the
sampling structure requires it.

### Margin model

```python
home = train[train["is_home"] == 1].copy()  # one row per game
margin_fit = smf.ols(
    "point_margin ~ rating_diff + rest_diff",
    data=home,
).fit(cov_type="HC3")
print(margin_fit.summary())
```

Inspect residual shape, changing variance, influential games, and nonlinear
patterns. If the scientific question concerns an average contrast rather than a
conditional linear effect, report that estimand directly too.

### Count model

```python
poisson_fit = smf.glm(
    "points_for ~ is_home + rating_diff",
    data=train,
    family=sm.families.Poisson(),
).fit()
dispersion = poisson_fit.pearson_chi2 / poisson_fit.df_resid
print(poisson_fit.summary())
print("Pearson dispersion:", dispersion)
```

Material overdispersion, excess zeros, or correlated paired scores can require a
negative-binomial, hurdle/zero-inflated, or joint score model. Select that
extension from diagnostics and the data-generating process—not a better-looking
p-value.

### Predictive evaluation

Freeze expanding time folds before fitting. Within each fold, estimate every
transform and model on earlier rows only; score the later block against a
training-rate constant and a simple legal-feature baseline. Report every fold,
not only the mean.

For a standalone additive binomial diagnostic report:

```bash
python /path/to/statistical-modeling/scripts/glm_diagnostics.py \
  --input model_frame.csv \
  --formula "won ~ is_home + rating_diff + rest_diff" \
  --out glm_report.json
```

The helper reports HC3 inference, odds ratios, intervals, AIC, and in-sample
calibration bins. Those bins diagnose fit; they are not held-out evidence.

---

## Assumption Checks & Diagnostics

**Always check assumptions before interpreting**, and report the checks.

### Standalone assumption checks

```bash
python /path/to/statistical-modeling/scripts/assumption_checks.py \
  --input observations.csv --value-col margin \
  --group-col venue --out assumptions.json
```

The helper reports Shapiro-Wilk normality, IQR outliers, and optional
median-centered Levene variance testing. Formal tests supplement plots and
domain judgment; at large sample sizes they can reject practically harmless
departures.

### Standalone binomial GLM diagnostics

```bash
python /path/to/statistical-modeling/scripts/glm_diagnostics.py \
  --input model_frame.csv \
  --formula "won ~ is_home + rating_diff + rest_diff" \
  --out glm_report.json
```

Inputs may be CSV, Parquet, JSON, JSONL, or NDJSON. Formulas support additive
numeric predictors joined by `+`; use `--outcome-col` when the binary target
is not `won`.

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
- inspect influence and leverage with the fitted library's diagnostics (for
  example, statsmodels `OLSInfluence`), and use Breusch-Pagan or another
  predeclared variance check when appropriate

The bundled `glm_diagnostics.py` fits only additive numeric binomial GLMs. It
does not diagnose OLS, Poisson, negative-binomial, mixed, or Bayesian models;
use the model library's diagnostics and the linked checklist for those
families.

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
home = panel.loc[panel["is_home"].eq(1), ["season", "point_diff"]].dropna()
print(home["point_diff"].describe())  # pooled descriptive game-weighted mean
print(home.groupby("season")["point_diff"].agg(["count", "mean", "std"]))
```

Do not attach an ordinary one-sample t-test to clustered team/season data by
default. Choose the uncertainty method from the sampling structure: a
season-block bootstrap for a game-weighted mean, an equal-season estimand on
season summaries when seasons are the independent units, or a model with
defensible cluster/hierarchical structure. Games connect two teams, so a
one-way team cluster can also be inadequate. State the estimand and number of
independent clusters; with few clusters, use small-sample-aware methods and
weaken the claim.

### Correlation: pre-game form vs margin

```python
required = {"pre_form_diff", "point_diff"}
missing = required.difference(panel.columns)
if missing:
    raise ValueError(f"build and join legal pre-game form columns first: {sorted(missing)}")
feat = panel.dropna(subset=["pre_form_diff", "point_diff"])
print(pg.corr(feat["pre_form_diff"], feat["point_diff"], method="pearson"))
print(pg.corr(feat["pre_form_diff"], feat["point_diff"], method="spearman"))
```

The example assumes `pre_form_diff` was created outside this skill with an
as-of/shifted feature workflow such as `time-series-sports`; no bundled
`add_pregame_form_features` function exists.

Always state that observational sports associations are not automatically causal.

---

## Reporting Templates (Sports)

### Predictive logistic win model

```text
Question: Pre-game P(team win) on NFL team-game panel, seasons S0–S1.
Unit: team-game. Decision time: scheduled kickoff.
Model: logistic GLM with HC3 SE.
Formula: won ~ is_home + rating_diff + pre_form_diff
Features: all declared pre-event predictors, with construction and as-of timing documented.
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
Analysis: game-weighted mean point_diff; season-block bootstrap (or another
dependence-aware method justified from the design); 95% interval.
Assumptions: one row per game; cluster definition and number of clusters stated.
Result: M=…, SD=…, dependence-aware 95% CI ….
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
| [sports_glm_guide.md](references/sports_glm_guide.md) | Sports outcome → GLM family map and formulas |
| [diagnostics_checklist.md](references/diagnostics_checklist.md) | Sports-specific diagnostic checklist |
| [test_selection_guide.md](references/test_selection_guide.md) | Full test selection tree (group comparisons, etc.) |
| [assumptions_and_diagnostics.md](references/assumptions_and_diagnostics.md) | Deep assumption checking guidance |
| [effect_sizes_and_power.md](references/effect_sizes_and_power.md) | Effect sizes, CIs, power analysis |
| [bayesian_statistics.md](references/bayesian_statistics.md) | Priors, hierarchical Bayes, diagnostics |
| [reporting_standards.md](references/reporting_standards.md) | Complete reporting standards and templates |

### scripts/

| File | Contents |
|---|---|
| `assumption_checks.py` | Normality, IQR outliers, and optional Levene variance check on a supplied column |
| `glm_diagnostics.py` | Fit an additive logistic GLM on a user-owned table; export OR, intervals, and calibration JSON |


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
python /path/to/statistical-modeling/scripts/assumption_checks.py \
  --input observations.csv --value-col margin --group-col venue \
  --out assumptions.json

python /path/to/statistical-modeling/scripts/glm_diagnostics.py \
  --input model_frame.csv \
  --formula "won ~ is_home + rating_diff + rest_diff" \
  --out glm_report.json
```

---
