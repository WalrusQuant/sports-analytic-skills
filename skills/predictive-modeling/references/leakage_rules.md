# Predictive Leakage Rules

## Illegal for pre-game T

- current game score / won / point_diff
- same-game PBP aggregates
- final season stats applied to early weeks
- opponent season totals that include this game
- target encoding fit on full data including test

## Required patterns

- `shift(1)` before rolling/expanding form
- as-of joins on timestamps
- train-only fit for scalers, imputers, encoders
- walk-forward splits with train time < test time

## Red flags

- walk-forward log-loss far too good
- accuracy near 90%+ on noisy sports outcomes without elite features
- feature importance dominated by something that is secretly an outcome

## Tools

```bash
python skills/predictive-modeling/scripts/leakage_smoke.py
python skills/leakage-audit/scripts/audit_pregame_features.py --seasons 2023-2024
```
