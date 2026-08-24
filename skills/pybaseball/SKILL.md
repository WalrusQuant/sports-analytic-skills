---
name: pybaseball
description: >
  Load MLB Statcast and season batting/pitching tables with pybaseball, and
  hand off team-game modeling to sports_ds MLB pipelines when game-level panels
  are enough. Use for baseball acquisition and pitch-level or season-aggregate
  pulls — even if the user only says "get Statcast" or "pull MLB batting stats."
  Includes bounded-pull guidance, legality handoff, smoke scripts, and clear
  split from sports_ds schedule panels.
version: "0.6.0"
license: MIT
metadata:
  version: "0.6.0"
---

# pybaseball

## Overview

Package skill for https://github.com/jldbc/pybaseball

Use for MLB **pitch-level Statcast** and season batting/pitching tables when you
need baseball depth beyond game-level panels.

For **team-game win/margin/Elo modeling**, prefer the sports_ds MLB path (Stats
API schedule via sportsdataverse), not pybaseball team logs.

---

## When to Use This Skill

Use when:

- MLB pitch-level Statcast analyses
- Season batting/pitching leaderboards from public baseball sources
- Python baseball workflows needing FanGraphs/Baseball Reference style tables
- User says “get Statcast,” “pull batting stats,” “exit velocity,” etc.

Do **not** use when:

| Need | Go instead |
|---|---|
| Non-baseball leagues | other loader skills |
| Simple MLB team-game panel / win/margin/Elo | `sports-ds mlb-*` |
| Environment missing | `environment-setup` |
| Source selection undecided | `data-sources` |

---

## Installation

```bash
pip install -e ".[multi]"
# or
pip install pybaseball
```

---

## Split of Responsibility

| Question | Tool |
|---|---|
| MLB team-game panel, EDA, win/margin/Elo walk-forward | `sports_ds` / `sports-ds mlb-*` |
| Statcast pitches, expected stats, barrels | `pybaseball.statcast*` |
| Season batting/pitching leaderboards | `pybaseball.batting_stats` / `pitching_stats` |

```bash
sports-ds mlb-eda --seasons 2023-2024
sports-ds mlb-win-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds mlb-margin-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds mlb-elo --seasons 2023-2024 --min-train-seasons 1
```

---

## Required Inputs

- Date range and/or season
- Entity (player, team, league-wide)
- Grain (pitch, game, season)
- Decision time T if features will be used pre-pitch/pre-game

---

## Workflow

1. Define grain and date window.
2. If grain is team-game outcomes → use `sports_ds` MLB loaders first.
3. If grain is pitch/Statcast → pull the **smallest** pybaseball table that answers the question.
4. Bound Statcast dates tightly (days/weeks, not whole seasons for exploration).
5. Cache/snapshot results to parquet immediately.
6. Document source function + package version + pull timestamp.
7. Pass through `feature-rules` / `leakage-audit` before pre-pitch/pre-game claims.
8. Log the experiment (`experiment-log`).

---

## Example Loads

```python
from pybaseball import statcast, batting_stats, pitching_stats

# pitch-level (can be large) — bound dates
# pitches = statcast("2024-04-01", "2024-04-07")

batting = batting_stats(2024)
pitching = pitching_stats(2024)
```

Team-game modeling:

```python
from sports_ds.data.mlb import load_mlb_team_game_panel
from sports_ds.pipelines.mlb_win_model import run_mlb_win_pipeline

panel = load_mlb_team_game_panel([2023, 2024])
run_mlb_win_pipeline([2023, 2024], min_train_seasons=1)
```

Patterns: `references/pull_patterns.md`  
Bounds: `references/statcast_bounds.md`

---

## Scripts

```bash
python skills/pybaseball/scripts/smoke_load.py
```

---

## Hard Constraints

1. Statcast pulls can be huge — bound dates.
2. Scrapers break; log package version and date.
3. Do not hammer endpoints in tight loops.
4. Pitch-level fields are not automatically legal pre-pitch features.
5. Snapshot any dataset used for a claim you may need to reproduce.
6. Do not force pybaseball `schedule_and_record` for full-league panels when `sports_ds` MLB schedule works.
7. Never treat season aggregates known only after the season as pre-game features.

---

## Anti-Patterns

- Pulling full-season Statcast for a tiny question
- No local cache/snapshot
- Silent retries that look like hanging agents
- Mixing FanGraphs/Reference definitions without mapping
- Reimplementing team-game win pipelines in notebooks instead of `sports-ds mlb-win-pipeline`
- Using end-of-season leaderboards as pregame inputs

---

## Output Contract

Done means:

- [ ] Grain/window stated
- [ ] Load succeeded or failed clearly
- [ ] Row counts reported
- [ ] Snapshot path optional but recommended
- [ ] Legality handoff done if features will be used pre-event
- [ ] Handoff to feature/validation skills or sports_ds MLB pipeline

---

## Worked Examples

### Quick season batting table
```python
from pybaseball import batting_stats
df = batting_stats(2024)
df.head()
```

### Bounded Statcast pull
```python
from pybaseball import statcast
pitches = statcast("2024-06-01", "2024-06-03")
```

### Team-game model (not pybaseball)
```bash
sports-ds mlb-win-pipeline --seasons 2023-2024 --min-train-seasons 1
```

---

## Bundled Resources

### references/
- `pull_patterns.md`
- `statcast_bounds.md`

### scripts/
- `smoke_load.py`

---

## Related Skills

- `sportsdataverse-py` for MLB schedule API + multi-sport
- `environment-setup`
- `data-sources`
- `feature-rules` / `leakage-audit`
- `experiment-log`
- `predictive-modeling`

---

## Quick Command Card

```bash
pip install -e ".[multi]"
python skills/pybaseball/scripts/smoke_load.py
sports-ds mlb-eda --seasons 2023-2024
sports-ds mlb-win-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds mlb-margin-pipeline --seasons 2023-2024 --min-train-seasons 1
```
