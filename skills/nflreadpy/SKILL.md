---
name: nflreadpy
description: >
  Load NFL data through sports_ds (nflverse via nflreadpy): schedules, team-game
  panels, and lower-level PBP/roster/stat pulls. Use for any NFL acquisition
  step before EDA or modeling. Includes load helpers and smoke scripts.
version: "0.3.0"
license: MIT
metadata:
  version: "0.3.0"
---

# nflreadpy / nflverse Loader

## Overview

NFL data plane for this repo. Prefer the `sports_ds` wrappers for modeling panels; use raw `nflreadpy` when you need PBP, rosters, or other nflverse releases directly.

Upstream ecosystem: nflverse data releases + `nflreadpy`.

## When to Use This Skill

- NFL schedules / scores / team-game panels
- nflverse PBP, rosters, player stats, injuries, snaps
- Building inputs for EDA and win/margin models

## When Not to Use

- Non-NFL leagues → `sportsdataverse-py` / `pybaseball`
- Environment missing → `environment-setup`

---

## Installation

```bash
pip install -e .
# nflreadpy comes in with sports_ds dependencies
```

---

## Load with sports_ds (preferred for modeling)

```python
from sports_ds.data.nfl import load_schedules, load_team_game_panel

sched = load_schedules([2023, 2024])
panel = load_team_game_panel([2023, 2024])
# panel grain: team-game with won, points_for/against, is_home, opponent, ...
```

CLI:

```bash
sports-ds nfl-eda --seasons 2023-2024
sports-ds nfl-win-pipeline --seasons 2018-2024
```

Code: `src/sports_ds/data/nfl.py`

---

## Direct nflreadpy (lower level)

```python
import nflreadpy as nfl

pbp = nfl.load_pbp([2023, 2024])
sched = nfl.load_schedules([2023, 2024])
rosters = nfl.load_rosters([2024])
stats = nfl.load_player_stats([2023, 2024])
```

Always check column names on the version you installed — nflverse schemas evolve.

---

## Scripts

```bash
python skills/nflreadpy/scripts/smoke_load.py
python skills/nflreadpy/scripts/load_game_panel.py --seasons 2023-2024
```

`load_game_panel.py` writes a parquet/csv snapshot of the team-game panel for offline work.

---

## Grain Rules

| Need | Grain | Notes |
|---|---|---|
| Game winner models | team-game or game | team-game doubles each game |
| Home advantage | filter `is_home==1` | overall win rate on team-game ≈ 0.5 |
| Play models | pbp | define T carefully (pre-snap vs post) |
| Player models | player-game / weekly | watch team renames and IDs |

---

## Hard Constraints

1. Prefer release loaders over ad-hoc site scrapes.
2. Snapshot data when an analysis must be reproducible offline.
3. Do not treat in-progress season weeks as complete without noting it.
4. Join keys: `game_id`, team abbreviations — validate renames/relocations.

---

## Next Steps After Load

1. `eda-sports`
2. `feature-rules` / `time-series-sports`
3. `baseline-models` / `statistical-modeling` / `predictive-modeling`
4. `validation-design` / `leakage-audit`

---

## Related Skills

- Environment: `environment-setup`
- Source choice: `data-sources`
- EDA: `eda-sports`
- Multi-sport: `sportsdataverse-py`
