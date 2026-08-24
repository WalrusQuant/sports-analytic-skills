---
name: sportsdataverse-py
description: >
  Load public multi-sport data directly with SportsDataverse Python. Use for NBA,
  MLB, NHL, college sports, soccer, and other supported league sources when a
  user needs schedules, box scores, rosters, or event data.
license: MIT
metadata:
  version: "0.7.0"
---

# SportsDataverse Python

## Outcome

Create a user-owned multi-sport artifact with documented league, source module,
loader function, arguments, grain, schema, coverage, retrieval time, and checks.
SportsDataverse APIs vary by version, so discover the installed interface before
performing a large pull.

## Installation

```bash
python -m pip install sportsdataverse pandas pyarrow
```

## Interface discovery

```python
import importlib
import sportsdataverse

league = importlib.import_module("sportsdataverse.nba")
print([name for name in dir(league) if name.startswith("load_")])
```

Consult the installed package documentation and function signatures. Do not
guess a loader name from another league module.

## Workflow

1. Lock sport, competition, grain, seasons, and required fields.
2. Confirm the installed package version and supported league module.
3. Inspect available functions and their signatures.
4. Run the smallest representative request.
5. Convert to pandas only when the next tool requires it.
6. Validate natural keys, dates, teams, scores, duplicates, and missingness.
7. Normalize column names in a separate derived artifact.
8. Save raw and normalized artifacts with retrieval metadata.
9. Record source limitations and a fallback.

## Normalized schedule schema

When preparing game-level analysis, prefer these durable fields:

```text
game_id, season, event_time, home_team, away_team,
home_score, away_score, status, source
```

Keep unmapped source fields rather than discarding them. Derive team-game rows
only after the game-level source artifact passes uniqueness checks.

## Validation checks

- module and loader names are recorded
- requested competitions and seasons are present
- event IDs are unique at game grain
- completed status agrees with non-null outcomes
- team names or IDs are consistent within the source
- timestamps and timezones are understood
- pagination or request limits did not truncate the result
- schema drift across seasons is reported

## Hard constraints

- Do not assume every league module has the same API.
- Do not swallow endpoint or schema errors and return empty data.
- Do not merge leagues before normalizing identifiers and grain.
- Do not treat post-event fields as pre-event predictors.
- Do not perform an unbounded event-level pull.
- Preserve source attribution and retrieval time.

## Helper

```bash
python <path-to-sportsdataverse-py>/scripts/smoke_load.py --modules nba,mlb,nhl
```

The helper parses arguments before importing the optional public package and
performs only a lightweight module probe.

## Output contract

Return artifact paths, package version, league module, loader and arguments,
retrieval timestamp, grain, keys, rows, schema, filters, checks, and known gaps.

## Resources

- `references/load_patterns.md` — robust direct-load patterns
- `references/when_not_nflreadpy.md` — source selection guidance
- `scripts/smoke_load.py` — installed-module probe
