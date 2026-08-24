---
name: eda-sports
description: >
  Exploratory data analysis for sports datasets and panels — coverage,
  missingness, distributions, schedule structure, team/player balance,
  outliers, and leakage red flags before modeling. Use after loading
  nflverse/SportsDataverse/pybaseball data and before feature engineering
  or model fitting. Includes sports_ds CLI/API workflows and plotting checks.
version: "0.3.0"
license: MIT
metadata:
  version: "0.3.0"
---

# EDA for Sports Data Science

## Overview

Understand a sports dataset hard enough that modeling choices become obvious.
EDA is not `df.describe()` once. It is a structured pass over grain, time,
entities, missingness, targets, and leakage suspects.

## When to Use This Skill

- New schedule/PBP/roster/stat extract landed
- Before building features or models
- When a model looks “too good” or bizarre
- Comparing seasons for structural breaks (rule changes, shortened seasons)

---

## Installation

```bash
pip install -e .
# optional plots
pip install seaborn
```

---

## EDA Workflow

1. **State expected grain** (game, team-game, player-game, pbp)
2. **Shape & keys** — rows, cols, duplicates
3. **Time coverage** — seasons/weeks/dates complete?
4. **Entity coverage** — teams/players counts; join failures
5. **Missingness** — by column and by season
6. **Target distribution** — win rate, margin histogram, score totals
7. **Segment slices** — home/away, season phase
8. **Leakage scouts** — columns that are outcomes relative to T
9. **Write a short EDA note** — go / repair / stop

---

## Fast Path with `sports_ds`

### CLI

```bash
sports-ds nfl-eda --seasons 2023-2024
```

### API

```python
from sports_ds.data.nfl import load_team_game_panel
from sports_ds.eda.summary import summarize_team_game_panel, format_summary

panel = load_team_game_panel([2023, 2024])
summary = summarize_team_game_panel(panel)
print(format_summary(summary))
```

### Expected summary fields

- `rows`, `n_games`, `n_teams`, `seasons`
- `home_win_rate`, `overall_win_rate`
- `point_diff_mean`, `point_diff_std`
- `null_counts`, `duplicate_rows`

---

## Deeper Checks (Code Patterns)

### Duplicate keys

```python
key = ["game_id", "team"]
dups = panel.duplicated(key).sum()
print("duplicate team-game keys:", dups)
```

### Season-week coverage

```python
print(panel.groupby(["season", "week"]).size().unstack(0).fillna(0).astype(int))
```

### Home advantage snapshot

```python
print(panel.loc[panel.is_home == 1, "won"].mean())
print(panel.groupby("season").apply(lambda d: d.loc[d.is_home == 1, "won"].mean()))
```

### Margin distribution

```python
import matplotlib.pyplot as plt
panel.loc[panel.is_home == 1, "point_diff"].hist(bins=40)
plt.title("Home team point differential")
plt.show()
```

### Leakage scout list (pre-game tasks)

Flag columns that should not be predictors at pre-game T:

- `points_for`, `points_against`, `won`, `point_diff` (current game)
- any same-game PBP aggregates
- post-game EPA with no shift

```bash
python skills/eda-sports/scripts/panel_report.py --seasons 2023-2024
```

---

## Sports EDA Red Flags

| Symptom | Likely issue |
|---|---|
| 33+ NFL “teams” in modern seasons | rename/relocation abbreviations not normalized |
| home_win_rate = 0.5 exactly on team-game panel | expected (each game has one win & one loss row) — use home rows for home advantage |
| Massive missing early season rolling features | normal before windows fill; set min_games thresholds |
| Perfect model accuracy in first fit | leakage until proven otherwise |
| Empty weeks | incomplete schedule load or active season in progress |

---

## EDA Note Template

```text
Dataset: NFL team-game panel seasons …
Source: sports_ds.data.nfl.load_team_game_panel → nflverse schedules
Grain: team-game
Rows/games/teams: …
Home win rate (home rows): …
Missingness: …
Target notes: …
Leakage suspects: …
Structural breaks: …
Decision: proceed to features / repair joins / stop
```

---

## Bundled Resources

### references/

- `eda_checklist.md`

### scripts/

- `panel_report.py` — JSON EDA report for NFL team-game panel

### package code

- `src/sports_ds/eda/summary.py`
- `src/sports_ds/data/nfl.py`

---

## Handoffs

- Features → `feature-rules` / `sports_ds.features`
- Baselines/models → `baseline-models` / `predictive-modeling` / `statistical-modeling`
- Plots for reports → `sports-visualization`
- Validation plan → `validation-design`

---

## Command Card

```bash
sports-ds nfl-eda --seasons 2018-2024
python skills/eda-sports/scripts/panel_report.py --seasons 2018-2024 --out data/eda_panel.json
```
