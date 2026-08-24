# Architecture

## Product

A **sports data science system**:

1. Python package (`sports_ds`) that loads sports data, explores it, engineers features, models, validates, and reports
2. CLI entrypoints for real workflows
3. Agent skills that operate the package

Code is the product. Skills are the interface for agents.

## Layout

```text
src/sports_ds/
  data/          loaders (nflverse first)
  eda/           exploratory summaries
  features/      time-safe feature builders
  models/        baselines + predictive models
  validation/    walk-forward splits / metrics helpers
  pipelines/     end-to-end workflows
  cli.py
skills/          agent operator manuals for the above
scripts/         thin runners
tests/           unit tests
```

## Core workflow

```text
load data
 → EDA
 → time-safe features
 → baselines
 → model
 → walk-forward validation
 → interpret / report
```

## Current implemented pipeline

`sports-ds nfl-win-pipeline`

- data: nflverse schedules via nflreadpy
- panel: team-game rows
- features: pre-game form only (shifted)
- models: constant baseline, logistic, hist GBM
- validation: season walk-forward

## Next pipelines

- NFL margin/total models
- ratings/Elo module with as-of ratings
- NBA/MLB loaders + one model each
- richer EDA/viz exports

## Design rules

- no future-using features in pre-game models
- baselines before celebrating ML
- walk-forward over random splits for season sports
- keep package usable without any agent host
