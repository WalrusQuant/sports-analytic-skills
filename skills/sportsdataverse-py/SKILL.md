---
name: sportsdataverse-py
description: >
  Load multi-sport data with the sportsdataverse Python package (NBA, WNBA,
  NCAAB, CFB, NFL, MLB, NHL, soccer, odds, and more). Use when work spans
  leagues or needs SDV/ESPN-style loaders outside pure nflverse NFL releases.
version: "0.1.0"
license: MIT
---

# sportsdataverse-py

Package skill for the SportsDataverse Python distribution.

Upstream docs: [py.sportsdataverse.org](https://py.sportsdataverse.org)  
Install name: `sportsdataverse`

## When to use

- Multi-sport projects
- NBA/WNBA/NCAAB/CFB/NHL/MLB/soccer loads in Python
- ESPN-style scoreboards, rosters, PBP where SDV wraps them
- NFL work that specifically wants SDV’s nfl module (else prefer `nflreadpy`)

## When not to use

- Pure nflverse NFL release loads → prefer `nflreadpy`
- Deep Statcast/FanGraphs baseball pulls → often `pybaseball`
- No packages installed → `environment-setup`

## Required inputs

- League/module
- Endpoint/result type (scoreboard, schedule, pbp, roster, person stats, …)
- Season/event IDs as required by the endpoint
- Desired frame type (polars default in modern SDV parsers; pandas optional)

## Install

```bash
pip install sportsdataverse
# or
pip install -r requirements/python-data.txt
```

## Procedure

1. Identify league module (`nba`, `nfl`, `mlb`, `nhl`, `cfb`, `soccer`, …).
2. Prefer parsed DataFrame returns over raw dicts for analysis.
3. Start with schedule/scoreboard, then deepen to pbp/person stats as needed.
4. Verify timestamps and IDs before joins.
5. Snapshot local parquet for experiments.
6. Hand off to judgment/feature skills.

## Example loads

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

## Scripts in this skill

- `scripts/smoke_load.py` — import modules and attempt a lightweight call

```bash
python skills/sportsdataverse-py/scripts/smoke_load.py
```

## Hard constraints

- Pin down league + endpoint before building features
- Do not assume every SDV function is stable forever; wrap loads and log versions
- Parsed frames still need as-of legality checks
- For NFL release-style bulk PBP, prefer `nflreadpy` unless SDV-specific fields are required
- Respect upstream rate limits and terms

## Anti-patterns

- Importing the entire universe for one scoreboard call
- Mixing raw dict schemas and parsed frames carelessly
- Treating ESPN timestamps as kickoff-safe without checking
- Using SDV odds helpers as CLV truth without `market-data-hygiene`

## Output contract

Done means:

- [ ] League/module selected
- [ ] Load code runs or fails with actionable install/network error
- [ ] Frame type + row counts reported
- [ ] Snapshot plan noted
- [ ] Next skill handoff named

## Handoffs

- `nflreadpy` if NFL bulk releases are a better fit
- `pybaseball` for baseball specialist pulls
- `feature-rules`, `validation-design`, `experiment-log`
- `market-data-hygiene` if odds are included

## References

- https://py.sportsdataverse.org/docs/intro
- https://www.sportsdataverse.org/packages
- `docs/data-ecosystem.md`
