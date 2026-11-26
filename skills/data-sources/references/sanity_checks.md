# First-file checks

Run after the first read of a league, dataset, and season. Stop if a check fails.

1. Row count matches the manifest `rows` value, or the difference is explained.
2. `season` is the requested integer, using that league's numbering.
3. `game_id` is unique on `games`. On a team file, `(game_id, team_id)` is unique and completed games have two rows.
4. `completed` games have non-null scores. Upcoming games do not.
5. Scores are not a single constant.
6. Home win rate, computed on one perspective, is plausible for the sport. A team-file mean of `score > opponent_score` near one half is the paired-row identity, not home advantage.
7. Nulls on the columns the question needs are counted by `season_type`.
8. `sha256` from the manifest is stored with the file.

Ties are `score == opponent_score` on a team file, or equal home and away scores on `games`. Do not label them as wins.
