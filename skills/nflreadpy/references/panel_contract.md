# Team-Game Panel Contract

Built by `sports_ds.data.nfl.load_team_game_panel`.

- one row per team per completed game
- two rows per `game_id`
- labels: `won`, `point_diff`
- home flag: `is_home`
- overall win rate ≈ 0.5 by construction
- home advantage: filter `is_home==1`
