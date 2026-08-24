# Evaluating Ratings

## Predictive tests (preferred)
- Convert rating diff → win probability
- Season walk-forward log-loss / Brier vs constant and home baselines

## Ranking tests (secondary)
- Correlation of midseason rating with rest-of-season win%
- Careful with leakage if the rating already used those games

## Always report
- as-of rule
- params
- per-season predictive metrics
