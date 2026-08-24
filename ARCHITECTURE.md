# Architecture

## Product

This repo is a **sports modeling skill pack**:

1. `skills/` — deep agent skills (manual + references + scripts)
2. `src/sports_ds/` — installable toolkit the skills operate
3. `sports-ds` CLI — one-command workflows on public sports data

```text
Agent / human
    │
    ├─ skills/<topic>/SKILL.md
    ├─ skills/<topic>/references/
    ├─ skills/<topic>/scripts/
    │
    └─ sports_ds package + sports-ds CLI
           load → EDA → features → baselines/ML → walk-forward → report
```

## Skill layout (every topic)

```text
skills/<skill-id>/
  SKILL.md
  references/
  scripts/
```

## Package layout

```text
src/sports_ds/
  data/
  eda/
  features/
  models/
  validation/
  pipelines/
  cli.py
```

## Standard analysis path

```text
doctrine → load → EDA → time-safe features → baselines
  → statistical and/or predictive models
  → walk-forward validation + leakage + calibration
  → interpret / report / model card / experiment log
```

## First concrete pipeline

`sports-ds nfl-win-pipeline`

- nflverse schedules via nflreadpy
- team-game grain
- shifted pre-game form features
- constant vs logistic vs hist GBM
- season walk-forward

## Design rules

- no future-using features in pre-game models
- baselines before celebrating ML
- walk-forward over random splits for season sports
- package usable without any agent host
- multi-sport skill map; NFL is the first wired pipeline
