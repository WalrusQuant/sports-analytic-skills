# Architecture

## Product

This repo is a **sports modeling skill pack**:

1. `skills/` — deep agent skills (manual + references + scripts)
2. `src/sports_ds/` — installable toolkit the skills operate
3. `sports-ds` CLI — one-command workflows on public sports data

See `docs/product-charter.md` for scope and v1 success criteria.

```text
Agent / human
    │
    ├─ skills/<topic>/SKILL.md
    ├─ skills/<topic>/references/
    ├─ skills/<topic>/scripts/
    │
    └─ sports_ds package + sports-ds CLI
           load → EDA → features/ratings → baselines/ML
           → walk-forward → leakage/calibration → report
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
  data/          # nfl, nba loaders + team-game panels
  eda/
  features/      # time-safe pre-game form
  ratings/       # as-of Elo
  metrics/       # log-loss, brier, calibration/ECE
  audit/         # leakage audits
  models/        # baselines, classifiers, margin regressors
  validation/    # season walk-forward masks
  pipelines/     # nfl win/margin/elo, nba win
  cli.py
```

## Standard analysis path

```text
doctrine → load → EDA → time-safe features / ratings → baselines
  → statistical and/or predictive models
  → walk-forward validation + leakage + calibration
  → interpret / report / model card / experiment log
```

## Concrete pipelines (package CLI)

| Command | What it does |
|---|---|
| `sports-ds nfl-eda` | NFL team-game panel EDA |
| `sports-ds nfl-win-pipeline` | form features + win walk-forward |
| `sports-ds nfl-margin-pipeline` | form features + margin walk-forward |
| `sports-ds nfl-elo` | as-of Elo + logistic walk-forward |
| `sports-ds calibrate` | win-logistic calibration/ECE |
| `sports-ds leakage-audit` | pre-game form time-safety audit |
| `sports-ds nba-eda` | NBA team-game panel EDA (needs `[multi]`) |
| `sports-ds nba-win-pipeline` | NBA win walk-forward (needs `[multi]`) |
| `sports-ds mlb-eda` | MLB team-game panel EDA (needs `[multi]`) |
| `sports-ds mlb-win-pipeline` | MLB win walk-forward (needs `[multi]`) |
| `sports-ds nhl-eda` | NHL team-game panel EDA (needs `[multi]`) |
| `sports-ds nhl-win-pipeline` | NHL win walk-forward (needs `[multi]`) |

## Design rules

- no future-using features in pre-game models
- baselines before celebrating ML
- walk-forward over random splits for season sports
- package usable without any agent host
- multi-sport skill map; NFL deepest, NBA second wired path
- skills drive package APIs; scripts should not reimplement core math
