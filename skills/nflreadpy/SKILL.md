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
analysis. Record seasons, loader function, retrieval time, schema, row count,
source release, and transformations.

## Installation

```bash
python -m pip install nflreadpy polars pyarrow
```

## Direct loads

```python
import nflreadpy as nfl

seasons = [2022, 2023, 2024]
schedules = nfl.load_schedules(seasons)
pbp = nfl.load_pbp([2024])
player_stats = nfl.load_player_stats(seasons)
rosters = nfl.load_rosters([2024])
```

Loader availability can change by release. Inspect `dir(nflreadpy)` and the
official package documentation before assuming a function or schema.

## Workflow

1. Lock the analytical grain and seasons.
2. Select the narrowest nflverse release that contains the required fields.
3. Load one season first and inspect type, columns, row count, and natural key.
4. Normalize only after preserving a raw snapshot.
5. Distinguish scheduled, completed, postponed, and canceled games.
6. Validate team codes, game identifiers, weeks, dates, and scores.
7. Save Parquet plus a JSON or Markdown manifest.
8. Hand the saved artifact to the next analysis skill.

## Team-game contract

When deriving one row per team per game, require:

```text
game_id, season, week, gameday, team, opponent, is_home,
points_for, points_against, won, point_diff
```

Completed games should produce exactly two complementary rows. Preserve the raw
schedule row so the transformation can be audited.

## Helpers

```bash
python <path-to-nflreadpy>/scripts/smoke_load.py --season 2024
python <path-to-nflreadpy>/scripts/load_game_panel.py \
  --seasons 2023-2024 \
  --raw-out data/nfl_schedules.parquet \
  --out data/nfl_team_games.parquet
python <path-to-nflreadpy>/scripts/describe_panel.py \
  --input data/nfl_team_games.parquet
```

All helpers parse `--help` before importing nflreadpy. The output file is owned
by the user and can be consumed by any dataframe or modeling tool.

## Validation checks

- requested seasons are present
- `game_id` is unique at game grain
- completed games have both teams and plausible scores
- home and away teams differ
- dates and week fields are internally consistent
- duplicate and missing rates are reported
- derived team-game rows are paired and complementary

## Hard constraints

- Do not load all play-by-play seasons when schedules suffice.
- Do not treat current rosters as historical without an as-of rule.
- Do not train on rows without a documented completion status.
- Do not join releases on player names when stable IDs exist.
- Do not silently rewrite historical team codes.

## Output contract

Return artifact path, source release, retrieval timestamp, seasons, grain,
natural key, row count, columns, filters, known gaps, and sanity-check results.

## Resources

- `references/nflverse_releases.md` — release selection
- `references/panel_contract.md` — team-game normalization
- `scripts/smoke_load.py` — bounded source probe
- `scripts/load_game_panel.py` — raw schedule to two-row team-game export
- `scripts/describe_panel.py` — portable panel validation and summary
