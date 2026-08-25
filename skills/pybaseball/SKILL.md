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
or schedule grain. Record the function and arguments, package version, retrieval
time, schema, coverage, natural key, qualifier rules, and transformations.

Pybaseball is especially useful for Statcast depth and public batting/pitching
tables. Source convenience does not make every returned field legal for a
pre-pitch or pregame model.

## When to use this skill

Use for pitch-level Statcast analysis, player-specific pitch pulls, season
batting and pitching tables, player identifier lookup, and selected team records.
For a general full-league schedule panel, evaluate whether a schedule-oriented
source is narrower and more stable. Use a multi-sport source for other leagues.

## Installation

```bash
python -m pip install pybaseball pandas pyarrow
```

Public endpoints can be slow or change. Start small, cache successful pulls,
record versions, and avoid aggressive retries.

## Provider-health boundary

Pybaseball is a collection of clients and scrapers over multiple upstream
providers, not one uniform service. A successful import proves nothing about
FanGraphs, Baseball Savant, Baseball Reference, Chadwick, or Retrosheet health.
Probe the exact function family required for the analysis and record the
provider separately.

In particular, `batting_stats` and `pitching_stats` are FanGraphs-backed. The
upstream project has reports of FanGraphs returning HTTP 403/CAPTCHA responses;
see [pybaseball issue #507](https://github.com/jldbc/pybaseball/issues/507).
This is a provider/interface-health warning, not evidence that every pybaseball
function is unavailable. Statcast uses Baseball Savant and must be probed
independently. Do not bypass access controls or hammer retries. If the required
provider is unhealthy, fail visibly, preserve the error and retrieval time, and
use a documented licensed/official alternative or a previously verified
snapshot rather than treating an empty frame as data.

## Choose the correct loader

| Need | Direct function | Grain | Important caveat |
|---|---|---|---|
| Player-season batting | `batting_stats(start, end)` | player-season | qualifiers and provider definitions |
| Player-season pitching | `pitching_stats(start, end)` | player-season | innings/qualification filters |
| League pitch data | `statcast(start_dt, end_dt)` | pitch | potentially large; bound dates |
| Batter-specific pitches | `statcast_batter(start_dt, end_dt, player_id)` | pitch | use stable MLBAM ID |
| Pitcher-specific pitches | `statcast_pitcher(start_dt, end_dt, player_id)` | pitch | use stable MLBAM ID |
| Player identifier | `playerid_lookup(last, first)` | candidate person matches | resolve ambiguity explicitly |
| Team schedule/record | `schedule_and_record(season, team)` | team-game | not automatically a full-league panel |

Read [`references/pull_patterns.md`](references/pull_patterns.md) for concise
season-table and Statcast call patterns. Read
[`references/statcast_bounds.md`](references/statcast_bounds.md) before any
multi-day, multi-player, or repeated Statcast acquisition.

## Example loads

```python
from pybaseball import batting_stats, pitching_stats, statcast

batters = batting_stats(2023, 2024, qual=100)
pitchers = pitching_stats(2024, 2024, qual=50)
pitches = statcast(start_dt="2024-04-01", end_dt="2024-04-07")
```

Use a short date window first. Inspect the returned schema and units before
requesting a larger interval.

## Acquisition workflow

1. Lock the question, grain, date/season range, entity, and required fields.
2. Define decision time if the artifact may feed a prospective model.
3. Choose the narrowest direct function and stable identifiers.
4. Probe one player, one season table, or a short date interval.
5. Inspect rows, columns, dtypes, nulls, duplicates, units, and category values.
6. For long intervals, define non-overlapping chunks with retry and stop rules.
7. Save each successful immutable chunk before requesting the next.
8. Check chunk coverage, overlap, schema consistency, and key uniqueness.
9. Concatenate only validated chunks; retain raw artifacts separately.
10. Save Parquet plus a manifest containing exact function arguments.

## Statcast planning

Estimate scope before pulling:

```text
date_start / date_end
league-wide or player-specific
expected active days
required columns
chunk interval
natural pitch key
retry/backoff limit
raw chunk naming
coverage and overlap check
```

Prefer days or weeks for exploration. A full season can contain hundreds of
thousands of pitches and may be unnecessary. Do not loop player-by-player when
a single bounded league-wide pull plus local filter answers the question.

## Validation checks

### All artifacts

- observed dates or seasons match the request;
- player IDs resolve to intended people;
- natural keys are unique at declared grain or duplicates are explained;
- package version, function, arguments, and retrieval time are recorded;
- missing values are distinguished from structural zeroes;
- source columns and any renamed fields have a mapping.

### Statcast

- pitch/game identifiers and event dates are plausible;
- chunk boundaries have neither gaps nor overlapping duplicate rows;
- handedness, coordinate systems, velocity/distance units, and event labels are understood;
- pitch outcomes and plate-appearance outcomes are not mixed silently;
- post-pitch or postgame variables are not treated as pre-pitch/pregame information.

### Season tables

- qualifier, minimum plate appearances/innings, and year semantics are recorded;
- counting and rate statistics are not compared without opportunity context;
- provider-specific definitions are not assumed equivalent to another source;
- multi-year results are checked for one-row-per-player-year versus aggregated rows.

## Baseball-specific caveats

- Statcast coverage and field definitions vary by era; avoid claiming uniform
  measurement across years without checking.
- Pitch rows are nested within plate appearances, games, pitchers, and batters.
  Row-level independence is usually false.
- Expected metrics, run values, and final event labels may use information not
  available at the decision time of a prospective model.
- Two players can share names and players can change display names. Join on IDs.
- Park, weather, handedness, count, opponent, and role changes can confound raw comparisons.
- End-of-season leaderboards contain future information for in-season prediction.
- Schedule and record functions are team-scoped; assembling a league panel
  requires explicit deduplication and game-key validation.

## Snapshot manifest

```text
source: pybaseball and underlying public provider
package_version
function_and_exact_arguments
retrieval_timestamp_utc
requested_and_observed_window
entity_ids_and_resolution_notes
grain_and_natural_key
row_count_and_schema
qualifier_or_minimums
raw_chunks_and_checksums
combined_artifact_and_checksum
units_and_definition_notes
filters_transformations_and_known_gaps
```

## Hard constraints and integrity rules

1. Never request unbounded Statcast history.
2. Never use display names as join keys when stable IDs are available.
3. Never mix season aggregates with pitch rows without explicit aggregation.
4. Never infer pre-event availability from a field produced after the event.
5. Respect public services; cache pulls and bound retries.
6. Snapshot every dataset supporting a durable claim.
7. Record qualifiers and provider-specific metric definitions.
8. Validate chunk gaps, overlaps, and schema drift before concatenation.
9. Do not return an empty frame as a successful acquisition when the source failed.
10. Do not treat missing numeric values as zero without semantic evidence.

## Anti-patterns

- a full-season Statcast pull for a question answerable with three days;
- no local snapshot or provenance manifest;
- silent retries that look like a hanging process;
- joining players by display name;
- mixing FanGraphs, Baseball Reference, and Statcast definitions without mapping;
- end-of-season rates used as pregame features;
- concatenating overlapping chunks and inflating pitch counts;
- comparing rate leaders without opportunity thresholds;
- assuming every Statcast column existed or meant the same thing in every era.

## Worked examples

### Bounded pitch analysis

Resolve the player ID, pull a three-to-seven-day interval, validate the player's
identity and date coverage, record units and pitch key, save raw Parquet, then
expand only if the small pull answers the schema and volume questions.

```python
from pybaseball import statcast_pitcher

pitches = statcast_pitcher("2024-06-01", "2024-06-07", player_id=123456)
```

### Season batting comparison

Call `batting_stats` with an explicit qualifier, preserve the `Season` and
stable player identifier columns, report opportunity, and state the provider's
metric definition before ranking players.

## Helper

```bash
python <path-to-pybaseball>/scripts/smoke_load.py --season 2024
```

The helper parses arguments before importing pybaseball and performs one bounded
FanGraphs-backed season-table probe. It exits nonzero on import errors, provider
errors, and zero-row or zero-column responses. It is not a Statcast health check
or a complete snapshot.

## Output contract

Return artifact paths, package version, function and arguments, retrieval time,
grain, natural key, rows, schema, filters, qualifier, identifiers, date/season
coverage, chunk audit, units, known gaps, and validation results.

## Resources

- [`references/pull_patterns.md`](references/pull_patterns.md) — read when
  selecting a bounded season-table or Statcast call.
- [`references/statcast_bounds.md`](references/statcast_bounds.md) — read before
  planning chunk size, caching, or repeated pulls.
- `scripts/smoke_load.py` — bounded direct-library probe.
