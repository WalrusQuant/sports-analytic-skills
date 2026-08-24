# Diagnostics Checklist (Sports Stats Models)

## Before fitting

- [ ] Outcome distribution plotted
- [ ] Base rate known
- [ ] Features time-safe at T
- [ ] Train/test chronology defined

## After fitting logistic / probability models

- [ ] Coefficients finite (no perfect separation)
- [ ] Odds ratios + CIs make domain sense
- [ ] Walk-forward log-loss vs constant baseline
- [ ] Calibration curve / Brier
- [ ] Season-stable signs for key effects (home, strength)

## After fitting margin models

- [ ] Residual vs fitted has no strong curve
- [ ] Residual SD not exploding by season
- [ ] Home effect magnitude plausible

## After fitting count models

- [ ] Overdispersion checked
- [ ] Zero inflation considered
- [ ] Predictions not negative

## Leakage / validity

- [ ] No same-game points_for/against as predictors for pre-game model
- [ ] Rolling stats use shift(1)
- [ ] Opponent features as-of pre-game only

## Report

- [ ] n, seasons, formula
- [ ] baselines
- [ ] metrics
- [ ] limits
