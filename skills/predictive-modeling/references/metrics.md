# Metrics for Sports Prediction

## Probability models

| Metric | Meaning | Notes |
|---|---|---|
| Log-loss | proper scoring rule for probs | primary default |
| Brier | mean squared error of probs | interpretable |
| Calibration / ECE | reliability of probability bins | required for confidence claims |
| Accuracy | % correct @ 0.5 | weak alone; depends on base rate |

## Regression

| Metric | Use |
|---|---|
| MAE | robust headline error |
| RMSE | penalizes big misses |
| Bias | systematic over/under |

## Pitfalls

- Optimizing accuracy on ~50/50 or 70/30 base rates without context is misleading
- Reporting only in-sample R² is not validation
- “Hot season” cherry-picks are not generalization
- Good ranking (AUC) can coexist with bad calibration
