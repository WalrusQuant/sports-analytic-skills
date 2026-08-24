---
name: nflreadpy
description: >
  Load NFL data through sports_ds data layer (nflverse/nflreadpy). Use to
  pull schedules and build team-game panels for analysis/modeling.
version: "0.2.0"
license: MIT
---

# nflreadpy / nflverse loader

## Install

```bash
pip install -e .
```

## Load data with the system

```python
from sports_ds.data.nfl import load_schedules, load_team_game_panel

sched = load_schedules([2023, 2024])
panel = load_team_game_panel([2023, 2024])
```

CLI:

```bash
sports-ds nfl-eda --seasons 2023-2024
```

## Direct nflreadpy (lower level)

```python
import nflreadpy as nfl
pbp = nfl.load_pbp([2023, 2024])
stats = nfl.load_player_stats([2023, 2024])
```

## Code

- `src/sports_ds/data/nfl.py`

## Next

- EDA: `sports-ds nfl-eda`
- Model: `sports-ds nfl-win-pipeline`
