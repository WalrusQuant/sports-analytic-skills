---
name: nflreadpy
description: >
  Load NFL schedules, play-by-play, rosters, and player or team statistics
  directly from nflverse with nflreadpy. Use for NFL acquisition, schema review,
  bounded snapshots, and preparing user-owned analysis artifacts.
license: MIT
metadata:
  version: "0.12.0"
---

# nflreadpy / nflverse Loader

## Outcome

Create a documented, user-owned NFL data artifact at the grain required by the
analysis. Record seasons, loader function and arguments, retrieval time,
installed package version, source release, schema, natural key, row count,
filters, and transformations.

Use nflreadpy for acquisition. Do not let source loading silently define the
analytical grain, prediction cutoff, or legal feature set.

## When to use this skill

Use for NFL schedules and scores, play-by-play, rosters, player or team stats,
snap counts, injuries, and other nflverse releases. For non-NFL sources use the
appropriate public package. Use `data-sources` when the source is undecided and
`feature-rules` before turning loaded fields into prospective predictors.

## Installation

```bash
python -m pip install nflreadpy polars pyarrow
```

The first retrieval may require network access. Record the package version and
cache or snapshot any data used for a durable claim.

## Release selection

| Need | Narrow starting release | Typical grain | Main timing risk |
|---|---|---|---|
| Results or schedule model | schedules | game | future/unplayed and status rows |
| Play analysis | play-by-play | play | post-play fields and drive summaries |
| Player identity | rosters | player-team-season/week | current roster used as history |
| Player performance | player stats | player-week/game/season | aggregation and availability cutoff |
| Participation | snap counts | player-game | known only after event |
| Availability | injuries | player-report | revision time and report stage |

Read [`references/nflverse_releases.md`](references/nflverse_releases.md) when
choosing among releases. Select the narrowest source that contains the required
fields; do not load all play-by-play seasons for a schedule-only question.

## Direct loads

```python
import nflreadpy as nfl

seasons = [2022, 2023, 2024]
schedules = nfl.load_schedules(seasons)
pbp = nfl.load_pbp([2024])
player_stats = nfl.load_player_stats(seasons)
rosters = nfl.load_rosters([2024])
```

Loader availability, return types, and schemas can change by release. Inspect
the installed interface and one bounded result before assuming a function,
column, dtype, or natural key.

```python
import nflreadpy as nfl

print(getattr(nfl, "__version__", "unknown"))
print([name for name in dir(nfl) if name.startswith("load_")])
```

## Acquisition workflow

1. Lock question, analytical grain, seasons, and required fields.
2. Choose the narrowest nflverse release.
3. Load one season first and inspect object type, schema, row count, nulls, and key.
4. Save an immutable raw snapshot before normalization or filtering.
5. Identify schedule status values and distinguish scheduled, completed,
   postponed, canceled, and missing-score rows.
6. Validate team codes, game identifiers, dates, weeks, seasons, and score units.
7. Normalize in a separate derived artifact; preserve source columns or a mapping.
8. Save Parquet plus a JSON or Markdown manifest.
9. Validate the artifact at its intended grain and document known gaps.
10. Hand the explicit saved artifact to EDA, feature, or modeling work.

## Team-game contract

When deriving one row per team per game, require at least:

```text
game_id, season, week, gameday, team, opponent, is_home,
game_type, points_for, points_against, won, tied, point_diff
```

Consider retaining status, season type, kickoff timestamp, neutral-site flag,
overtime/tie indicators, and raw team identifiers. Completed non-tied games
should yield two complementary rows: points and margin reverse, home flags
oppose, and exactly one `won` value is true. For ties, both `won` values may be
false, so preserve an explicit `tied` flag.

Read [`references/panel_contract.md`](references/panel_contract.md) before
normalizing schedules into team-game rows. Preserve raw schedule rows so every
derived row can be audited.

## Validation checks

### Raw game grain

- requested seasons and season types are present;
- `game_id` is unique or duplication is explained;
- completed games have both teams and plausible scores;
- home and away teams differ;
- week, date, season, and status fields are internally consistent;
- duplicate and missing rates are reported by season;
- future or incomplete events are not mislabeled completed.

### Derived team-game grain

- exactly two rows per included contest;
- team/opponent and home/away values are complementary;
- points-for/against and margins reverse across the pair;
- `won`, `tied`, and `point_diff` follow the documented label rule;
- unique-game count is reported beside row count;
- overall row-level win rate is interpreted as a construction property, not home advantage.

### Joins

- stable player/team/game identifiers are preferred over display names;
- join cardinality and unmatched rates are checked;
- roster, injury, and weekly tables use a documented as-of timestamp;
- relocations and historical team abbreviations are mapped explicitly, not silently rewritten.

## Sports-specific traps

- **Doubled-panel trap:** overall win rate is approximately 0.5 because each
  game contributes opponent rows. Estimate home advantage from home rows.
- **Postgame feature trap:** EPA, final score, snap share, and many summaries are
  known after the event. They require lagging or a different decision time.
- **Roster hindsight:** a current roster is not a historical roster snapshot.
- **Week ordering:** postponed games and rescheduling can make week labels differ
  from event-time order. Use timestamps for as-of features.
- **Ties:** coding `won == 0` for both teams is not equivalent to two losses.
- **Schema drift:** columns and dtypes can change across releases or seasons;
  validate before concatenation.
- **Identifiers:** display-name joins can duplicate or mismatch players; use IDs.

## Snapshot manifest

Record:

```text
source: nflverse via nflreadpy
package_version
loader_function_and_arguments
retrieval_timestamp_utc
requested_and_observed_seasons
raw_artifact_path_and_checksum
derived_artifact_path_and_checksum
grain_and_natural_key
row_and_unique_event_counts
filters_and_status_rule
schema_or_schema_path
transformations_and_identifier_mapping
known_gaps_and_validation_results
```

## Hard constraints and integrity rules

1. Prefer documented release loaders over ad-hoc scraping.
2. Do not load broad play-by-play when schedules or stats suffice.
3. Do not use raw post-event fields as pre-event predictors without as-of rules.
4. Do not treat current rosters as historical.
5. Do not train outcome models on incomplete events unless forecasting those
   future events is the explicitly separate purpose.
6. Do not join on player names when stable IDs exist.
7. Do not silently rewrite historical team codes or schemas.
8. Do not model a doubled panel without accounting for paired contest rows.
9. Snapshot the exact data used for claims.
10. Never swallow a load/schema error and return an empty artifact as success.

## Anti-patterns

- pulling every play from every season for a game-score question;
- using postgame EPA in a pre-kickoff model;
- claiming home advantage from the full team-game panel's win rate;
- joining current rosters to historical games;
- concatenating seasons before checking schema drift;
- retaining only normalized output with no source snapshot;
- reporting only row count while hiding duplicate games;
- retry loops that hammer public infrastructure or obscure failure.

## Helpers

```bash
python <path-to-nflreadpy>/scripts/smoke_load.py --season 2024

python <path-to-nflreadpy>/scripts/load_game_panel.py \
  --seasons 2023-2024 \
  --game-types REG \
  --raw-out data/nfl_schedules.parquet \
  --out data/nfl_team_games.parquet

python <path-to-nflreadpy>/scripts/describe_panel.py \
  --input data/nfl_team_games.parquet
```

All helpers parse `--help` before importing nflreadpy. The output files are
user-owned and consumable by any dataframe or modeling tool. The panel helper
defaults to regular-season (`REG`) games, records `game_type` on every derived
row, and requires the requested scope to be verifiable from the source. Pass an
explicit comma-separated scope such as `REG,WC,DIV,CON,SB` when postseason
games belong in the analysis. The panel helper does not replace manifest review
or decision-time feature validation.

## Worked example

For a pregame home-advantage analysis, load schedules rather than play-by-play,
retain completed regular-season games under an explicit status rule, save raw
Parquet, derive paired team-game rows, and report both unique games and rows.
Compute the home rate on `is_home == 1`; do not use the full-panel rate.

## Output contract

Return artifact paths, source release, package version, retrieval timestamp,
loader arguments, requested/observed seasons, grain, natural key, row and event
counts, columns/schema, filters, transformations, known gaps, and sanity-check
results. Name the next artifact consumer without requiring a particular project.

## Resources

- [`references/nflverse_releases.md`](references/nflverse_releases.md) — read
  when selecting the narrowest NFL release.
- [`references/panel_contract.md`](references/panel_contract.md) — read before
  building or validating paired team-game rows.
- `scripts/smoke_load.py` — bounded source probe.
- `scripts/load_game_panel.py` — raw schedule to team-game export.
- `scripts/describe_panel.py` — standalone panel validation and summary.
