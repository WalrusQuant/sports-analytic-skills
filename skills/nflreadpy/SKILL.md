---
name: nflreadpy
description: >
  Load NFL data through sports_ds and nflverse/nflreadpy: schedules, team-game
  panels, PBP, rosters, player stats, and smoke/snapshot scripts. Use for any
  NFL acquisition step before EDA or modeling — even if the user only says
  "get NFL data" or "load schedules." Prefer sports_ds wrappers for modeling
  panels; use raw nflreadpy for lower-level releases. Includes full CLI path
  into win/margin/Elo pipelines, panel traps, and snapshot rules.
version: "0.6.0"
license: MIT
metadata:
  version: "0.6.0"
---

# nflreadpy / nflverse Loader

## Overview

NFL data plane for this repo.

- Prefer **`sports_ds` wrappers** for modeling panels
- Use **raw `nflreadpy`** when you need PBP, rosters, or other nflverse releases directly

Upstream ecosystem: nflverse data releases + `nflreadpy`.

This skill gets data into a clean panel. It does not replace doctrine, EDA, or
leakage checks.

---

## When to Use This Skill

Use when:

- NFL schedules / scores / team-game panels
- nflverse PBP, rosters, player stats, injuries, snaps
- Building inputs for EDA and win/margin/Elo models
- User says “get NFL data” or “load schedules”

Do **not** use when:

| Need | Go instead |
|---|---|
| Non-NFL leagues | `sportsdataverse-py` / `pybaseball` |
| Environment missing | `environment-setup` |
| Source undecided | `data-sources` |
| Feature legality | `feature-rules` |

---

## Installation

```bash
pip install -e .
# nflreadpy comes with sports_ds dependencies
```

First download needs network; later runs use cache.

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
sports-ds nfl-margin-pipeline --seasons 2018-2024
sports-ds nfl-elo --seasons 2018-2024
sports-ds leakage-audit --sport nfl --seasons 2023-2024
sports-ds calibrate --sport nfl --seasons 2018-2024
sports-ds feature-registry | head
```

Code: `src/sports_ds/data/nfl.py`  
Panel contract: `docs/panel-contract.md`

### Team-game panel contract

| Column | Meaning |
|---|---|
| `game_id` | contest id |
| `season`, `week`, `gameday` | time |
| `team`, `opponent` | abbreviations |
| `is_home` | 1 home / 0 away |
| `points_for`, `points_against` | final scores |
| `won`, `point_diff` | derived labels |

Only completed games with non-null scores are kept.

Trap: overall win rate ~0.5 on full panels; home advantage only on `is_home == 1`.

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

Release notes: `references/nflverse_releases.md`  
Panel notes: `references/panel_contract.md`

---

## Workflow

1. Confirm NFL + grain (schedule vs team-game vs pbp).
2. Load via `sports_ds` for modeling panels.
3. Sanity-check row counts, seasons, home win rate.
4. Run EDA (`sports-ds nfl-eda` or `eda-sports` scripts).
5. Build time-safe features / Elo as needed.
6. Hand off to validation + modeling skills.
7. Snapshot any custom join tables you create.

---

## Scripts

```bash
python skills/nflreadpy/scripts/smoke_load.py
python skills/nflreadpy/scripts/load_game_panel.py --seasons 2023-2024
python skills/nflreadpy/scripts/describe_panel.py --seasons 2023-2024
```

---

## Hard Constraints

1. Prefer release loaders over scraping.
2. Do not treat raw PBP columns as pre-game features without as-of rules.
3. Completed games only for outcome models unless forecasting future slates intentionally.
4. Snapshot data used for claims.
5. Keep team abbreviations consistent within a season (nflverse standard).
6. Do not model the doubled panel without understanding home/away rows.

---

## Anti-Patterns

- Loading full PBP for a schedule-only question
- Using post-game EPA as a pre-kickoff feature
- Mixing home and away rows without understanding the doubled panel
- Silent schema drift across nflreadpy versions
- Claiming home advantage from overall win rate on the full panel

---

## Output Contract

Done means:

- [ ] Grain/window stated
- [ ] Load succeeded with row counts
- [ ] Panel contract verified if modeling
- [ ] Home-rate trap checked if relevant
- [ ] Next skill handoff named

---

## Worked Example

```bash
sports-ds nfl-eda --seasons 2018-2024
# expect overall win rate ~0.5; home win rate > 0.5 on is_home==1
sports-ds nfl-win-pipeline --seasons 2018-2024
sports-ds leakage-audit --sport nfl --seasons 2023-2024
```

---

## Bundled Resources

### references/
- `nflverse_releases.md`
- `panel_contract.md`

### scripts/
- `smoke_load.py`
- `load_game_panel.py`
- `describe_panel.py`

---

## Related Skills

- `environment-setup`
- `data-sources`
- `eda-sports`
- `feature-rules`
- `predictive-modeling`
- `ratings-strength-models`

---

## Quick Command Card

```bash
pip install -e .
sports-ds nfl-eda --seasons 2023-2024
sports-ds nfl-win-pipeline --seasons 2018-2024
sports-ds nfl-margin-pipeline --seasons 2018-2024
sports-ds nfl-elo --seasons 2018-2024
python skills/nflreadpy/scripts/smoke_load.py
```
