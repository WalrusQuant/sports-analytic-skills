---
name: sportsdataverse-py
description: >
  Load public multi-sport data directly with SportsDataverse Python. Use for NBA,
  MLB, NHL, college sports, soccer, and other supported league sources when a
  user needs schedules, box scores, rosters, or event data.
license: MIT
metadata:
  version: "0.12.0"
---

# SportsDataverse Python

## Outcome

Create a user-owned multi-sport artifact with documented league, upstream
source, module, loader function, arguments, package version, retrieval time,
grain, schema, coverage, natural key, and validation results.

SportsDataverse modules and upstream endpoints vary. Discover and probe the
installed interface before a large pull; never guess that one league's function
name or parameters apply to another.

## When to use this skill

Use for supported NBA, MLB, NHL, college, soccer, and other multi-sport schedule,
scoreboard, roster, box-score, or event sources. Prefer `nflreadpy` for bulk
nflverse releases and `pybaseball` for Statcast or baseball leaderboard depth.

Read [`references/when_not_nflreadpy.md`](references/when_not_nflreadpy.md) when
choosing an NFL source. Read
[`references/load_patterns.md`](references/load_patterns.md) when choosing the
acquisition depth and snapshot pattern for another module.

## Installation

```bash
python -m pip install sportsdataverse pandas pyarrow
```

Network access and upstream availability are external constraints. Record the
installed package version and preserve successful source responses used in claims.

## Interface discovery

```python
import importlib
import importlib.metadata
import inspect
import pkgutil
import sportsdataverse

print(importlib.metadata.version("sportsdataverse"))
print([
    item.name for item in pkgutil.iter_modules(sportsdataverse.__path__)
    if not item.name.startswith("_")
])
league = importlib.import_module("sportsdataverse.nba")
callables = [
    name for name in dir(league)
    if not name.startswith("_") and callable(getattr(league, name))
]
print(callables)
for name in callables:
    print(name, inspect.signature(getattr(league, name)))
```

Consult the installed package documentation, signature, and return type. A
function may accept `dates` rather than `season`, return nested mappings rather
than a table, or expose different parameters across modules and versions. Do
not restrict discovery to `load_*`: installed releases also expose functions
with provider- and league-prefixed names such as `espn_*`.

## Source and loader decision table

| Need | Start with | Escalate only when | Main risk |
|---|---|---|---|
| Season coverage/results | schedule or bulk season loader | game fields are insufficient | status/schema variation |
| Today's or bounded slate | scoreboard/date loader | detail endpoint is required | assuming one date equals a season |
| Team/player box data | box-score loader | event/play grain is essential | pagination and nested schema |
| Play-by-play/events | event loader | question truly requires it | volume, truncation, post-event fields |
| Rosters | roster loader | historical snapshots are needed | current roster used as historical |
| Multi-league comparison | separate league artifacts first | identifiers/grains are normalized | false schema equivalence |

Prefer bulk schedule/release loaders over date-by-date scraping when the package
offers them. Request event-level data only when schedule or box-score grain
cannot answer the question.

## Acquisition workflow

1. Lock sport, competition, season/date window, grain, and required fields.
2. Confirm installed package version and supported league module.
3. Inspect available functions, signatures, docs, and return types.
4. Run the smallest representative request.
5. Inspect nested structure or columns, dtypes, row count, key, and status values.
6. Save the raw response or minimally converted table before normalization.
7. Check pagination, request limits, and observed coverage.
8. Convert to pandas only if the next user-selected tool requires it.
9. Normalize names and types in a separate derived artifact with a field map.
10. Validate dates, teams, scores, duplicates, missingness, and schema drift.
11. Save raw and normalized artifacts plus a manifest and known fallback.

## Normalized schedule schema

When preparing game-level analysis, prefer durable fields such as:

```text
game_id, season, event_time, home_team, away_team,
home_score, away_score, status, source
```

Also preserve competition/league, season type, neutral-site flag, venue,
timezone, and raw identifiers when available. Keep unmapped source fields in the
raw artifact rather than discarding them. Derive team-game rows only after the
game-level artifact passes uniqueness and completion checks.

## Validation checks

### Interface and retrieval

- package version, module, loader, and exact arguments are recorded;
- the returned object type and conversion steps are documented;
- requested competitions, seasons, or dates are present;
- pagination/request limits did not truncate results;
- empty responses are distinguished from endpoint errors;
- raw artifacts can be traced to a retrieval timestamp and source.

### Game or schedule grain

- event IDs are unique or duplicate causes are resolved;
- home and away identifiers are present and distinct;
- completed status agrees with non-null plausible outcomes;
- scheduled/postponed/canceled events remain distinguishable;
- timestamps and timezones are understood;
- regular season, postseason, neutral sites, ties, and overtime are treated explicitly.

### Cross-season or cross-league data

- schema drift is reported before concatenation;
- team/player IDs and name changes are mapped explicitly;
- units, score conventions, period structures, and grains are not assumed equal;
- each source remains attributable after normalization;
- row counts and missingness are broken out by league and season.

## Multi-sport caveats

- A similarly named column can have different semantics across modules.
- Season labels may refer to start year, end year, or competition-specific codes.
- Scoreboard helpers often accept dates and return only a bounded slate; they
  are not necessarily season loaders.
- Historical dumps or upstream feeds can contain constant scores, duplicates,
  missing periods, or incomplete seasons. Sanity-check distributions.
- Current rosters and post-event box scores are not automatically legal
  pre-event predictors.
- Ties, overtime, shootouts, doubleheaders, aggregate legs, neutral venues, and
  postseason formats differ by sport.
- A shared normalized schema aids storage but does not erase sport-specific logic.

## Team-game derivation

If a downstream analysis requires team-game grain:

1. validate one unique completed source row per contest;
2. preserve the raw game row and status;
3. emit two complementary rows with shared `game_id`;
4. reverse team/opponent, home flag, scores, and margin correctly;
5. preserve tie/overtime/neutral-site semantics;
6. report both team-row and unique-game counts;
7. verify the full-panel win rate is understood as a construction property.

Do not normalize directly from an unchecked, possibly truncated scoreboard response.

## Snapshot manifest

```text
package_and_version
league_module
upstream_source_if_known
loader_and_exact_arguments
retrieval_timestamp_utc
requested_and_observed_coverage
raw_artifact_path_and_checksum
normalized_artifact_path_and_checksum
grain_and_natural_key
rows_events_teams_and_seasons
status_filter_and_timezone
field_mapping_and_transformations
pagination_or_request_limit_check
schema_drift_known_gaps_and_fallback
```

## Hard constraints and integrity rules

1. Never assume league modules expose the same API.
2. Never guess loader arguments without inspecting the installed signature.
3. Never swallow endpoint or schema errors and return empty data as success.
4. Never merge leagues before normalizing identifiers, units, and grain.
5. Never treat post-event fields as pre-event predictors.
6. Never perform an unbounded event-level pull.
7. Preserve source attribution, package version, and retrieval time.
8. Filter completed games under a documented status rule for outcome analysis.
9. Validate pagination, uniqueness, scores, and schema before modeling.
10. Preserve raw source data separately from normalized derivatives.

## Anti-patterns

- passing a `season` argument to a date-only scoreboard helper;
- believing one scoreboard response contains an entire season;
- modeling rows with incomplete or ambiguous status;
- ignoring constant-score or duplicate-event corruption;
- normalizing disparate leagues by column name alone;
- silent schema drift across seasons;
- loading play-by-play when schedules answer the question;
- claiming success from a zero-row table after an upstream failure;
- converting/discarding nested fields before saving the raw response.

## Worked examples

### Bounded module probe

Discover functions for the installed NBA module, inspect the candidate schedule
loader signature, request one small season/date slice, record return type and
schema, and expand only after checking event IDs and coverage.

### Multi-league schedule comparison

Acquire and validate each league separately. Save league-specific raw snapshots,
normalize only common game-level fields with a source column, retain sport-
specific fields separately, and compare rates only after aligning competition,
season type, status, and denominator definitions.

## Helper

```bash
python <path-to-sportsdataverse-py>/scripts/smoke_load.py \
  --modules nba,mlb,nhl --list-modules
```

The helper parses arguments before importing the optional public package and
uses installed distribution metadata for the version. It discovers real public
namespaces, imports every requested module, and exits nonzero if any requested
module fails; a partial probe is not reported as success. It does not call an
endpoint or prove that a particular loader/source is healthy.

## Output contract

Return raw and normalized artifact paths, package version, league module,
upstream source if known, loader and arguments, retrieval time, grain, natural
key, rows/events, schema, filters, coverage, mapping, pagination check, known
gaps, fallback, and validation results.

## Resources

- [`references/load_patterns.md`](references/load_patterns.md) — read when
  choosing schedule, box-score, or event acquisition depth and snapshot shape.
- [`references/when_not_nflreadpy.md`](references/when_not_nflreadpy.md) — read
  when choosing between SportsDataverse and nflreadpy for NFL data.
- `scripts/smoke_load.py` — lightweight installed-module probe.
