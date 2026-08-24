# Walk-Forward Validation for Sports Prediction

## Default: season walk-forward

```text
train seasons < S → test season S
```

Requires `min_train_seasons` prior seasons (default 2).

## Why not random K-fold?

Games are ordered. Random splits leak future strength, roster state, and scheme information into training.

## Expanding vs sliding window

| Style | Train set | Use when |
|---|---|---|
| Expanding | all past seasons | default; more data |
| Sliding | last K seasons only | major rule/style regime change |

## Tuning

- Inner loop: hold out the latest train season or nested walk-forward
- Outer loop: true test seasons untouched by search

## Reporting

Always publish:

- per-test-season metrics
- mean across seasons
- n_train / n_test per fold
- whether baseline was beaten on each fold
