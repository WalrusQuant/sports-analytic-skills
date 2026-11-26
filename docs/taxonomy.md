# Skill taxonomy

## Domains

| Domain | Skills |
|---|---|
| foundation | sports-modeling-doctrine |
| data | environment-setup, data-sources |
| eda-viz | eda-sports, sports-visualization, anti-slop-analytics |
| modeling | baseline-models, feature-rules, statistical-modeling, predictive-modeling, ratings-strength-models, time-series-sports |
| validation | validation-design, leakage-audit, calibration-check |
| simulation | simulation-sports |
| reporting | model-interpretation, model-card, results-reporting, experiment-log |

## Composition

```text
environment-setup, when needed
        ↓
data-sources (sportsleader-data manifest or sports-leader connector)
        ↓
eda-sports → feature-rules → baseline-models
        ↓
statistical-modeling and/or predictive-modeling and/or ratings-strength-models
        ↓
validation-design → leakage-audit → calibration-check
        ↓
model-interpretation → results-reporting / model-card / experiment-log
```

Twenty skills. Dataset choice stays in `data-sources`.
