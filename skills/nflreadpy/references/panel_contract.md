# Team-Game Panel Contract

Build this from a user-owned nflreadpy schedule snapshot and preserve the source rows.

- one row per team per completed game
- two rows per `game_id`
- explicit preserved `game_type`; filter the requested season type before derivation
- labels: `won`, `point_diff`
- tie flag: `tied` (because `won` is 0 for both teams in a tied game)
- home flag: `is_home`
- overall win rate ≈ 0.5 by construction
- home advantage: filter `is_home==1`

Validate pairs field by field: team/opponent swap, home flags oppose,
points-for/against swap, margins negate, season and game type agree, tie flags
agree, and non-tied `won` values sum to one.
