---
name: pybaseball
description: >
  Load MLB Statcast, batting, pitching, standings, and player lookup data
  directly with pybaseball. Use for bounded pitch-level pulls, season tables,
  schema checks, and user-owned baseball data artifacts.
license: MIT
metadata:
  version: "0.12.0"
---

# pybaseball

## Outcome

Create a bounded, documented MLB artifact at pitch, player-season, team-season,
or schedule grain. Record function, arguments, retrieval time, schema, coverage,
and all transformations.

## Installation

```bash
python -m pip install pybaseball pandas pyarrow
```

## Choose the correct loader

| Need | Direct library function |
|---|---|
| Player-season batting | `batting_stats(start, end)` |
| Player-season pitching | `pitching_stats(start, end)` |
| Pitch-level Statcast | `statcast(start_dt, end_dt)` |
| Batter-specific pitches | `statcast_batter(start_dt, end_dt, player_id)` |
| Pitcher-specific pitches | `statcast_pitcher(start_dt, end_dt, player_id)` |
| Player identifier | `playerid_lookup(last, first)` |
| Team record | `schedule_and_record(season, team)` |

## Examples

```python
from pybaseball import batting_stats, statcast

batters = batting_stats(2023, 2024, qual=100)
pitches = statcast(start_dt="2024-04-01", end_dt="2024-04-07")
```

Use short date windows first. Large Statcast pulls can be slow and place
unnecessary load on public services.

## Workflow

1. Lock question, grain, seasons or dates, and identifiers.
2. Select the narrowest direct function.
3. Probe a small season or date window.
4. Inspect row count, columns, nulls, duplicates, and units.
5. Resolve players with stable identifiers rather than display names.
6. Chunk long date ranges and cache each immutable chunk.
7. Concatenate only after checking overlap and schema consistency.
8. Save Parquet plus a manifest with function arguments and retrieval time.

## Validation checks

- dates fall inside the requested interval
- player IDs match the intended players
- pitch identifiers are unique at the chosen grain
- handedness, units, and event labels are understood
- season-table qualifiers and minimums are recorded
- chunks do not overlap or leave gaps
- missing values are distinguished from zeroes

## Hard constraints

- Do not request unbounded Statcast history.
- Do not use player names as join keys when IDs are available.
- Do not mix season aggregates with pitch rows without explicit aggregation.
- Do not infer pre-game availability from fields created after the game.
- Respect provider limits and cache successful pulls.

## Helper

```bash
python <path-to-pybaseball>/scripts/smoke_load.py --season 2024
```

The helper imports pybaseball only after parsing arguments and performs one
bounded season-table probe.

## Output contract

Return artifact path, library function and arguments, retrieval timestamp,
grain, natural key, rows, columns, filters, qualifier, coverage gaps, and checks.

## Resources

- `references/pull_patterns.md` — bounded acquisition recipes
- `references/statcast_bounds.md` — request sizing and caching
- `scripts/smoke_load.py` — direct public-library probe
