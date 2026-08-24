---
name: sportsdataverse-py
description: >
  Load multi-sport data with sportsdataverse and the sports_ds multi-sport
  panels/pipelines for NBA and MLB (NHL loader exists but is not the focus).
  Use when work spans leagues or needs SDV loaders outside pure nflverse NFL
  releases — even if the user only says "get NBA data", "run MLB win model", or
  "load schedules." Includes package CLI paths, bulk loader recipes, sanity
  checks, and handoff rules.
version: "0.6.0"
license: MIT
metadata:
  version: "0.6.0"
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

- Multi-sport projects (NBA / MLB first-class in `sports_ds`)
- SDV bulk schedule loaders
- ESPN-style scoreboards, rosters, PBP where SDV wraps them
- User says “get NBA data,” “MLB schedules,” “SportsDataverse”

Do **not** use when:

| Need | Go instead |
|---|---|
| Pure nflverse NFL release loads | `nflreadpy` |
| Deep Statcast/FanGraphs baseball pulls | `pybaseball` |
| Environment missing | `environment-setup` |
| Source undecided | `data-sources` |

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

# walk-forward pipelines
sports-ds nba-win-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds nba-margin-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds nba-elo --seasons 2023-2024 --min-train-seasons 1
sports-ds mlb-win-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds mlb-margin-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds mlb-elo --seasons 2023-2024 --min-train-seasons 1

# trust checks
sports-ds leakage-audit --sport nba --seasons 2023-2024
sports-ds calibrate --sport mlb --seasons 2023-2024 --min-train-seasons 1
```

Python:

```python
from sports_ds.data.nba import load_nba_team_game_panel
from sports_ds.data.mlb import load_mlb_team_game_panel
from sports_ds.pipelines.nba_win_model import run_nba_win_pipeline
from sports_ds.pipelines.mlb_margin_model import run_mlb_margin_pipeline

nba = load_nba_team_game_panel([2023, 2024])
mlb = load_mlb_team_game_panel([2023, 2024])
run_nba_win_pipeline([2023, 2024], min_train_seasons=1)
run_mlb_margin_pipeline([2023, 2024], min_train_seasons=1)
```

Panel contract: `docs/panel-contract.md`

---

## Direct SDV bulk loaders (under the hood)

| Sport | Preferred bulk loader | Notes |
|---|---|---|
| NBA | `sportsdataverse.nba.load_nba_schedule(seasons)` | final scores; `return_as_pandas=True` |
| MLB | `mlb.mlb_schedule(season=...)` + `parse_mlb_api_schedule` | Stats API dict → parsed frame |
| NHL | `load_nhl_schedule` | many historical dumps corrupt; not focus |

```python
from sportsdataverse.nba import load_nba_schedule
from sportsdataverse import mlb
from sportsdataverse.mlb import parse_mlb_api_schedule

nba = load_nba_schedule([2023, 2024], return_as_pandas=True)
mlb_df = parse_mlb_api_schedule(mlb.mlb_schedule(season=2024, sport_id=1, game_type="R"))
```

Do **not** pass `season=` into `espn_*_schedule` helpers — those take `dates=` and will error or return a single scoreboard slice.

Patterns: `references/load_patterns.md`  
NFL choice: `references/when_not_nflreadpy.md`

---

## Workflow

1. Install `[multi]`.
2. Load via `sports_ds` panel helpers when possible.
3. Run EDA (`*-eda`) and confirm home win rate is sane.
4. Run win/margin/Elo pipelines under season walk-forward.
5. Run leakage/calibration checks.
6. Hand off to interpretation/reporting skills.

---

## Hard Constraints

1. Prefer bulk release/API loaders over date-by-date scoreboard scraping.
2. Normalize to the shared team-game panel before modeling.
3. Filter completed games; drop duplicate `game_id`s.
4. Sanity-check scores (unique pairs, home-win rate not ~0 or ~1).
5. Snapshot parquet for any claim you may need to reproduce.
6. For NFL bulk PBP/schedules, prefer `nflreadpy` unless SDV-specific fields are required.
7. Do not silently model corrupt dumps.

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

## Worked Examples

### NBA end-to-end
```bash
pip install -e ".[multi]"
sports-ds nba-eda --seasons 2023-2024
sports-ds nba-win-pipeline --seasons 2023-2024 --min-train-seasons 1 --json-out data/nba_win.json
sports-ds leakage-audit --sport nba --seasons 2023-2024
```

### MLB margin + Elo
```bash
sports-ds mlb-margin-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds mlb-elo --seasons 2023-2024 --min-train-seasons 1
```

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
sports-ds nba-win-pipeline --seasons 2023-2024 --min-train-seasons 1
sports-ds mlb-elo --seasons 2023-2024 --min-train-seasons 1
python skills/sportsdataverse-py/scripts/smoke_load.py
```
