---
name: sportsdataverse-py
description: >
  Load multi-sport data with the sportsdataverse Python package (NBA, WNBA,
  NCAAB, CFB, NFL, MLB, NHL, soccer, and more). Use when work spans leagues or
  needs SDV/ESPN-style loaders outside pure nflverse NFL releases — even if the
  user only says "get NBA data" or "load CFB schedules." Includes install,
  example loads, smoke scripts, and handoff rules.
version: "0.4.0"
license: MIT
metadata:
  version: "0.4.0"
---

# sportsdataverse-py

## Overview

Package skill for the SportsDataverse Python distribution.

Upstream docs: https://py.sportsdataverse.org  
Install name: `sportsdataverse`

For bulk NFL release-style loads, prefer `nflreadpy` unless you need SDV-specific fields.

---

## When to Use This Skill

Use when:

- Multi-sport projects
- NBA/WNBA/NCAAB/CFB/NHL/MLB/soccer loads in Python
- ESPN-style scoreboards, rosters, PBP where SDV wraps them
- NFL work that specifically wants SDV’s nfl module

Do **not** use when:

- Pure nflverse NFL release loads → `nflreadpy`
- Deep Statcast/FanGraphs baseball pulls → often `pybaseball`
- No packages installed → `environment-setup`

---

## Installation

```bash
pip install -e ".[multi]"
# or
pip install sportsdataverse
```

---

## Required Inputs

- League/module
- Endpoint/result type (scoreboard, schedule, pbp, roster, person stats, …)
- Season/event IDs as required by the endpoint
- Desired frame type (polars default in modern SDV parsers; pandas optional)

---

## Workflow

1. Identify league module (`nba`, `nfl`, `mlb`, `nhl`, `cfb`, `soccer`, …).
2. Prefer parsed DataFrame returns over raw dicts for analysis.
3. Start with schedule/scoreboard, then deepen to pbp/person stats as needed.
4. Verify timestamps and IDs before joins.
5. Snapshot local parquet for experiments.
6. Hand off to EDA/feature skills.
7. Apply as-of legality checks before modeling.

---

## Example Loads

```python
# NBA scoreboard (parsed polars in current SDV defaults)
from sportsdataverse.nba import espn_nba_scoreboard
nba_sb = espn_nba_scoreboard()

# MLB person season stats via API + parser pattern
from sportsdataverse.mlb import mlb_api_person_stats, parse_mlb_api_person_stats
judge = parse_mlb_api_person_stats(
    mlb_api_person_stats(person_id=592450, stats="season", season=2024)
)

# NHL PBP parse pattern
from sportsdataverse.nhl import nhl_web_pbp, parse_nhl_web_pbp
# pbp = parse_nhl_web_pbp(nhl_web_pbp(game_id))
```

Exact function names can evolve — check current SDV docs if an import fails.

More patterns: `references/load_patterns.md`

---

## Scripts

```bash
python skills/sportsdataverse-py/scripts/smoke_load.py
```

---

## Hard Constraints

1. Pin down league + endpoint before building features.
2. Do not assume every SDV function is stable forever; wrap loads and log versions.
3. Parsed frames still need as-of legality checks (`feature-rules`).
4. For NFL release-style bulk PBP, prefer `nflreadpy` unless SDV-specific fields are required.
5. Respect upstream rate limits and terms.

---

## Anti-Patterns

- Importing the entire universe for one scoreboard call
- Mixing raw dict schemas and parsed frames carelessly
- Treating ESPN timestamps as kickoff-safe without checking
- Silent schema drift mid-experiment

---

## Output Contract

Done means:

- [ ] League/module selected
- [ ] Load code runs or fails with actionable install/network error
- [ ] Frame type + row counts reported
- [ ] Snapshot plan noted
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

- `nflreadpy` if NFL bulk releases are a better fit
- `pybaseball` for baseball specialist pulls
- `environment-setup`
- `data-sources`
- `eda-sports`, `feature-rules`, `validation-design`, `experiment-log`

---

## Quick Command Card

```bash
pip install -e ".[multi]"
python skills/sportsdataverse-py/scripts/smoke_load.py
```
