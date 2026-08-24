# Sports GLM Guide

## Pick the family from the outcome

| Outcome | Examples | Start here |
|---|---|---|
| Binary | win, threshold event, play success | Logistic / Binomial GLM |
| Continuous symmetric | point margin, rating residual | Gaussian OLS/GLM |
| Continuous skewed | possessions-adjusted rates | transform or Gamma |
| Counts | goals, runs, strikeouts | Poisson → NegBin if overdispersed |
| Ordered | win/draw/loss | Ordered logit |

## Standard sports formulas (start minimal)

### Pre-game win probability

```text
won ~ is_home + strength_diff + rest_diff
```

### Margin

```text
point_diff ~ is_home + strength_diff
```

### Team goals/points for

```text
goals ~ is_home + attack_rating + opp_defense_rating
```

## Coefficient interpretation

- Logistic: exp(beta) = odds ratio for +1 feature change
- Gaussian margin: beta is expected point contribution
- Always state the unit and the reference class (e.g., away=0)

## Sports-specific traps

1. **Double counting games** in team-game panels when aggregating without care.
2. **Using final-season stats** to explain that season’s early games.
3. **Ignoring renames/relocations** (team abbreviations change).
4. **Treating playoff and regular season** as i.i.d. without a flag.
5. **Small-sample players** as fixed effects → insane coefficients. Prefer pooling.
6. **Home win rate on team-game panel ≈ 0.5** overall — use home rows for home advantage.

## Model comparison

For prediction:

- log-loss / Brier / MAE on walk-forward folds

For nested explanatory models:

- likelihood ratio tests / AIC can help, but still validate out of time for predictive claims

## Minimal → richer ladder

1. Intercept only / constant rate
2. Home only
3. Home + one strength differential
4. Add form windows / rest
5. Hierarchical team effects
6. Only then nonlinear ML (`predictive-modeling`)
