# Shift Patterns

## Expanding prior mean

```text
sort by entity, time
value.shift(1).expanding().mean()
```

## Rolling prior mean

```text
value.shift(1).rolling(W, min_periods=1).mean()
```

## Opponent differential

```text
team_feat - opp_feat
# opp_feat from merge of team features on (game_id, opponent)
```

## Illegal

```text
value.rolling(W).mean()          # includes current
season_mean joined to all weeks  # future weeks pollute early weeks
```
