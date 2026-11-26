---
name: data-sources
description: >
  Choose sportsleader-data Parquet, or the sports-leader connector, for MLB,
  NBA, NFL, NHL, college football, and men's college basketball. Use before
  loading a table, whenever grain, season coverage, or identifiers are unclear.
license: MIT
metadata:
  version: "1.0.0"
---

# Data Sources

sportsleader-data is the default source for this pack. It publishes public Parquet for six leagues. The sports-leader connector reads the same files. This repository does not ship loaders.

## When to use this skill

Use it when:

- the question needs a public table and none has been chosen;
- the grain might be game, team-game, or player-game;
- season numbers, coverage, or ESPN ids are unclear;
- a snapshot and attribution note are part of the plan.

Do not use it when the user already has a table and wants EDA or modeling. Hand that table to `eda-sports`.

| Need | Go instead |
|---|---|
| Coverage, missingness, grain audit | `eda-sports` |
| Decision-time legality | `feature-rules` |
| Machine setup or the connector | `environment-setup` |

## Outcome

A source plan that names the dataset, season window, grain, decision-time fields, snapshot, and what the files do not contain. Source choice does not create predictive validity.

## Where the files are

Catalog:

https://github.com/WalrusQuant/sportsleader-data/releases/download/manifest/manifest.json

File URL:

```text
https://github.com/WalrusQuant/sportsleader-data/releases/download/<league>_<dataset>/<season>.parquet
```

Example published by sportsleader-data:

https://github.com/WalrusQuant/sportsleader-data/releases/download/nba_games/2027.parquet

Each manifest `files` entry has `url`, `rows`, `columns`, `bytes`, `sha256`, `league`, `dataset`, and `season`. Also read `generated_at`, `datasets`, `ids`, and `coverage`. Download a file again only when its `sha256` changed. Column names and types live on that entry. Do not invent a column that the entry does not list.

The same files are available through the sports-leader MCP connector: https://github.com/WalrusQuant/sports-leader-mcp

If that connector is already available (some clients list it as `sports-leader-v05`), call `get_data_status`, then the historical tool for the dataset. Otherwise read the manifest and the Parquet URL.

Historical tools and the datasets they read:

| Tool | Dataset |
|---|---|
| `get_games` | `games` |
| `get_team_box_scores` | `team_box_scores` |
| `get_team_game_stats` | `team_game_stats` |
| `get_player_game_logs` | player logs, selected with the tool's `statGroup` |
| `get_player_trends` | aggregates of those logs |
| `get_rosters` | `rosters` |
| `get_injury_reports` | `injuries` |
| `get_transaction_log` | `transactions` |
| `get_depth_charts` | `depth_charts` |
| `get_probables` | `probables` |
| `get_lineups` | `lineups` |
| `get_weather` | `weather` |

`get_player_game_logs` chooses among `player_game_logs`, `skater_game_logs`, `goalie_game_logs`, `batting_game_logs`, `pitching_game_logs`, `passing_game_logs`, `rushing_game_logs`, and `receiving_game_logs`. Use the tool schema for `statGroup`. Do not guess a value.

Documented filters: `league`, `season` / `seasons`, `from` / `to` (`YYYY-MM-DD`), `team`, `opponent`, `player`, `columns`, `sort`, `order`, and `limit` (default 100, hard cap 250). League codes are `mlb`, `nba`, `nfl`, `nhl`, `cfb`, and `cbb`.

The connector also has live scoreboard, news, and odds tools. Modeling tables for this pack come from the historical export. These Parquet files do not include ratings, forecasts, or betting lines.

## Leagues and season numbers

| Code | League | Season number |
|---|---|---|
| `mlb` | MLB | calendar year |
| `nfl` | NFL | year the season starts |
| `cfb` | college football, FBS, including games against FCS teams and bowls | year the season starts |
| `nba` | NBA | year the season ends, so 2023-24 is `2024` |
| `nhl` | NHL | year the season ends |
| `cbb` | men's college basketball, Division I, including non-Division I opponents and the postseason | year the season ends, so 2020-21 is `2021` |

There is no NHL `2005` season. `season_type` is `regular`, `postseason`, `preseason`, or `nba_cup_final`.

The connector describes the export as these six leagues from the 2021 season through the current season, refreshed nightly. The manifest is the list of files that exist. On the manifest with `generated_at` `2026-11-26T10:17:44+00:00`:

- `games`, team box, team counting stats, and the matching player logs run from 2021 through 2026 for MLB, NFL, and college football, from 2021 through 2027 for men's college basketball, and from 2022 through 2027 for NBA and NHL.
- Rosters, injuries, transactions, depth charts, probables, lineups, and weather on that manifest cover only the latest season or two, not the full game history.

Read `files` again after `generated_at` moves. sportsleader-data can add older pro seasons by a manual backfill (the data README describes NFL from 1999, NBA and NHL from the 1993-94 season, and MLB from 2003). A season is usable here only when the manifest lists its file.

Current-season files are rebuilt nightly, about 4:00 AM America/Chicago. The job refreshes recent games, team lines, player logs, current rosters, and the other current-season extracts named in the sportsleader-data README. Older seasons stay in place until a backfill replaces them.

## Datasets

Descriptions below are the manifest `datasets` notes. Stat columns differ by league. Read `columns` on the file entry before selecting fields.

| Dataset | Leagues | Grain |
|---|---|---|
| `games` | mlb, nba, nfl, nhl, cfb, cbb | one row per game; upcoming games have no score |
| `team_box_scores` | all six | ESPN team box, one row per team per game |
| `team_game_stats` | all six | counting stats for and against, one row per team per game |
| `player_game_logs` | nba, cbb | one row per player per game; college plus/minus is blank |
| `skater_game_logs` | nhl | one row per skater per game |
| `goalie_game_logs` | nhl | one row per goalie per game |
| `batting_game_logs` | mlb | one row per batter per game |
| `pitching_game_logs` | mlb | one row per pitcher per game |
| `passing_game_logs` | nfl, cfb | one row per passer per game |
| `rushing_game_logs` | nfl, cfb | one row per rusher per game |
| `receiving_game_logs` | nfl, cfb | one row per receiver per game; college targets are blank when ESPN does not send them |
| `rosters` | mlb, nba, nfl, nhl | roster spans; empty `valid_to` means still current |
| `injuries` | mlb, nba, nfl, nhl | ESPN plus the NBA official report and the NFL practice report |
| `transactions` | mlb, nba, nfl, nhl | ESPN, plus MLB official |
| `depth_charts` | nfl | depth-chart slots with a valid span |
| `probables` | mlb, nhl | probable pitchers and goalies |
| `lineups` | mlb, nba, nhl | announced batting orders, starting fives, and NHL lines |
| `weather` | mlb, nfl | venue conditions |

Shared `games` columns: `league`, `season`, `season_type`, `game_id`, `game_date`, `start_time`, `status`, `completed`, `home_team_id`, `home_team_abbr`, `home_team_name`, `away_team_id`, `away_team_abbr`, `away_team_name`, `home_score`, `away_score`, `ending`, `neutral_site`, `venue`, `venue_city`, `venue_state`, `venue_country`, `notes`, `series_summary`, `if_necessary`.

Shared team-file columns, then league-specific stats: `league`, `season`, `season_type`, `game_id`, `game_date`, `team_id`, `team_abbr`, `team_name`, `opponent_id`, `opponent_abbr`, `opponent_name`, `is_home`, `score`, `opponent_score`.

Player logs add `player_id` and `player_name`, then the stat line for that dataset. College team rows use the pro columns and leave a stat null when ESPN does not send it. College football counting stats follow the NFL columns. College basketball counting stats follow the NBA columns.

Ids, from the manifest: `game_id` is the ESPN event id; `team_id` and `opponent_id` are ESPN team ids; `player_id` is the ESPN athlete id. Abbreviations and names are on the row, so a file can be used alone. Files are Parquet with zstd compression. Timestamps are UTC.

There is no play-by-play file and no pitch-level file. A question that needs those grains needs a table the user already has rights to, or the question has to change.

## How to read a file

Prefer the connector when it is connected. For a direct read, take `url` from the manifest:

```python
import duckdb
url = "https://github.com/WalrusQuant/sportsleader-data/releases/download/nfl_games/2024.parquet"
games = duckdb.sql(f"""
  SELECT game_id, season, season_type, game_date, start_time, completed,
         home_team_id, away_team_id, home_score, away_score, neutral_site
  FROM read_parquet('{url}')
  WHERE completed
""").df()
```

## Team-game panel from sportsleader-data

Team files (`team_game_stats`, and the same prefix on `team_box_scores`) have `team_id`, `opponent_id`, and `game_date`. `game_date` is a date, not a datetime, and those rows have no `start_time`. `games` has `start_time`. Join it, then derive `event_time`, `won`, and `point_diff`. Rename `team_id` to `team` and `opponent_id` to `opponent`. Ties stay missing until the charter defines them. Do not treat a null score as a zero.

This is the panel `eda-sports`, `feature-rules`, `leakage-audit`, and `statistical-modeling` expect. Each published file is one season. Concatenate the seasons the manifest lists before the join.

```python
import pandas as pd

def read_seasons(dataset, seasons):
    frames = [pd.read_parquet(f"nfl_{dataset}_{season}.parquet") for season in seasons]
    return pd.concat(frames, ignore_index=True)

games = read_seasons("games", [2022, 2023, 2024])
team = read_seasons("team_game_stats", [2022, 2023, 2024])
games = games.loc[games["completed"], ["game_id", "start_time"]]
panel = team.merge(games, on="game_id", how="inner", validate="many_to_one")
panel["event_time"] = pd.to_datetime(panel["start_time"], utc=True)
panel["game_date"] = pd.to_datetime(panel["game_date"])
panel["point_diff"] = panel["score"] - panel["opponent_score"]
panel["won"] = (panel["score"] > panel["opponent_score"]).astype("float")
panel.loc[panel["point_diff"] == 0, "won"] = pd.NA
panel = panel.rename(columns={"team_id": "team", "opponent_id": "opponent"})
```

## Workflow

1. Lock the question, population, target, grain, and decision time T with `sports-modeling-doctrine` when the work is predictive.
2. Pick the dataset whose native grain is the analytical grain, or write the aggregation.
3. Read the manifest entry for that league, dataset, and season. Record `generated_at`, `url`, `sha256`, `rows`, and `columns`.
4. Pull one season before a multi-season download.
5. Check keys, completion, scores, and nulls. See [sanity_checks.md](references/sanity_checks.md).
6. Save the file unchanged, or record the connector arguments and the file `updated_at`.
7. Hand the path to `eda-sports`.

## Provenance

Record league, dataset, season, manifest `generated_at`, file `sha256`, `url` or connector tool and arguments, and retrieval time in UTC. Do not overwrite a file an experiment already cited.

These are revised public rows, not a point-in-time feed of what was known before each game. Injury, lineup, roster, and weather extracts are current-season snapshots on the manifest above. A pre-game feature needs its own as-of rule. If the file has no publication time for a fact, do not treat that fact as known at T.

Game, box, roster, injury, transaction, lineup, depth-chart, and weather rows are collected from public sources, chiefly ESPN, plus the other sources named on each dataset in the sportsleader-data README. Attribute game data to ESPN and to any other named source, and attribute the files to sportsleader-data. sportsleader-data is not affiliated with ESPN, those sources, or the leagues. The underlying data stays under the terms of its source. Read [tos_notes.md](references/tos_notes.md) before redistributing a file.

## Hard constraints

| Do not | Why |
|---|---|
| Invent a dataset or column | The manifest is the schema |
| Assume NBA `2024` is the same season as NFL `2024` | End-year versus start-year labels |
| Use both team rows as independent games | One contest, two perspectives |
| Fill a null score with zero | Upcoming and missing games |
| Join on abbreviations alone across eras | ESPN ids are the stable key; relocated clubs keep that season's name |
| Treat the connector's odds tools as columns in these files | The Parquet export has no betting lines |
| Claim a season file exists because a backfill is documented | Only the manifest lists files |

## Source-plan artifact

```text
Question / league / target:
Grain and natural key / population / decision time T:
Dataset and native grain:
Seasons requested and seasons present in the manifest:
Required columns (copied from the manifest entry):
Connector tool or Parquet URL:
Manifest generated_at / sha256 / rows:
Tie, overtime, and completion rule:
What this file does not contain:
Attribution:
Known gaps:
EDA handoff:
```

Read [source_matrix.md](references/source_matrix.md) when more than one dataset could answer the question.
