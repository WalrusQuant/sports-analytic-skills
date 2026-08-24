# Sports EDA Red Flags

| Symptom | Likely issue | Action |
|---|---|---|
| 33+ NFL teams modern season | rename/relocation abbreviations | normalize IDs |
| overall win rate ≈ 0.5 on team-game | expected double rows | use home rows for HFA |
| empty weeks | incomplete schedule / active season | document incompleteness |
| duplicate game_id+team | broken panel | rebuild |
| one row per game labeled team-game | not expanded | build home+away |
| absurd first-model accuracy | leakage | stop → leakage-audit |
| early-season form all null | window not filled | min_games threshold |
| huge team count jump year-to-year | ID churn | mapping table |
