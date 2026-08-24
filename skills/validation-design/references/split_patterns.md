# Split Patterns for Sports

## Season walk-forward

```text
train 2018-2019 → test 2020
train 2018-2020 → test 2021
...
```

Use when seasons are natural regeneration boundaries.

## Week walk-forward inside a season

Useful for in-season models with large within-season samples. Still never train on week t to predict week t without shift-safe features.

## Sliding window

```text
train last 3 seasons → test next season
```

Use after major rule/style shifts.

## What not to do

- Shuffle all games, 5-fold CV, report mean accuracy
- Train on 2018-2024, test on 2023
- Use future opponent rest/injury known only after lock
