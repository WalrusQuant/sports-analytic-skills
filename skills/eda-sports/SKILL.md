---
name: eda-sports
description: >
  Exploratory data analysis for sports datasets and panels — coverage,
  missingness, distributions, schedule structure, team/player balance,
  base rates, outliers, structural breaks, and leakage red flags before
  modeling. Use after loading nflverse/SportsDataverse/pybaseball data and
  before feature engineering or model fitting — even if the user only says
  "look at the data" or "is this panel clean." Includes sports_ds CLI/API
  workflows, plotting checks, and a structured EDA note template.
version: "0.4.0"
license: MIT
metadata:
  version: "0.4.0"
---

# EDA for Sports Data Science

## Overview

Understand a sports dataset hard enough that modeling choices become obvious.

EDA is **not** `df.describe()` once. It is a structured pass over:

- grain and keys
- time coverage
- entities (teams/players)
- missingness
- targets and base rates
- segments (home/away, season phase)
- leakage suspects relative to decision time T

Output: a short EDA note with **go / repair / stop**.

---

## When to Use This Skill

Use this skill when:

- A new schedule / PBP / roster / stat extract landed
- Before building features or models
- A model looks “too good” or bizarre
- Comparing seasons for structural breaks (rule changes, shortened seasons)
- User says “look at the data,” “is this clean,” or “summarize the panel”

Do **not** use this skill as a substitute for:

| Need | Go to |
|---|---|
| Choosing which source to load | `data-sources` |
| Actually loading NFL/MLB/multi-sport | `nflreadpy` / `pybaseball` / `sportsdataverse-py` |
| Building features | `feature-rules` |
| Fitting models | `baseline-models` / `statistical-modeling` / `predictive-modeling` |
| Formal leakage audit after features exist | `leakage-audit` |

---

## Installation

```bash
pip install -e .
# optional plots
pip install seaborn
```

Requires network on first nflverse download.

---

## EDA Workflow

Work in order. Say what you found at each step.

1. **State expected grain** — game, team-game, player-game, pbp, pitch
2. **Shape and keys** — rows, cols, primary key uniqueness, duplicates
3. **Time coverage** — seasons/weeks/dates complete? in-progress season?
4. **Entity coverage** — team/player counts; unexpected IDs; join failures
5. **Missingness** — by column and by season
6. **Target distribution** — win rate, margin histogram, score totals, zero inflation
7. **Segment slices** — home/away, season phase, playoffs vs regular if flagged
8. **Leakage scouts** — columns that are outcomes relative to T
9. **Write the EDA note** — go / repair / stop

If grain is wrong, stop. Do not model a broken panel.

---

## Fast Path with `sports_ds` (NFL team-game)

### CLI

```bash
sports-ds nfl-eda --seasons 2023-2024
sports-ds nfl-eda --seasons 2018-2024
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

| Field | Meaning |
|---|---|
| `rows` | team-game rows |
| `n_games` | unique `game_id` |
| `n_teams` | unique team abbreviations |
| `seasons` | season list |
| `home_win_rate` | win rate on `is_home==1` rows |
| `overall_win_rate` | win rate on all team-game rows (~0.5 expected) |
| `point_diff_mean` / `point_diff_std` | margin moments |
| `null_counts` | nonzero null columns |
| `duplicate_rows` | full-row duplicates |

### JSON report script

```bash
python skills/eda-sports/scripts/panel_report.py --seasons 2023-2024 --out data/eda_panel.json
python skills/eda-sports/scripts/coverage_table.py --seasons 2018-2024
```

---

## Deeper Checks (Code Patterns)

### 1. Duplicate keys

```python
key = ["game_id", "team"]
print("duplicate team-game keys:", panel.duplicated(key).sum())
print("rows per game (expect 2):")
print(panel.groupby("game_id").size().value_counts())
```

### 2. Season–week coverage

```python
print(
    panel.groupby(["season", "week"])
    .size()
    .unstack(0)
    .fillna(0)
    .astype(int)
)
```

Or:

```bash
python skills/eda-sports/scripts/coverage_table.py --seasons 2018-2024
```

### 3. Home advantage snapshot

```python
home = panel[panel.is_home == 1]
print("home win rate:", home["won"].mean())
print(home.groupby("season")["won"].mean())
print("home margin mean:", home["point_diff"].mean())
```

**Critical:** on a team-game panel, **overall** `won.mean()` is ~0.5 because each game contributes one win and one loss row. Always use home rows (`is_home==1`) for home-field estimates.

### 4. Score / margin distributions

```python
import matplotlib.pyplot as plt

home = panel[panel.is_home == 1]
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(home["point_diff"], bins=40, color="steelblue", edgecolor="black", alpha=0.85)
ax.axvline(0.0, color="red", linestyle="--")
ax.set_title(f"Home point differential (n={len(home)})")
ax.set_xlabel("point_diff")
ax.grid(alpha=0.25, axis="y")
plt.show()
```

Also:

```bash
python skills/sports-visualization/scripts/plot_home_margin_hist.py --seasons 2023-2024
```

### 5. Team balance

```python
print(panel.groupby("season")["team"].nunique())
print(panel["team"].value_counts().head(20))
# modern NFL should be 32 teams; 33+ often means rename/relocation abbreviations
```

### 6. Missingness by season

```python
for c in ["gameday", "points_for", "points_against", "won"]:
    if c in panel.columns:
        print(c, panel.groupby("season")[c].apply(lambda s: s.isna().mean()))
```

### 7. Leakage scout list (pre-game tasks)

Flag columns that must **not** be predictors at pre-game T:\n\n- `points_for`, `points_against`, `won`, `point_diff` (current game)\n- any same-game PBP aggregates\n- post-game EPA / win probability added without shift
- final-season stats joined onto early weeks

```python
leakage_suspects = ["points_for", "points_against", "won", "point_diff"]
print("present suspects:", [c for c in leakage_suspects if c in panel.columns])
```

These columns are fine as **targets** or post-game labels. They are illegal as pre-game features.

---

## Grain-Specific Notes

| Grain | Expect | Common mistake |
|---|---|---|
| game | one row per contest | using team-game win rate as game base rate |
| team-game | two rows per game | treating overall win rate as home advantage |
| player-game | uneven n by role | ignoring DNP / inactive without a flag |
| pbp | many rows per game | modeling pre-snap with post-play fields |

State the grain in the EDA note before any model talk.

---

## Sports EDA Red Flags

| Symptom | Likely issue | Action |
|---|---|---|
| 33+ NFL teams in a modern season | rename/relocation abbreviations not normalized | map abbreviations; document |
| overall win rate ≈ 0.5 on team-game panel | expected | use home rows for home advantage |
| home win rate far from historical ~0.55–0.58 | filter bug, incomplete season, or data error | inspect seasons |
| empty weeks | incomplete load or active season | note incomplete weeks |
| massive nulls in early rolling features | normal before windows fill | set min_games thresholds later |
| perfect model accuracy on first fit | leakage until proven otherwise | stop → `leakage-audit` |
| duplicate game_id+team | bad panel build | repair before modeling |
| only one row per game in “team-game” | panel not expanded | rebuild with home+away rows |

See `references/red_flags.md`.

---

## Structural Breaks Checklist

Before pooling many seasons:

- [ ] Rule changes (e.g. extra games, OT rules, shot clock)
- [ ] Shortened / COVID seasons
- [ ] Team moves / renames
- [ ] Tracking data availability start year
- [ ] Playoff vs regular season mixing

If a break is real, either segment analyses or include an explicit era flag known at T.

---

## EDA Note Template

```text
EDA note
Dataset:
Source:
Grain:
Period:
Rows / games / teams (or players):
Keys unique: yes/no
Home win rate (home rows):
Overall win rate (if team-game):
Margin mean/sd (home rows):
Missingness:
Target notes:
Leakage suspects (for pre-game T):
Structural breaks:
Plots produced:
Decision: go to features | repair | stop
Reasons:
```

Save this before feature engineering.

---

## Worked Example (NFL 2023–2024)

```bash
sports-ds nfl-eda --seasons 2023-2024
python skills/eda-sports/scripts/panel_report.py --seasons 2023-2024 --out data/eda_2023_2024.json
python skills/eda-sports/scripts/coverage_table.py --seasons 2023-2024
```

Example findings you should be able to state:

- grain = team-game; ~2 rows per game
- 32 teams
- home win rate on home rows ~0.55-ish (season-dependent)
- overall win rate ~0.50
- leakage suspects present as outcome columns (expected): won, points_*, point_diff
- decision: go to `feature-rules` for pre-game modeling

---

## Integrity Rules

1. State grain before metrics.
2. Do not compute home advantage on all team-game rows.
3. Do not hide missing weeks.
4. Do not proceed to modeling if keys are duplicated or grain is wrong.
5. Separate outcome columns from feature candidates explicitly.
6. Write the go/repair/stop decision down.

---

## Bundled Resources

### references/

| File | Contents |
|---|---|
| `eda_checklist.md` | step checklist |
| `red_flags.md` | symptom → issue table |
| `grain_guide.md` | grain definitions and traps |

### scripts/

| File | Contents |
|---|---|
| `panel_report.py` | JSON EDA report for NFL team-game panel |
| `coverage_table.py` | season×week coverage counts |

### package code

- `src/sports_ds/eda/summary.py`
- `src/sports_ds/data/nfl.py`

---

## Related Skills

| Next | Skill |
|---|---|
| Load NFL | `nflreadpy` |
| Features | `feature-rules` |
| Plots | `sports-visualization` |
| Baselines / models | `baseline-models`, `statistical-modeling`, `predictive-modeling` |
| Validation plan | `validation-design` |
| Leakage after features | `leakage-audit` |

---

## Quick Command Card

```bash
pip install -e .
sports-ds nfl-eda --seasons 2018-2024
python skills/eda-sports/scripts/panel_report.py --seasons 2018-2024 --out data/eda_panel.json
python skills/eda-sports/scripts/coverage_table.py --seasons 2018-2024
python skills/sports-visualization/scripts/plot_home_margin_hist.py --seasons 2023-2024
```
