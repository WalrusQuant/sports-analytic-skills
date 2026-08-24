# Team-game panel contract

Shared grain for modeling pipelines in `sports_ds`.

## Required columns

| Column | Type | Meaning |
|---|---|---|
| `game_id` | str | Unique game identifier |
| `season` | int | Season year |
| `week` | int | Week / week proxy |
| `gameday` | datetime-like (optional) | Game date |
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
