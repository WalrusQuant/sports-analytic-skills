---
name: eda-sports
description: >
  Run exploratory analysis on sports panels using sports_ds EDA utilities
  and CLI. Use after loading NFL or other team-game data.
version: "0.2.0"
license: MIT
---

# EDA Sports

Uses real code, not vibes.

## Run

```bash
pip install -e .
sports-ds nfl-eda --seasons 2023-2024
```

## Code

```python
from sports_ds.data.nfl import load_team_game_panel
from sports_ds.eda.summary import summarize_team_game_panel, format_summary

panel = load_team_game_panel([2023, 2024])
print(format_summary(summarize_team_game_panel(panel)))
```

Files:

- `src/sports_ds/data/nfl.py`
- `src/sports_ds/eda/summary.py`

## Check

- rows/games/teams
- season coverage
- home win rate
- missingness
- point diff distribution

## Next

- feature build: `sports_ds.features.team_form`
- model: `sports-ds nfl-win-pipeline`
