---
name: statistical-modeling
description: >
  Classical statistical modeling for sports: GLMs, hierarchical models,
  regularization, uncertainty, and inference-minded analysis. Use when the
  goal is explanation, baselines, or principled probability models.
version: "0.1.0"
license: MIT
---

# Statistical Modeling (Sports)

Stats-first modeling skill for sports outcomes and quantities.

## When to use

- Win/lose, score, margin, count models
- Need interpretable coefficients / uncertainty
- Building strong classical baselines before ML
- Hierarchical team/player effects

## When not to use

- Pure black-box leaderboard chase → `predictive-modeling`
- No EDA yet → `eda-sports`
- Ratings-only strength models → `ratings-strength-models`

## Model families

| Family | Sports uses |
|---|---|
| Logistic / multinomial | win, result class |
| Linear / Gaussian | margin, rating residuals |
| Poisson / NegBin | goals, runs, points counts |
| Ordered models | win/draw/loss
| Hierarchical / mixed effects | team, pitcher, venue effects |
| Regularized GLM (ridge/lasso/elastic net) | many correlated features |

## Procedure

1. Define target distribution and link.
2. Start with a tiny covariate set (strength, home, rest).
3. Fit and check calibration/residuals.
4. Add structure only if it earns improvement on time-safe validation.
5. Report coefficients with uncertainty where meaningful.
6. Compare to baselines.

## Hard constraints

- Match model family to outcome type
- Time-safe validation required for predictive claims
- Overdispersion check for counts
- Do not interpret coefficients causally without design support

## Anti-patterns

- Linear regression on win probability without link care
- Ignoring clustering (multiple games per team)
- Giant GLM with collinear form stats and no regularization
- Reporting p-values as the product

## Output contract

- [ ] Model family justified
- [ ] Formula/feature set listed
- [ ] Fit diagnostics noted
- [ ] Time-safe metrics vs baselines
- [ ] Interpretation limits stated

## Handoffs

- `baseline-models`
- `predictive-modeling` if nonlinear needed
- `calibration-check` for probability models
- `model-interpretation`
- `validation-design`

## Stack hints

- Python: `statsmodels`, `scikit-learn`, `pymc`/`bamboo` optional later
- R: `lme4`, `brms`, `glmnet` (if user is in R)
