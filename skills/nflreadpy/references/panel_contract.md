# Team-Game Panel Contract

Build this from a user-owned nflreadpy schedule snapshot and preserve the source rows.

- one row per team per completed game
- two rows per `game_id`
- labels: `won`, `point_diff`
- tie flag: `tied` (because `won` is 0 for both teams in a tied game)
- home flag: `is_home`
- overall win rate ≈ 0.5 by construction
- home advantage: filter `is_home==1`
