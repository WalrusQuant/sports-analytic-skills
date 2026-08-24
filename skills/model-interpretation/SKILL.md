---
name: model-interpretation
description: >
  Interpret sports models: feature effects, partial dependence, error slices,
  and what drivers actually mean under leakage-safe features. Use after fitting
  a model to explain behavior and failure modes.
version: "0.1.0"
license: MIT
---

# Model Interpretation (Sports)

Explain what a sports model is doing and where it fails.

## When to use

- After baseline/ML/stat model fit
- Need driver explanations for a report
- Debugging segment failures (home underdogs, early season, etc.)

## When not to use

- Model not trained yet
- Features are known leaked — fix leakage first

## Techniques

- coefficient tables (GLM)
- tree importances + caution
- partial dependence / ALE style effects
- residual slices by season/team/position
- case studies of largest misses
- ablation: remove feature group and re-check forward metrics

## Procedure

1. Confirm features are time-safe.
2. Global picture: top drivers.
3. Local picture: example games/players.
4. Slice errors by meaningful segments.
5. Separate correlation from actionable explanation.
6. Document limits.

## Hard constraints

- Importance ≠ causality
- Don’t explain a leaked model as insight
- Slice metrics with enough n or mark unstable
- Keep interpretation tied to validation evidence

## Anti-patterns

- SHAP theater on a contaminated pipeline
- One importance bar chart as the whole story
- Ignoring systematic miss segments

## Output contract

- [ ] Global drivers summarized
- [ ] Key slices checked
- [ ] Example misses analyzed
- [ ] Limits explicit
- [ ] No causal overclaim

## Handoffs

- `results-reporting`
- `feature-rules` if drivers look leaked
- `eda-sports` for deeper segment dives
