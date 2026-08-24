---
name: pybaseball
description: >
  Load MLB data with pybaseball (Statcast/Savant, batting/pitching tables,
  and related public baseball sources). Use for baseball acquisition and
  pitch-level or season-aggregate pulls in Python.
version: "0.1.0"
license: MIT
---

# pybaseball

Package skill for [pybaseball](https://github.com/jldbc/pybaseball).

## When to use

- MLB pitch-level Statcast analyses
- Season batting/pitching tables from public baseball sources
- Python baseball workflows where SportsDataverse MLB is not enough

## When not to use

- Non-baseball leagues
- Environment missing → `environment-setup`
- Simple MLB API person stats already covered by SDV and already working

## Required inputs

- Date range and/or season
- Entity (player, team, league-wide)
- Grain (pitch, game, season)

## Install

```bash
pip install pybaseball
# or
pip install -r requirements/python-data.txt
```

## Procedure

1. Define grain and date window.
2. Pull the smallest table that answers the question.
3. Cache/snapshot results to parquet.
4. Document source function used (Statcast vs season tables).
5. Pass through `feature-rules` before pre-pitch/pre-game claims.

## Example loads

```python
from pybaseball import statcast, batting_stats, pitching_stats

# pitch-level (can be large)
# pitches = statcast("2024-04-01", "2024-04-07")

batting = batting_stats(2024)
pitching = pitching_stats(2024)
```

## Scripts

- `scripts/smoke_load.py` — import + lightweight season table pull

```bash
python skills/pybaseball/scripts/smoke_load.py
```

## Hard constraints

- Statcast pulls can be huge — bound dates
- Scrapers break; log package version and date
- Do not hammer endpoints in tight loops
- Pitch-level fields are not automatically legal pre-pitch features
- Snapshot any dataset used for a paper claim

## Anti-patterns

- Pulling full-season Statcast for a tiny question
- No local cache/snapshot
- Silent retries that look like hanging agents
- Mixing FanGraphs/Reference definitions without mapping

## Output contract

Done means:

- [ ] Grain/window stated
- [ ] Load succeeded or failed clearly
- [ ] Row counts reported
- [ ] Snapshot path optional but recommended
- [ ] Handoff to feature/validation skills

## Handoffs

- `sportsdataverse-py` for alternate MLB API paths
- `feature-rules` / `leakage-audit`
- `experiment-log`

## References

- https://github.com/jldbc/pybaseball
- `docs/data-ecosystem.md`
