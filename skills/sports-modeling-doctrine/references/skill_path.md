# Default skill path

```text
sports-modeling-doctrine
 → environment-setup, when the machine or connector is not ready
 → data-sources (sportsleader-data manifest, or the sports-leader connector)
 → eda-sports
 → feature-rules (+ time-series-sports / ratings-strength-models)
 → baseline-models
 → statistical-modeling and/or predictive-modeling
 → validation-design + leakage-audit + calibration-check
 → model-interpretation
 → results-reporting / model-card / experiment-log
```

Use only the steps the question needs. `data-sources` is the acquisition step. The sports-leader connector and a direct Parquet read are two ways to reach the same files.

`sports-visualization` and `anti-slop-analytics` apply wherever a figure is made. `simulation-sports` applies after probabilities exist. `experiment-log` starts before fitting, not after.
