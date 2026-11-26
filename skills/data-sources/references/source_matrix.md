# sportsleader-data dataset choice

Confirm the file in the manifest before committing. This table is the dataset catalog, not a coverage guarantee.

| Question grain | Dataset | Check before use |
|---|---|---|
| One row per game, scores and schedule | `games` | `completed`, null scores, `season_type`, `neutral_site` |
| One row per team per game, box line | `team_box_scores` | two rows per `game_id`, `is_home`, league-specific stat nulls |
| One row per team per game, for and against | `team_game_stats` | same keys; college football follows NFL columns, college basketball follows NBA columns |
| NBA or men's college basketball player-game | `player_game_logs` | `did_not_play`, blank college plus/minus |
| NHL skater-game | `skater_game_logs` | `toi_seconds` nulls in older seasons if a backfill is present |
| NHL goalie-game | `goalie_game_logs` | `starter` |
| MLB batter-game or pitcher-game | `batting_game_logs`, `pitching_game_logs` | `starter`, `batting_order` or `pitching_order` |
| NFL or college football passer, rusher, receiver | `passing_game_logs`, `rushing_game_logs`, `receiving_game_logs` | college blanks called out in the dataset note |
| Who was on the roster as of a date | `rosters` | `valid_from` / `valid_to`; pro leagues only; often current season only |
| Injury, transaction, NFL depth, probables, lineups, weather | matching dataset | source column, valid span, and which seasons the manifest actually lists |

Rules:

- One dataset per fact. Do not mix grains without an aggregation contract.
- Season integers are not comparable across leagues until the numbering rule is applied.
- Play-by-play and pitch-level tables are not in this catalog.
- The user's own file is the fallback when the manifest has no matching dataset. Record its path, grain, and rights. Do not describe it as sportsleader-data.
