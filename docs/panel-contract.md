# Team-game panel contract

Shared grain for modeling pipelines in `sports_ds`.

## Required columns

| Column | Type | Meaning |
|---|---|---|
| `game_id` | str | Unique game identifier |
| `season` | int | Season year |
| `week` | int | Within-season week. NFL uses nflverse week. Other sports use weeks since the season's first `gameday` (not ISO week). |
| `gameday` | datetime-like (optional) | Game date; required for Oct–Jun sports so form chronology is legal |
| `team` | str | Focal team |
| `opponent` | str | Opposing team |
| `is_home` | 0/1 | 1 if focal team is home |
| `points_for` | float | Points scored by focal team |
| `points_against` | float | Points scored by opponent |
| `won` | 0/1 | 1 if focal team won |
| `point_diff` | float | `points_for - points_against` |

## Rules

1. One row per team per game (two rows per contest).
2. Completed games only for training panels (non-null scores).
3. Overall win rate ~0.5 on full panels; home advantage only on `is_home == 1`.
4. Pre-game features must be shift/as-of legal at decision time T.
5. NFL builder: `sports_ds.data.nfl.load_team_game_panel`
6. NBA builder: `sports_ds.data.nba.load_nba_team_game_panel` (optional `[multi]`)
7. MLB builder: `sports_ds.data.mlb.load_mlb_team_game_panel` (optional `[multi]`)
8. NHL builder: `sports_ds.data.nhl.load_nhl_team_game_panel` (optional `[multi]`)
9. Every builder ends in `validate_panel`: required columns, unique `(game_id, team)`, exactly two rows per `game_id`.
