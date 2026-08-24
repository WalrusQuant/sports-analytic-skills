---
name: sportsdataverse-py
description: >
  Load multi-sport data with sportsdataverse and the sports_ds multi-sport
  panels/pipelines for NBA, MLB, and NHL. Use when work spans leagues or needs
  SDV loaders outside pure nflverse NFL releases — even if the user only says
  "get NBA data", "run MLB win model", or "load NHL schedules." Includes package
  CLI paths, bulk loader recipes, and handoff rules.
version: "0.5.0"
license: MIT
metadata:
  version: "0.5.0"
---

# sportsdataverse-py

## Overview

Package skill for SportsDataverse Python **and** the `sports_ds` multi-sport
wrappers built on top of it.

Upstream docs: https://py.sportsdataverse.org  
Install name: `sportsdataverse`

For bulk NFL release-style loads, prefer `nflreadpy` / `sports_ds.data.nfl`.

---

## When to Use This Skill

Use when:

- Multi-sport projects (NBA / MLB / NHL first-class in `sports_ds`)
- SDV bulk schedule loaders
- ESPN-style scoreboards, rosters, PBP where SDV wraps them

Do **not** use when:

- Pure nflverse NFL release loads → `nflreadpy`
- Deep Statcast/FanGraphs baseball pulls → `pybaseball`
- Environment missing → `environment-setup`

---

## Installation

```bash
pip install -e ".[multi]"
# or
pip install sportsdataverse
```

Requires network on first download.

---

## sports_ds first-class paths (prefer these)

```bash
# panels + EDA
sports-ds nba-eda --seasons 2023-2024
sports-ds mlb-eda --seasons 2023-2024
sports-ds nhl-eda --seasons 2024

# walk-forward win pipelines (form features + baselines + models)
sports-ds nba-win-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds mlb-win-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds nhl-win-pipeline --seasons 2024 --min-train-seasons 1
```

Python:

```python
from sports_ds.data.nba import load_nba_team_game_panel
from sports_ds.data.mlb import load_mlb_team_game_panel
from sports_ds.data.nhl import load_nhl_team_game_panel
from sports_ds.pipelines.nba_win_model import run_nba_win_pipeline
from sports_ds.pipelines.mlb_win_model import run_mlb_win_pipeline
from sports_ds.pipelines.nhl_win_model import run_nhl_win_pipeline

nba = load_nba_team_game_panel([2023, 2024])
mlb = load_mlb_team_game_panel([2023, 2024])
nhl = load_nhl_team_game_panel([2024])  # see NHL caveats

run_nba_win_pipeline([2023, 2024], min_train_seasons=1)
```

Panel contract: `docs/panel-contract.md`

---

## Direct SDV bulk loaders (under the hood)

| Sport | Preferred bulk loader | Notes |
|---|---|---|
| NBA | `sportsdataverse.nba.load_nba_schedule(seasons)` | returns final scores; use `return_as_pandas=True` |
| NHL | `sportsdataverse.nhl.load_nhl_schedule(season)` | some historical dumps corrupt — `sports_ds` skips them |
| MLB | `mlb.mlb_schedule(season=...)` + `parse_mlb_api_schedule` | Stats API dict → parsed frame |

```python
from sportsdataverse.nba import load_nba_schedule
from sportsdataverse.nhl import load_nhl_schedule
from sportsdataverse import mlb
from sportsdataverse.mlb import parse_mlb_api_schedule

nba = load_nba_schedule([2023, 2024], return_as_pandas=True)
nhl = load_nhl_schedule(2024, return_as_pandas=True)
mlb_df = parse_mlb_api_schedule(mlb.mlb_schedule(season=2024, sport_id=1, game_type="R"))
```

Do **not** pass `season=` into `espn_*_schedule` helpers — those take `dates=` and will error or return a single scoreboard slice.

---

## Hard Constraints

1. Prefer bulk release/API loaders over date-by-date scoreboard scraping.
2. Normalize to the shared team-game panel before modeling.
3. Filter completed games; drop duplicate `game_id`s.
4. Sanity-check scores (unique pairs, home-win rate not ~0 or ~1).
5. Snapshot parquet for any claim you may need to reproduce.
6. For NFL bulk PBP/schedules, prefer `nflreadpy` unless SDV-specific fields are required.

---

## NHL caveat (important)

SportsDataverse NHL release dumps are not equally trustworthy by season.
Observed: the 2023 dump can be all `home_score=2`, `away_score=3` (unusable).
`sports_ds.data.nhl` detects corrupt constant-score seasons and skips them.
If every requested season is corrupt/empty, it raises `MultiSportDataError`.
Use a known-good end-year (e.g. 2024) or expand seasons until a valid dump loads.

---

## Workflow

1. Install `[multi]`.
2. Load via `sports_ds` panel helpers when possible.
3. Run EDA (`*-eda`) and confirm home win rate is sane (~0.5x, not 0.0/1.0).
4. Run `*-win-pipeline` under season walk-forward.
5. Hand off to leakage/calibration/reporting skills.

---

## Anti-Patterns

- Using `espn_*_schedule(season=2024)` and thinking you got a season
- Modeling without completed-game filters
- Ignoring corrupt constant-score dumps
- Mixing raw SDV column names with `sports_ds` feature code without normalization
- Silent schema drift mid-experiment

---

## Output Contract

Done means:

- [ ] League chosen
- [ ] Panel rows/teams/seasons reported
- [ ] Home win rate sanity checked
- [ ] Pipeline or explicit blocker reported
- [ ] Next skill handoff named

---

## Bundled Resources

### references/
- `load_patterns.md`
- `when_not_nflreadpy.md`

### scripts/
- `smoke_load.py`

---

## Related Skills

- `data-sources`
- `environment-setup`
- `nflreadpy` for NFL bulk
- `pybaseball` for Statcast depth
- `eda-sports`, `feature-rules`, `validation-design`, `predictive-modeling`

---

## Quick Command Card

```bash
pip install -e ".[multi]"
sports-ds nba-eda --seasons 2023-2024
sports-ds mlb-eda --seasons 2023-2024
sports-ds nhl-eda --seasons 2024
sports-ds nba-win-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds mlb-win-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds nhl-win-pipeline --seasons 2024 --min-train-seasons 1
python skills/sportsdataverse-py/scripts/smoke_load.py
```
