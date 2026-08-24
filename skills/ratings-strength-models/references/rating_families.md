# Rating Families (Sports)

## Elo-like
Sequential updates after each game. Natural as-of history. Good default.

## Offense / defense
Each team has attack and defense parameters. Predict score lines, not only winners.

## Least-squares power ratings
Each week, solve for team strengths from margins to date. Recompute as-of each week.

## Hierarchical
Player or team effects with partial pooling — important when sample sizes differ wildly.

## Common failure modes
- using final rating for earlier games
- ignoring home advantage
- huge K chasing noise
- mixing playoff and regular season without a flag
