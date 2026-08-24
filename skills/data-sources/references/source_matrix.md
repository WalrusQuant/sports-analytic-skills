# Public Sports Source Matrix

| Need | Prefer | Fallback |
|---|---|---|
| NFL PBP / schedules / rosters / weekly | nflverse via `nflreadpy` | SportsDataverse NFL |
| CFB | SportsDataverse CFB | — |
| NBA / WNBA / NCAAB | SportsDataverse | — |
| MLB pitch / Statcast depth | `pybaseball` | SportsDataverse MLB |
| NHL | SportsDataverse NHL | — |
| Soccer events | SportsDataverse soccer; optional StatsBomb later | ToS-careful open event data |

Rules:

- Prefer release loaders over live scrapers
- State grain (game, team-game, player-game, pbp, pitch)
- Snapshot for reproducible offline analysis
- Source choice does not create predictive value by itself
