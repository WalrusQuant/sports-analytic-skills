---
name: sports-modeling-doctrine
description: >
  Core doctrine for sports data science: define the prediction/analysis
  question, baselines, time-safe evaluation, and when a sports model is
  good enough. Use at the start of modeling or analysis work.
version: "0.1.0"
license: MIT
---

# Sports Modeling Doctrine

Foundation skill for sports data science. Centers the work on analysis and
prediction quality — not markets, odds, or betting products.

## When to use

- Starting any sports modeling or analysis project
- Choosing what “good” means for a predictive or explanatory model
- Deciding baselines and evaluation standards
- Preventing notebook chaos before code starts

## When not to use

- Pure data download with no analytic goal → `data-sources` / package skills
- Deep EDA only → `eda-sports`
- Specific ML algorithm choice → `predictive-modeling`

## Required inputs

- Question (predict / explain / rank / simulate)
- Target and grain (game, player-game, possession, pitch, etc.)
- Prediction or analysis time T if predictive
- Available historical window

## Core rules

1. **State the question before the model.**
2. **Name baselines before complexity.**
3. **Time order matters in sports.** Prefer walk-forward over random splits.
4. **Features must be knowable at T** for prediction tasks.
5. **Beat simple models first** (base rates, ratings, linear/logistic).
6. **Report uncertainty and limits**, not just a leaderboard score.
7. **Reproducibility required** for any kept result.

## Procedure

1. Write the analytic question in one sentence.
2. Define target, grain, and T.
3. Choose metrics that match the question (log-loss/Brier for probs; MAE/RMSE for continuous; ranking metrics for ranks).
4. Define Tier A/B baselines (`baseline-models`).
5. Lock validation design (`validation-design`).
6. Only then engineer features and fit richer models.
7. Interpret and report (`model-interpretation`, `results-reporting`).

## Hard constraints

- No random K-fold as default on chronological sports events
- No same-event outcome fields as pre-event predictors
- No “complex model wins” without baseline comparison
- No results without a stated question and metric
- Do not center the workflow on betting products or odds pipelines

## Anti-patterns

- Model-first, question-later
- Metric shopping after results
- One hot season as universal truth
- Feature dumps with no timing rules
- Treating data pull success as analysis success

## Output contract

- [ ] Question / target / grain / T stated
- [ ] Metrics chosen
- [ ] Baselines named
- [ ] Validation approach named
- [ ] Next skills identified

## Handoffs

- `data-sources` → loaders
- `eda-sports` → explore
- `feature-rules` → features
- `baseline-models` / `statistical-modeling` / `predictive-modeling`
- `validation-design` / `leakage-audit`
- `results-reporting`

## References

- `ARCHITECTURE.md`
- `docs/data-ecosystem.md`
