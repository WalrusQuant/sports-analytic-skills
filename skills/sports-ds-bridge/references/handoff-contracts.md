# Portable handoff contracts

These are bridge defaults. The downstream skill remains the source of truth for
its exact input contract.

## Team-game panel

One row per team per game.

Required core fields:

| Field | Meaning |
|---|---|
| `season` | season identifier |
| `game_id` | stable game identifier |
| `gameday` | game date or timestamp |
| `team` | focal team identifier |
| `opponent` | opposing team identifier |
| `is_home` | 1 for home, 0 for away |
| `points_for` | focal-team score |
| `points_against` | opponent score |
| `point_diff` | `points_for - points_against` |
| `won` | binary outcome from the focal team's view |

Include `week` or another within-season ordering field when available. A doubled
team-game panel should contain exactly two complementary rows per `game_id`.

## Prediction table

One row per evaluated decision.

Required fields:

- stable observation keys;
- `y_true`;
- `y_pred` for numeric outcomes or `p_pred` for probabilities;
- a time/fold field such as `season`;
- any slice columns the user wants to interpret.

Do not rename fields silently. Map them explicitly when exporting.

## Fold-metrics JSON

Prefer a portable object:

```json
{
  "task": "binary classification",
  "validation": "season walk-forward",
  "primary_metric": "log_loss",
  "folds": [
    {"fold": "2024", "model": 0.61, "baseline": 0.66, "n_test": 544}
  ]
}
```

If a toolkit pipeline emits different keys, translate them or provide an
explicit mapping. Never let a reporting skill infer the validation design from
the filename or producer.

Win pipelines write raw keys `test_season`, `logistic_log_loss`, and
`constant_log_loss`. Convert with:

```python
from sports_ds.artifacts import write_win_skill_artifacts

write_win_skill_artifacts(result, "data/skill_artifacts")
```

Or CLI:

```bash
sports-ds nfl-win-pipeline --seasons 2018-2024 --skill-out data/skill_artifacts
```

That directory contains `fold_metrics.json` (this schema) and `predictions.csv`
with `y_true`, `p_pred`, `fold`, `season`, `game_id`, and `team`.

## Elo schedule

One row per remaining matchup, not a doubled team panel.

Required fields:

- `season`
- `game_id` (unique after selecting one row per game)
- `team`
- `opponent`
- `is_home`
- either `win_probability` or enough documented rating fields to calculate it

Toolkit Elo tables are a **doubled** team-game panel with `elo_expected`, not
`win_probability`. Before simulation:

1. keep `is_home == 1` (one row per game);
2. rename `elo_expected` → `win_probability`, or compute it from `elo_diff`.

Validate uniqueness of the game key before simulation.
