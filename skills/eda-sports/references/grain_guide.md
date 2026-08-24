# Grain Guide

| Grain | Row means | Typical keys |
|---|---|---|
| game | one contest | game_id |
| team-game | one team in one contest | game_id, team |
| player-game | one player in one contest | game_id, player_id |
| pbp / event | one play/event | game_id, play_id |
| pitch | one pitch | game_pk, pitch_no |

## Traps

- Modeling team-game with metrics that assume one row per game
- Aggregating PBP to game without defining pre/post decision time
- Mixing regular season and playoffs without a flag
