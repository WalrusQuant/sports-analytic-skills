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

## Elo schedule

One row per remaining matchup, not a doubled team panel.

Required fields:

- `season`
- `game_id` (unique after selecting one row per game)
- `team`
- `opponent`
- `is_home`
- either `win_probability` or enough documented rating fields to calculate it

Validate uniqueness of the game key before simulation.
