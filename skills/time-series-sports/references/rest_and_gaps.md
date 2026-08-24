# Rest and Gaps

## Rest days
```text
sort team, gameday
rest_days = gameday.diff().days
```
First game NA; offseason gaps are not normal short-week rest.

## Byes
Model rest explicitly; do not impute 0.

## Missing games
Do not forward-fill outcomes across unplayed games.
