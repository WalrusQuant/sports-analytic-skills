---
name: model-card
description: >
  Write a model card for a sports model: intended use, data, methods,
  validation, limits, and maintenance. Use when documenting a model version
  for reuse or sharing.
version: "0.1.0"
license: MIT
---

# Model Card (Sports DS)

Durable documentation for a sports analysis/prediction model.

## When to use

- After a model reaches a stable evaluation
- Before sharing results
- Versioning a kept model

## When not to use

- No model yet
- Quick scratch experiment with no keep decision

## Required inputs

- Model/process name and version
- Target and prediction timestamp T (if predictive)
- Data window and sources
- Validation summary
- Baseline comparison summary

## Card sections

1. Identity
2. Intended use / not-for
3. Target and timing
4. Data
5. Features
6. Baselines
7. Validation
8. Results
9. Limits and failure modes
10. Maintenance / retrain / kill conditions

## Procedure

1. Gather evidence from modeling + validation work.
2. Draft all sections; use `unknown` explicitly when needed.
3. Remove unsupported claims.
4. Link `experiment-log` entries.
5. Freeze version.

## Hard constraints

- Never omit baselines if performance is reported
- Never hide leakage/validation status
- Never present exploration as production-ready without saying so

## Output contract

- [ ] All sections present
- [ ] Intended use explicit
- [ ] Baselines + validation summarized
- [ ] Limits written
- [ ] Experiment refs linked or marked none

## Handoffs

- `experiment-log`
- `results-reporting`
- **Stop** when card is frozen

## Worked example

**Identity:** `home_win_logit_v3`  
**Purpose:** Estimate pre-start P(home win) from rating differential and rest.  
**Result:** walk-forward log-loss beat season base rate and Elo-like baseline over 2018–2024.  
**Kill conditions:** two consecutive seasons failing baseline log-loss; major rule/regime break without revalidation.

## References

- `skills/sports-modeling-doctrine`
- `skills/baseline-models`
- `skills/validation-design`
- `skills/experiment-log`
