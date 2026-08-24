# Architecture

## System

Sports Analytic Skills is a **sports data science skill library** with an installable toolkit.

```text
Agent / human
    │
    ├─ skills/*/SKILL.md      deep topic manuals
    ├─ skills/*/scripts/      sports-specific runnable helpers
    ├─ skills/*/references/   method detail
    │
    └─ sports_ds package + sports-ds CLI
           load → EDA → features → baselines/ML → walk-forward → report
```

## Package

```text
src/sports_ds/
  data/          loaders (nflverse first)
  eda/           exploratory summaries
  features/      time-safe feature builders
  models/        baselines + predictive models
  validation/    walk-forward splits
  pipelines/     end-to-end workflows
  cli.py
```

## Core analysis path

```text
load data
 → EDA
 → time-safe features
 → baselines
 → statistical or ML model
 → walk-forward validation
 → calibration / interpretation / report
```

## First concrete pipeline

`sports-ds nfl-win-pipeline`

- data: nflverse schedules via nflreadpy
- grain: team-game
- features: shifted pre-game form differentials
- models: constant baseline, logistic, hist GBM
- validation: season walk-forward

## Skill contract

Every topic skill should eventually include:

1. discovery description agents can match
2. install / deps if needed
3. ordered workflow
4. sports-specific decision tables
5. code against `sports_ds` or public loaders
6. `scripts/` agents can execute
7. `references/` for deep method detail
8. worked examples on public sports data
9. reporting template

## Design rules

- no future-using features in pre-game models
- baselines before celebrating ML
- walk-forward over random splits for season sports
- package usable without any agent host
- multi-sport core; no single-sport identity
