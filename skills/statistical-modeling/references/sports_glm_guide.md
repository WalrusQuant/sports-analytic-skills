# Sports GLM Guide

## Pick the family from the outcome

| Outcome | Examples | Start here |
|---|---|---|
| Binary | win, cover-style threshold, play success | Logistic / Binomial GLM |
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

### Team goals/points for (with offset for exposure if needed)

```text
goals ~ is_home + attack_rating + opp_defense_rating
```

## Sports-specific traps

1. **Double counting games** in team-game panels when aggregating to league metrics without care.
2. **Using final-season stats** to explain that season’s early games.
3. **Ignoring renames/relocations** (team abbreviations change).
4. **Treating playoff and regular season** as i.i.d. without a flag.
5. **Small-sample players** as fixed effects → insane coefficients. Prefer pooling.

## Coefficient interpretation

- Logistic: exp(beta) = odds ratio for +1 feature change
- Gaussian margin: beta is expected point contribution
- Always state the unit and the reference class (e.g., away=0)

## Model comparison

For prediction:

- log-loss / Brier / MAE on walk-forward folds

For nested explanatory models:

- likelihood ratio tests / AIC can help, but still validate out of time for predictive claims
