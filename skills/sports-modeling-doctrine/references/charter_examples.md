# Charter Examples

## NFL pre-game win probability
```text
Question: Pre-game P(team wins)
Grain: team-game
T: kickoff
Target: won
Baselines: constant; home+form logistic
Metric: log-loss
Validation: season walk-forward
```

## NBA margin
```text
Question: Expected pre-game margin
Grain: team-game
T: tipoff
Target: point_diff
Baselines: home advantage mean; rating differential linear
Metric: MAE
Validation: season walk-forward
```

## MLB starter strikeouts
```text
Question: Predict starter K in next start
Grain: player-game
T: first pitch
Target: strikeouts
Baselines: trailing mean K; opponent K-allowed mean
Metric: MAE
Validation: time walk-forward by date
```
