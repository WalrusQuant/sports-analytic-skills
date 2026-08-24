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
  data/          # nfl/nba/mlb loaders, team-game + NFL player panels
  eda/
  features/      # time-safe team form (rich EWMA/rest) + player form
  ratings/       # as-of Elo
  metrics/       # log-loss, brier, calibration/ECE
  audit/         # leakage audits
  models/        # baselines, classifiers, regressors, ensembles
  validation/    # season walk-forward masks
  pipelines/     # team win/margin/elo, rich win ladder, NFL player
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
| `sports-ds nfl-win-rich` | rich features + logistic/GBM/Elo ensemble |
| `sports-ds nfl-margin-pipeline` | form features + margin walk-forward |
| `sports-ds nfl-elo` | as-of Elo + logistic walk-forward |
| `sports-ds nfl-player-eda` | NFL skill-position player panel EDA |
| `sports-ds nfl-player-pipeline` | player form + fantasy/volume walk-forward |
| `sports-ds nba-player-eda` | NBA player boxscore panel EDA (needs `[multi]`) |
| `sports-ds nba-player-pipeline` | NBA player form + fantasy/points walk-forward |
| `sports-ds mlb-player-eda` | MLB batter boxscore panel EDA (needs `[multi]`) |
| `sports-ds mlb-player-pipeline` | MLB batter form + fantasy walk-forward (cached boxscores) |
| `sports-ds calibrate` | win-logistic calibration/ECE |
| `sports-ds leakage-audit` | pre-game form time-safety audit |
| `sports-ds nba-eda` | NBA team-game panel EDA (needs `[multi]`) |
| `sports-ds nba-win-pipeline` | NBA win walk-forward (needs `[multi]`) |
| `sports-ds nba-margin-pipeline` | NBA margin walk-forward (needs `[multi]`) |
| `sports-ds nba-elo` | NBA Elo baseline walk-forward (needs `[multi]`) |
| `sports-ds mlb-eda` | MLB team-game panel EDA (needs `[multi]`) |
| `sports-ds mlb-win-pipeline` | MLB win walk-forward (needs `[multi]`) |
| `sports-ds mlb-margin-pipeline` | MLB margin walk-forward (needs `[multi]`) |
| `sports-ds mlb-elo` | MLB Elo baseline walk-forward (needs `[multi]`) |
| `sports-ds feature-registry` | Print feature legality registry |
| `sports-ds calibrate --sport` | Calibration for nfl/nba/mlb |
| `sports-ds leakage-audit --sport` | Leakage audit for nfl/nba/mlb |

## Design rules

- no future-using features in pre-game models
- baselines before celebrating ML
- walk-forward over random splits for season sports
- package usable without any agent host
- multi-sport skill map; NFL deepest, NBA second wired path
- skills drive package APIs; scripts should not reimplement core math
